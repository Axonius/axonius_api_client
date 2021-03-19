# -*- coding: utf-8 -*-
"""Conf for py.test."""
import os

import pytest
from axonius_api_client.connect import Connect
from axonius_api_client.constants.adapters import CSV_ADAPTER

from .meta import CSV_FILECONTENT_STR, CSV_FILENAME, USER_NAME
from .utils import get_key_creds, get_url

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
    config.addinivalue_line("filterwarnings", "error::axonius_api_client.exceptions.AxonWarning")
    config.addinivalue_line("filterwarnings", "ignore::urllib3.exceptions.InsecureRequestWarning")


@pytest.fixture(scope="session")
def api_client(request):
    """Pass."""
    url = get_url(request)
    creds = get_key_creds(request)
    connect_args = {}
    connect_args["url"] = url
    connect_args["certwarn"] = False
    connect_args.update(creds)

    client = Connect(**connect_args)
    client.start()
    return client


@pytest.fixture(scope="session")
def csv_file_path(api_adapters):
    """Test utility."""
    data = api_client.adapters.file_upload(
        name=CSV_ADAPTER,
        field_name="file_path",
        file_name=CSV_FILENAME,
        file_content=CSV_FILECONTENT_STR,
    )
    assert isinstance(data, dict)
    assert data["uuid"]
    assert data["filename"]
    return data


@pytest.fixture(scope="session")
def csv_file_path_broken(api_client):
    """Test utility."""
    data = api_client.adapters.file_upload(
        name=CSV_ADAPTER,
        field_name="file_path",
        file_name="BADWOLF",
        file_content="BADWOLF",
    )
    assert isinstance(data, dict)
    assert data["uuid"]
    assert data["filename"]
    return data


@pytest.fixture()
def smtp_setup(api_client):
    """Pass."""

    def setup():
        try:
            api_client.settings_global.update_section(
                section="email_settings", enabled=True, smtpHost="10.0.2.110", smtpPort=25
            )
        except Exception:
            pass

    def teardown():
        try:
            api_client.settings_global.update_section(
                section="email_settings", enabled=False, smtpHost=None, smtpPort=None
            )
        except Exception:
            pass

    return setup, teardown


@pytest.fixture(scope="function")
def temp_user(api_client):
    """Pass."""
    roles = api_client.system_roles._get()
    users = api_client.system_users._get()
    for user in users:
        if user.user_name == USER_NAME:
            api_client.system_users._delete(uuid=user.uuid)

    role_id = roles[0].uuid

    tuser = api_client.system_users._add(user_name=USER_NAME, role_id=role_id, password=USER_NAME)

    yield tuser

    try:
        api_client.system_users._delete(uuid=tuser.uuid)
    except Exception:
        pass
