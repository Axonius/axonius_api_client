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


@pytest.fixture(scope="session")
def api_url(request):
    """Fixture for getting user/name creds."""
    url = request.config.getoption("--url")
    if not url:
        msg = "Need --url or $AX_URL set for test!"
        pytest.skip(msg)
    parsed_url = axonius_api_client.tools.UrlParser(url=url, default_scheme="https")
    return parsed_url.url


@pytest.fixture(scope="session")
def creds_user(request):
    """Fixture for getting username/password creds."""
    username = request.config.getoption("--username")
    password = request.config.getoption("--password")

    if not username:
        msg = "Need --username or $AX_USERNAME for test!"
        pytest.skip(msg)

    if not password:
        msg = "Need --password or $AX_PASSWORD for test!"
        pytest.skip(msg)

    return {"username": username, "password": password}


@pytest.fixture(scope="session")
def creds_key(request):
    """Fixture for getting key/secret creds."""
    key = request.config.getoption("--key")
    secret = request.config.getoption("--secret")

    if not key:
        msg = "Need --key or $AX_KEY for test!"
        pytest.skip(msg)

    if not secret:
        msg = "Need --secret or $AX_SECRET for test!"
        pytest.skip(msg)

    return {"key": key, "secret": secret}


@pytest.fixture(scope="session")
def auth_objs(api_url, request):
    """Fixture for getting multiple auth methods depending on what is supplied."""
    key = request.config.getoption("--key")
    secret = request.config.getoption("--secret")
    username = request.config.getoption("--username")
    password = request.config.getoption("--password")

    http_client = axonius_api_client.http.HttpClient(url=api_url)

    objs = []

    if username and password:
        obj = axonius_api_client.auth.AuthUser(
            http_client=http_client, username=username, password=password
        )
        objs.append(obj)

    if key and secret:
        obj = axonius_api_client.auth.AuthKey(
            http_client=http_client, key=key, secret=secret
        )
        objs.append(obj)

    if not objs:
        msg = (
            "Need ((--username OR $AX_USERNAME) AND (--password OR $AX_PASSWORD))"
            " AND/OR ((--key OR $AX_KEY) AND (--secret OR $AX_SECRET)) for test!"
        )
        pytest.skip(msg)

    return objs


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
