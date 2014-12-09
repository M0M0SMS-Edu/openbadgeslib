#!/usr/bin/env python3

from distutils.core import setup

version = '0.1'

dependencies = [
        'ecdsa',
        'pycrypto',
        ]

setup(
  name = 'openbadgeslib',
  packages = ['openbadgeslib'], # this must be the same as the name above
  version = version,
  description = 'A library to sign and verify OpenBadges',
  long_description = 'A library to sign and verify OpenBadges',
  author = 'Luis González Fernández, Jesús Cea Avión',
  author_email = 'openbadges@luisgf.es, jcea@jcea.es',
  url = 'https://hg.luisgf.es/openbadges/',
  keywords = ['openbadges'], # arbitrary keywords
  classifiers = [
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 3.4',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'Natural Language :: English',
      'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)'
  ],
  license = 'LGPLv3',
  install_requires = dependencies,
  include_package_data = True,
  entry_points = {
          'console_scripts': [
          'openbadges-keygenerator = openbadgeslib.openbadges_keygenerator:main',
	      'openbadges-signer = openbadgeslib.openbadges_signer:main',
	      'openbadges-verifier = openbadgeslib.openbadges_verifier:main'
          ]
  }
)

