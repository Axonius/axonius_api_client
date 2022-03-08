#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Package setup."""
import codecs
import os
from typing import List

from setuptools import find_packages, setup

PROJECT = "axonius_api_client"
SHELL_CMD = "axonshell"
HERE = os.path.abspath(os.path.dirname(__file__))
PATH_VERSION = os.path.join(HERE, PROJECT, "version.py")
PATH_README = os.path.join(HERE, "README.md")
PATH_REQ = os.path.join(HERE, "requirements.txt")


def read(path: str, clean: bool = True) -> List[str]:
    """Read a file."""
    with codecs.open(path, "r", "utf-8") as fh:
        contents = fh.readlines()

    if clean:
        contents = [x for x in contents if not x.startswith("#") and x.strip()]
    return contents


ABOUT = {}
CONTENTS = "\n".join(read(path=PATH_VERSION))
exec(CONTENTS, ABOUT)
README = read(path=PATH_README, clean=False)
INSTALL_REQUIRES = [x.strip() for x in read(path=PATH_REQ)]

setup(
    name=ABOUT["__title__"],
    version=ABOUT["__version__"],
    description=ABOUT["__description__"],
    long_description=README,
    long_description_content_type="text/markdown",
    author=ABOUT["__author__"],
    author_email=ABOUT["__author_email__"],
    url=ABOUT["__url__"],
    packages=find_packages(),
    package_data={"": ["LICENSE"]},
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=INSTALL_REQUIRES,
    keywords=["Axonius", "API Library"],
    tests_require=["pytest", "pytest-cov", "pytest-httpbin", "coverage"],
    license=ABOUT["__license__"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={"console_scripts": [f"{SHELL_CMD}={PROJECT}.cli:cli"]},
)
