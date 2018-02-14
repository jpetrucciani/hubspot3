#!/usr/bin/env python
"""
pip setup file
"""
from hubspot3.globals import (
    __version__
)
from setuptools import (
    setup
)

setup(
    name='hubspot3',
    version=__version__,
    description=(
        'A python wrapper around HubSpot\'s APIs, for python 3.'
        ' Built initially around hapipy, but heavily modified.'
    ),
    author='HubSpot Dev Team, Jacobi Petrucciani',
    author_email='jacobi@mimirhq.com',
    url='https://github.com/jpetrucciani/hubspot3.git',
    download_url='https://github.com/jpetrucciani/hubspot3.git',
    license='LICENSE.txt',
    packages=['hubspot3', 'hubspot3.mixins'],
    install_requires=[
        'nose==1.3.6'
    ],
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose']
)
