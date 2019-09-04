# -*- coding: utf-8 -*-
"""Conf for py.test."""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import re

import dotenv
import pytest

import axonius_api_client as axonapi

dotenv.load_dotenv()

AX_URL = os.environ.get("AX_URL", None) or None
AX_KEY = os.environ.get("AX_KEY", None) or None
AX_SECRET = os.environ.get("AX_SECRET", None) or None


def join(opts, switch):
    """Join a string with switch."""
    return "({})".format(" {} ".format(switch).join(opts))


NEEDS_KEY = join(["--key", "$AX_KEY", ".env/AX_KEY"], "OR")
NEEDS_SECRET = join(["--secret", "$AX_SECRET", ".env/AX_SEXRET"], "OR")
NEEDS_URL = join(["--url", "$AX_URL", ".env/AX_URL"], "OR")

NEEDS_KEY_CREDS = join([NEEDS_KEY, NEEDS_SECRET], "AND")


def pytest_addoption(parser):
    """Add API connection options."""
    parser.addoption(
        "--url",
        action="store",
        default=AX_URL,
        required=False,
        help="URL of Axonius API",
    )
    parser.addoption(
        "--key",
        action="store",
        default=AX_KEY,
        required=False,
        help="Username for Axonius API",
    )
    parser.addoption(
        "--secret",
        action="store",
        default=AX_SECRET,
        required=False,
        help="Password for Axonius API",
    )


def pytest_configure(config):
    """Ini file additions."""
    config.addinivalue_line(
        "markers", "needs_key_creds: requires {}".format(NEEDS_KEY_CREDS)
    )
    config.addinivalue_line("markers", "needs_url: requires {}".format(NEEDS_URL))
    config.addinivalue_line(
        "filterwarnings", "ignore::urllib3.exceptions.InsecureRequestWarning"
    )


def pytest_runtest_setup(item):
    """Handle marks."""
    key = item.config.getoption("--key")
    secret = item.config.getoption("--secret")
    url = item.config.getoption("--url")

    needs = []

    has_key_creds = all([key, secret])

    if "needs_url" in item.keywords and not url:
        needs.append(NEEDS_URL)

    if "needs_key_creds" in item.keywords and not has_key_creds:
        needs.append(NEEDS_KEY_CREDS)

    if needs:
        msg = "Need {needs} for this test!"
        msg = msg.format(needs=join(needs, "AND"))
        pytest.skip(msg)


@pytest.fixture(scope="session")
def url(request):
    """Fixture for getting API URL."""
    url = request.config.getoption("--url")
    if url:
        parsed_url = axonapi.ParserUrl(url=url, default_scheme="https")
        url = parsed_url.url
    return url


@pytest.fixture(scope="session")
def creds_key(request):
    """Fixture for getting key/secret creds."""
    return {
        "cls": axonapi.ApiKey,
        "creds": {
            "key": request.config.getoption("--key"),
            "secret": request.config.getoption("--secret"),
        },
    }


@pytest.fixture(scope="session")
def creds(request):
    """Pass."""
    return request.getfixturevalue(request.param)


@pytest.fixture
def log_check():
    """Fixture to check if list of regexes found in pytest logging captures."""
    # wrapper
    def _log_check(caplog, entries):
        """Check if entries match caplog."""
        msgs = [rec.message for rec in caplog.records]
        for entry in entries:
            if not any(re.search(entry, m) for m in msgs):
                error = "Did not find entry in log: {!r}\nAll entries:\n{}"
                error = error.format(entry, "\n".join(msgs))
                raise Exception(error)

    return _log_check
