# -*- coding: utf-8 -*-
"""Conf for py.test."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import os

import pytest

import axonius_api_client

AX_URL = os.environ.get("AX_URL", None) or None
AX_USERNAME = os.environ.get("AX_USERNAME", None) or None
AX_PASSWORD = os.environ.get("AX_PASSWORD", None) or None
AX_KEY = os.environ.get("AX_KEY", None) or None
AX_SECRET = os.environ.get("AX_SECRET", None) or None


def join(opts, switch):
    """Join a string with switch."""
    return "({})".format(" {} ".format(switch).join(opts))


NEEDS_USERNAME = join(["--username", "$AX_USERNAME"], "OR")
NEEDS_PASSWORD = join(["--password", "$AX_PASSWORD"], "OR")
NEEDS_KEY = join(["--key", "$AX_KEY"], "OR")
NEEDS_SECRET = join(["--secret", "$AX_SECRET"], "OR")
NEEDS_URL = join(["--url", "$AX_URL"], "OR")

NEEDS_USER_CREDS = join([NEEDS_USERNAME, NEEDS_PASSWORD], "AND")
NEEDS_KEY_CREDS = join([NEEDS_KEY, NEEDS_SECRET], "AND")
NEEDS_ANY_CREDS = join([NEEDS_USER_CREDS, NEEDS_KEY_CREDS], "AND/OR")


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
        "--username",
        action="store",
        default=AX_USERNAME,
        required=False,
        help="Username for Axonius API",
    )
    parser.addoption(
        "--password",
        action="store",
        default=AX_PASSWORD,
        required=False,
        help="Password for Axonius API",
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
        "markers", "needs_user_creds: requires {}".format(NEEDS_USER_CREDS)
    )
    config.addinivalue_line(
        "markers", "needs_key_creds: requires {}".format(NEEDS_KEY_CREDS)
    )
    config.addinivalue_line(
        "markers", "needs_any_creds: requires {}".format(NEEDS_ANY_CREDS)
    )
    config.addinivalue_line("markers", "needs_url: requires {}".format(NEEDS_URL))
    config.addinivalue_line(
        "filterwarnings", "ignore::urllib3.exceptions.InsecureRequestWarning"
    )


def pytest_runtest_setup(item):
    """Handle marks."""
    username = item.config.getoption("--username")
    password = item.config.getoption("--password")
    key = item.config.getoption("--key")
    secret = item.config.getoption("--secret")
    url = item.config.getoption("--url")

    needs = []

    has_user_creds = all([username, password])
    has_key_creds = all([key, secret])
    has_any_creds = any([has_user_creds, has_key_creds])

    if "needs_url" in item.keywords and not url:
        needs.append(NEEDS_URL)

    if "needs_user_creds" in item.keywords and not has_user_creds:
        needs.append(NEEDS_USER_CREDS)

    if "needs_key_creds" in item.keywords and not has_key_creds:
        needs.append(NEEDS_KEY_CREDS)

    if "needs_any_creds" in item.keywords and not has_any_creds:
        needs.append(NEEDS_ANY_CREDS)

    if needs:
        msg = "Need {needs} for this test!"
        msg = msg.format(needs=join(needs, "AND"))
        pytest.skip(msg)


@pytest.fixture(scope="session")
def api_url(request):
    """Fixture for getting API URL."""
    url = request.config.getoption("--url")
    if url:
        parsed_url = axonius_api_client.http.urlparser.UrlParser(
            url=url, default_scheme="https"
        )
        url = parsed_url.url
    return url


@pytest.fixture(scope="session")
def creds_user(request):
    """Fixture for getting username/password creds."""
    return {
        "cls": axonius_api_client.auth.AuthUser,
        "username": request.config.getoption("--username"),
        "password": request.config.getoption("--password"),
    }


@pytest.fixture(scope="session")
def creds_key(request):
    """Fixture for getting key/secret creds."""
    return {
        "cls": axonius_api_client.auth.AuthKey,
        "key": request.config.getoption("--key"),
        "secret": request.config.getoption("--secret"),
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
