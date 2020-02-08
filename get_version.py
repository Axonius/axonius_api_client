#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Package setup."""
import codecs
import os

PROJECT = "axonius_api_client"
HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_PATH = os.path.join(HERE, PROJECT, "version.py")


ABOUT = {}
with codecs.open(VERSION_PATH, "r", "utf-8") as fh:
    CONTENTS = "\n".join(a for a in fh.readlines() if not a.startswith("#"))
    exec(CONTENTS, ABOUT)

print(ABOUT["__version__"], end="")
