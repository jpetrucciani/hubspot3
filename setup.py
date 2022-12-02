#!/usr/bin/env python
"""
pip setup file
"""
import os
import re
from setuptools import setup


__library__ = "hubspot3"
__user__ = "https://github.com/jpetrucciani"


with open("README.md") as readme:
    LONG_DESCRIPTION = readme.read()


def find_version(*file_paths):
    """
    This pattern was modeled on a method from the Python Packaging User Guide:
        https://packaging.python.org/en/latest/single_source_version.html
    We read instead of importing so we don't get import errors if our code
    imports from dependencies listed in install_requires.
    """
    base_module_file = os.path.join(*file_paths)
    with open(base_module_file) as module_file:
        base_module_data = module_file.read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", base_module_data, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="hubspot3",
    version=find_version("hubspot3", "globals.py"),
    description=(
        "A python wrapper around HubSpot's APIs, for python 3. "
        "Built initially around hapipy, but heavily modified."
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="HubSpot Dev Team, Jacobi Petrucciani",
    author_email="j@cobi.dev",
    url=f"{__user__}/{__library__}.git",
    download_url=f"{__user__}/{__library__}.git",
    license="LICENSE",
    packages=["hubspot3"],
    install_requires=["typing_extensions; python_version < '3.8'"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    zip_safe=False,
    extras_require={"cli": ["fire==0.4.0"]},
    entry_points={"console_scripts": ["hubspot3=hubspot3.__main__:main"]},
)
