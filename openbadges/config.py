#!/usr/bin/env python3

""" 
    Please, don't enable this if you are not completly sure 
    that your are doing.
    
    Setting PLEASE_ENABLE_ECC to True makes the program able
    to use Elliptic Curve cryptography rather that RSA.
    
    JWS draft are not clear with ECC, don't use 
    in production systems, use at your own risk!
"""
PLEASE_ENABLE_ECC = True
    
""" Log signed badges in this file """
log_ecc = '/tmp/openbadges-ecc_sign.log'
log_rsa = '/tmp/openbadges-rsa_sign.log'

""" Configuration of ECC Keys """
ecc_keypair = dict(   
                    crypto    = 'ECC' if PLEASE_ENABLE_ECC else 'RSA',
                    curve     = 'NIST256p',
                    hash_algo = 'SHA256',
                    private = './private/test_sign_ecc.pem',
                    public  = './public/test_verify_ecc.pem'
                )

""" Configuration of RSA Keys """
rsa_keypair = dict(   
                    crypto    = 'RSA',
                    size      = 2048,
                    hash_algo = 'SHA256',
                    private = './private/test_sign_rsa.pem',
                    public  = './public/test_verify_rsa.pem'
                )

""" Issuer Configuration """
issuer_luisgf = dict(
    name = 'Luis G.F Badge Issuer',
    image = 'https://openbadges.luisgf.es/issuer/logo.png',
    url = 'https://www.luisgf.es',
    email = 'openbadges@luisgf.es',
    revocationList = 'https://openbadges.luisgf.es/issuer/revocation.json'
 )

""" Badge Entry """
badge_testrsa = dict(
                name = 'Badge RSA',
                description = 'Test de Badge firmado con clave RSA',
                image = 'https://openbadges.luisgf.es/issuer/badges/badge.svg',
                criteria = 'https://openbadges.luisgf.es/issuer/criteria.html',
                issuer = 'https://openbadges.luisgf.es/issuer/organization.json',
                json_url = 'https://openbadges.luisgf.es/issuer/badge-luisgf.json',
                evidence = 'https://openbadges.luisgf.es/evidence.html',
                url_key_verif = 'https://openbadges.luisgf.es/issuer/pubkeys/test_verify_rsa.pem',
                local_badge_path = '../images/badge.svg'
            )
badge_testecc = dict(
                name = 'Badge ECC',
                description = 'Test de Badge firmado con clave ECC',
                image = 'https://openbadges.luisgf.es/issuer/badges/badge.svg',
                criteria = 'https://openbadges.luisgf.es/issuer/criteria.html',
                issuer = 'https://openbadges.luisgf.es/issuer/organization.json',
                json_url = 'https://openbadges.luisgf.es/issuer/badge-luisgf.json',
                evidence = 'https://openbadges.luisgf.es/evidence.html',
                url_key_verif = 'https://openbadges.luisgf.es/issuer/pubkeys/test_verify_ecc.pem',
                local_badge_path = '../images/badge.svg'
            )


""" Profile Composition. Here you can configure your settings per profile """
profiles = {
        'ECC_PROFILE': { 'issuer':issuer_luisgf, 'badges':[badge_testecc], 'keys':ecc_keypair, 'log':log_ecc },
        'RSA_PROFILE': { 'issuer':issuer_luisgf, 'badges':[badge_testrsa], 'keys':rsa_keypair, 'log':log_rsa }
}


