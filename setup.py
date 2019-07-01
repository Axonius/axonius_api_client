#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Package setup."""
import os

import codecs

from setuptools import setup
from setuptools import find_packages


HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_PATH = os.path.join(HERE, 'axonius_api_client', 'version.py')


ABOUT = {}
with codecs.open(VERSION_PATH, 'r', 'utf-8') as f:
    x = f.readlines()
    CONTENTS = '\n'.join(a for a in x if not a.startswith('#'))
    # pylint: disable=W0122
    exec(CONTENTS, ABOUT)  # nosec


with codecs.open('README.md', 'r', 'utf-8') as f:
    README = f.read()

setup(
    name=ABOUT['__title__'],
    version=ABOUT['__version__'],
    description=ABOUT['__description__'],
    long_description=README,
    long_description_content_type='text/markdown',
    author=ABOUT['__author__'],
    author_email=ABOUT['__author_email__'],
    url=ABOUT['__url__'],
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    include_package_data=True,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=['requests[security,socks]'],
    keywords=['Axonius', 'Plugin', 'Adapter', 'IT'],
    tests_require=[],
    license=ABOUT['__license__'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)
