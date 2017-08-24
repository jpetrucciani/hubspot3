#!/usr/bin/env python
from setuptools import setup

setup(
    name='hubspot3',
    version='3.0.2',
    description=(
        "A python wrapper around HubSpot's APIs, for python 3."
        " Built around hapipy, but heavily modified."
    ),
    long_description=open('README.md').read(),
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
