# -*- coding: utf-8 -*-
"""Conf for py.test."""
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import dotenv

dotenv.load_dotenv()

AX_URL = os.environ.get("AX_URL", None) or None
AX_KEY = os.environ.get("AX_KEY", None) or None
AX_SECRET = os.environ.get("AX_SECRET", None) or None


def pytest_addoption(parser):
    """Add API connection options."""
    parser.addoption(
        "--ax-url",
        action="store",
        default=AX_URL,
        required=not bool(AX_URL),
        help="URL of Axonius API",
    )
    parser.addoption(
        "--ax-key",
        action="store",
        default=AX_KEY,
        required=not bool(AX_KEY),
        help="API key for Axonius API",
    )
    parser.addoption(
        "--ax-secret",
        action="store",
        default=AX_SECRET,
        required=not bool(AX_SECRET),
        help="API secret for Axonius API",
    )


def pytest_configure(config):
    """Ini file additions."""
    config.addinivalue_line(
        "filterwarnings", "error::axonius_api_client.exceptions.AxonWarning"
    )
    config.addinivalue_line(
        "filterwarnings", "ignore::urllib3.exceptions.InsecureRequestWarning"
    )
