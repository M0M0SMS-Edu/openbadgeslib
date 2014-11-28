#!/usr/bin/env python3
#description     : Library for dealing with signing of badges
#author          : Luis G.F
#date            : 20141125
#version         : 0.1 

import hashlib
import os
import sys
import time

from ecdsa import SigningKey, VerifyingKey, NIST256p, BadSignatureError
from urllib import request
from urllib.error import HTTPError, URLError
from urllib.request import HTTPSHandler
from urllib.parse import urlparse
from ssl import SSLContext, CERT_NONE, VERIFY_CRL_CHECK_CHAIN, PROTOCOL_TLSv1, SSLError
from xml.dom.minidom import parse, parseString

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "./3dparty/")))
import jws.utils

class GenPrivateKeyError(Exception):
    pass

class GenPublicKeyError(Exception):
    pass

class HashError(Exception):
    pass

class PrivateKeySaveError(Exception):
    pass
    
class PublicKeySaveError(Exception):
    pass
    
class PrivateKeyExists(Exception):
    pass

class PrivateKeyReadError(Exception):
    pass

class PublicKeyReadError(Exception):
    pass
   
class KeyFactory():
    """ ECDSA Factory class """
    
    def __init__(self, conf):
        self.private_key = None
        self.public_key = None
        self.issuer = None
        self.private_key_file = conf.keygen['private_key_path']
        self.public_key_file = conf.keygen['public_key_path']

        self.issuer = conf.issuer['name'].encode('utf-8')

    def has_key(self):
        """ Check if a issuer has a private key generated """
       
        key_path = self.private_key_file + sha1_string(self.issuer) + b'.pem'
        
        if os.path.isfile(key_path):
            raise PrivateKeyExists(key_path)        

    def generate_keypair(self):
        """ Generate a ECDSA keypair """       

        # If the issuer has a key, stop a new key generation
        self.has_key()
        
        # Private key generation
        try:
            self.private_key = SigningKey.generate(curve=NIST256p)            
            self.private_key_file += sha1_string(self.issuer) + b'.pem'
        except:
            raise GenPrivateKeyError()
        
        # Public Key name is the hash of the public key
        try:
            self.public_key = self.private_key.get_verifying_key()
            self.public_key_file += sha1_string(self.get_public_key_pem()) + b'.pem'
        except:
            raise GenPublicKeyError()
        
        # Save the keypair
        self.save_keypair()

    def read_private_key(self, private_key_file): 
        """ Read the private key from files """
        try:
            with open(private_key_file, "rb") as priv:
                self.private_key_file = private_key_file
                self.private_key = SigningKey.from_pem(priv.read())
                priv.close()
                
            return True 
        except:
            raise PrivateKeyReadError('Error reading private key: %s' % self.private_key_file)
            return False
        
    def read_public_key(self, public_key_file): 
        """ Read the public key from files """
        try:
            with open(public_key_file, "rb") as pub:
                self.public_key_file = public_key_file
                self.public_key = VerifyingKey.from_pem(pub.read())
                pub.close()
                
            return True 
        except:
            raise PublicKeyReadError('Error reading public key: %s' % self.public_key_file)
            return False        
                        
    def save_keypair(self):      
        """ Save keypair to file """        
        try:
            with open(self.private_key_file, "wb") as priv:
                priv.write(self.get_private_key_pem())
                priv.close()                
        except:
             raise PrivateKeySaveError()
         
        try:
            with open(self.public_key_file, "wb") as pub:
                pub.write(self.get_public_key_pem())                    
                pub.close()                
        except:
             raise PublicKeySaveError() 

    def get_private_key_pem(self):
        """ Return private key in PEM format """
        return self.private_key.to_pem()
    
    def get_public_key_pem(self):
        """ Return public key in PEM format """
        return self.public_key.to_pem()    

""" Signer Exceptions """

class BadgeNotFound(Exception):
    pass

class FileToSignNotExists(Exception):
    pass

class ErrorSigningFile(Exception):
    pass

class SignerFactory():
    """ JWS Signer Factory """
    
    def __init__(self, conf, badgename, receptor):
        self.conf = conf                              # Access to config.py values                
        self.receptor = receptor                      # Receptor of the badge
        
        try:
            if conf.badges[badgename]:
                self.badge = conf.badges[badgename]
        except KeyError:
            raise BadgeNotFound()
        
    def generate_uid(self):
        """ Generate a UID for a signed badge """
        
        return sha1_string((self.conf.issuer['name'] + self.badge['name']).encode('utf-8') + self.receptor)
    
    def generate_jose_header(self):
        """ Generate JOSE Header """
        
        return { 'alg': 'ES256' }
    
    def generate_jws_payload(self): 
        """ Generate JWS Payload """        
        
        # All this data MUST be a Str string in order to be converted to json properly.
        
        recipient_data = dict (
            identity = (b'sha256$' + sha256_string(self.receptor)).decode('utf-8'),
            type = 'email',
            hashed = 'true'
        )                
        
        verify_data = dict(
            type = 'signed',
            url = self.badge['url_key_verif']
        )                
        
        return dict(
                        uid = self.generate_uid().decode('utf-8'),
                        recipient = recipient_data,
                        image = self.badge['image'],
                        badge = self.badge['json_url'],
                        verify = verify_data,
                        issuedOn = int(time.time())
                     )  
    
    def generate_openbadge_assertion(self):
        """ Generate and Sign and OpenBadge assertion """
        
        import jws
        
        priv_key_file = self.conf.keygen['private_key_path'] + sha1_string(self.conf.issuer['name'].encode('utf-8')) + b'.pem'
        
        header = self.generate_jose_header()
        payload = self.generate_jws_payload()

        try:
            with open(priv_key_file, "rb") as key_file:
                sign_key = SigningKey.from_pem(key_file.read())
                
        except:
            raise PrivateKeyReadError()
        
        signature = jws.sign(header, payload, sign_key)             
        assertion = jws.utils.encode(header) + b'.' + jws.utils.encode(payload) + b'.' + jws.utils.to_base64(signature)                      
        
        # Verify the assertion just after the generation.
        vf = VerifyFactory(self.conf)  
        
        if not vf.verify_signature(assertion):
            return None
        else:
            return assertion
        
    def sign_svg_file(self, file_in, file_out, assertion_data):
        """ Add the Assertion information into the SVG file
        assertion_data MUST by a str. The assertion_data input
        as bytes but MUST be converted tu str """
    
        if not os.path.exists(file_in):
            raise FileToSignNotExists()
    
        try:
            # Parse de SVG XML
            svg_doc = parse(file_in)  
            
            # Adding XML header
            #header = svg_doc.getElementsByTagName("svg")
            #header[0].attributes['xmlns:openbadges'] = 'http://openbadges.org'
        
            # Assertion
            xml_tag = svg_doc.createElement("openbadges:assertion")
            xml_tag.attributes['xmlns:openbadges'] = 'http://openbadges.org'
            svg_doc.childNodes[1].appendChild(xml_tag) 
            xml_tag.attributes['verify']= assertion_data.decode('utf-8')
            svg_doc.childNodes[1].appendChild(xml_tag) 
            
            with open(file_out, "w") as f:
                svg_doc.writexml(f)

        except:
            raise ErrorSigningFile('Error Signing file: ', file_in)
        finally:
            svg_doc.unlink()
            
        return True

class PayloadFormatIncorrect(Exception):
    pass

class AssertionFormatIncorrect(Exception):
    pass

class NotIdentityInAssertion(Exception):
    pass

""" Signature Verification Factory """
class VerifyFactory():
    """ JWS Signature Verifier Factory """
    
    def __init__(self, conf, pub_key=None, key_inline=False):
        self.conf = conf                              # Access to config.py values  
        self.pub_key = pub_key
        self.vk = None                                # VerifyingKey() Object
                
        # If the pubkey is not passed as parameter, i can obtaint it via private_key
        if pub_key and not key_inline:
            # The pubkey is in a file
            try:
                with open(pub_key, "rb") as key_file:
                    self.vk = VerifyingKey.from_pem(key_file.read())
                
            except:
                raise PublicKeyReadError()
            
        elif pub_key and key_inline:
            # The pub key is passed as string
            try:
                self.vk = VerifyingKey.from_pem(pub_key)
            except:
                raise PublicKeyReadError()
            
        else:
            # Pubkey not passed. Using the private key to obtain one.
            try:                
                priv_key_file = self.conf.keygen['private_key_path'] + sha1_string(self.conf.issuer['name'].encode('utf-8')) + b'.pem'
                
                with open(priv_key_file, "rb") as key_file:
                    sign_key = SigningKey.from_pem(key_file.read())
                    self.vk = sign_key.get_verifying_key()
                
            except:
                raise PrivateKeyReadError()
        
    def verify_signature(self, assertion):
        """ Verify the JWS Signature, Return True if the signature block is Good """
        
        try:
            return jws.verify_block(assertion, self.vk)            
        except: 
            return False            
     
    def verify_signature_inverse(self, assertion, receptor):
         """ Check the assertion signature With the Key specified in JWS Paload """
         import json
         # The assertion MUST have a string like head.payload.signature         
         try:
            head_encoded, payload_encoded, signature_encoded = assertion.split(b'.')
         except:
             raise AssertionFormatIncorrect()
         
         # Try to decode the payload
         try:
             payload = jws.utils.decode(payload_encoded)
         except:
             raise AssertionFormatIncorrect('Payload deserialization error')
         
         """ Parse URL to detect that has a correct format and a secure source.
             Warning User otherwise """
            
         u = urlparse(payload['verify']['url'])
         
         if u.scheme != 'https':
             print('[!] Warning! The public key is in a server that\'s lacks TLS support.', payload['verify']['url'])
         else:
             print('[+] The public key is in a server with TLS support. Good!', payload['verify']['url'])
             
         if u.hostname == b'':
             raise AssertionFormatIncorrect('The URL thats point to public key not exists in this assertion')
                                            
         # OK, is time to download the pubkey
         try:
            pub_key_pem = self.download_pubkey(payload['verify']['url'])
         except HTTPError as e:
            print('[!] And error has occurred during PubKey download. HTTP Error: ', e.code, e.reason)
         except URLError as e:
            print('[!] And error has occurred during PubKey download. Reason: ', e.reason)                  
         
         print('[+] This is the assertion content:')
         print(json.dumps(payload, sort_keys=True, indent=4))
         
         # Ok, is time to verify the assertion againts the key downloaded.
         vf = VerifyFactory(self.conf, pub_key_pem, key_inline=True)
         signature_valid = vf.verify_signature(assertion)
         
         if not signature_valid:
            return False
     
         # Ok, the signature is valid, now i check if the badge is emitted for this receptor
         if payload['recipient']['identity'] != '':
            email_hashed = (b'sha256$' + sha256_string(receptor.encode('utf-8'))).decode('utf-8')
            if email_hashed == payload['recipient']['identity']:
                # OK, the signature is valid and the badge is emitted for this user
                return True
            else:
                return False
         else:
             raise NotIdentityInAssertion('The assertion doesn\'t have an identify ')
     
    def download_pubkey(self, url):
        """ This function return the Key in pem format from server """
        
        # SSL Context
        sslctx = SSLContext(PROTOCOL_TLSv1)
        sslctx.verify_mode = CERT_NONE   
        sslctx_handler = HTTPSHandler(context=sslctx, check_hostname=False)
        
        request.install_opener(request.build_opener(sslctx_handler))
        
        with request.urlopen(url, timeout=30) as kd:
            pub_key_pem = kd.read()
        
        return pub_key_pem
    
    def extract_svg_signature(self, file_in):
        """ Extract the signature embeded in a SVG file. """
        
        if not os.path.exists(file_in):
            raise FileToSignNotExists()
        
        try:
            # Parse de SVG XML
            svg_doc = parse(file_in)  
            
            # Extract the assertion
            assertion = svg_doc.getElementsByTagName("openbadges:assertion")
            return assertion[0].attributes['verify'].nodeValue.encode('utf-8')
            
        except:
            raise ErrorParsingFile('Error Parsing SVG file: ', file_in)
        finally:
            svg_doc.unlink()
     
    def is_svg_signature_valid(self, file_in, receptor):
        """ This function return True/False if the signature in the
             file is correct or no """
            
        assertion = self.extract_svg_signature(file_in)
        return self.verify_signature_inverse(assertion, receptor)

     
""" Shared Utils """

def sha1_string(string):
    """ Calculate SHA1 digest of a string """
    try:
        hash = hashlib.new('sha1')
        hash.update(string)
        return hash.hexdigest().encode('utf-8')     # hexdigest() return an 'str' not bytes.
    except:
        raise HashError() 

def sha256_string(string):
    """ Calculate SHA256 digest of a string """
    try:
        hash = hashlib.new('sha256')
        hash.update(string)
        return hash.hexdigest().encode('utf-8')     # hexdigest() return an 'str' not bytes.
    except:
        raise HashError() 
                
if __name__ == '__main__':
    unittest.main()
