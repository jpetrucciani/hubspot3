#!/usr/bin/env python
"""
pip setup file
"""
import os
import re
from setuptools import setup


with open("README.rst") as readme:
    LONG_DESCRIPTION = readme.read()


def find_version(*file_paths):
    """
    This pattern was modeled on a method from the Python Packaging User Guide:
        https://packaging.python.org/en/latest/single_source_version.html
    We read instead of importing so we don't get import errors if our code
    imports from dependencies listed in install_requires.
    """
    base_module_file = os.path.join(*file_paths)
    with open(base_module_file) as f:
        base_module_data = f.read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", base_module_data, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open("requirements.txt") as requirements:
    install_requires = requirements.read().split("\n")
    install_requires = [x.strip() for x in install_requires if x.strip()]


setup(
    name="hubspot3",
    version=find_version("hubspot3", "globals.py"),
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
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    zip_safe=False,
)
