#!/usr/bin/env python
"""
pip setup file
"""
from hubspot3.globals import __version__
from setuptools import setup


with open("README.rst") as readme:
    LONG_DESCRIPTION = readme.read()


setup(
    name="hubspot3",
    version=__version__,
    description=(
        "A python wrapper around HubSpot's APIs, for python 3. "
        "Built initially around hapipy, but heavily modified."
    ),
    long_description=LONG_DESCRIPTION,
    author="HubSpot Dev Team, Jacobi Petrucciani",
    author_email="jacobi@mimirhq.com",
    url="https://github.com/jpetrucciani/hubspot3.git",
    download_url="https://github.com/jpetrucciani/hubspot3.git",
    license="LICENSE",
    packages=["hubspot3"],
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    zip_safe=False,
)
