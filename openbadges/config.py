#!/usr/bin/env python3

""" 
    Please, don't enable this if you are not completly sure 
    that your are doing.
    Enabling this makes the program use
    Elliptic Curve cryptography rather that RSA.
    
    JWS draft are not clear with ECC, don't use 
    in production systems.
"""
PLEASE_ENABLE_ECC = True
LOG_FILE = '/tmp/opnecbadges.log'

""" Issuer Configuration """
issuer = dict(
    name = 'Luis G.F Badge Issuer',
    image = 'https://openbadges.luisgf.es/issuer/logo.png',
    url = 'https://www.luisgf.es',
    email = 'openbadges@luisgf.es',
    revocationList = 'https://openbadges.luisgf.es/issuer/revocation.json'
 )

""" Badge Catalog, You can add more creating new dict() entrys at end """
badges = {
    'BADGETEST': dict(
                name = 'Badge Test',
                description = 'A badge test example',
                image = 'https://openbadges.luisgf.es/issuer/badges/badge.svg',
                criteria = 'https://openbadges.luisgf.es/issuer/criteria.html',
                issuer = 'https://openbadges.luisgf.es/issuer/organization.json',
                json_url = 'https://openbadges.luisgf.es/issuer/badge-luisgf.json',
                evidence = '',
                url_key_verif = 'https://openbadges.luisgf.es/issuer/pubkeys/verify.pem',
                local_badge_path = '../images/badge.svg'
            )
}

""" KeyGenerator Configuration """
keygen = dict(   
    private_key_path = './private/',
    public_key_path = './public/',
    url_verif = 'https://openbadges.luisgf.es'
)

