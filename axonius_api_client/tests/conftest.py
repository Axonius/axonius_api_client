# -*- coding: utf-8 -*-
"""Conf for py.test."""
import os

import dotenv
import pytest

from axonius_api_client.api import dashboard, enforcements, instances, system
from axonius_api_client.api.adapters import Adapters
from axonius_api_client.api.adapters.cnx import Cnx
from axonius_api_client.api.assets import Devices, Users, fields, labels, saved_query
from axonius_api_client.api.signup import Signup
from axonius_api_client.constants import CSV_ADAPTER, DEFAULT_NODE

from .meta import CSV_FILECONTENT_STR, CSV_FILENAME
from .utils import check_apiobj, check_apiobj_children, check_apiobj_xref, get_auth, get_url

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
    config.addinivalue_line("filterwarnings", "error::axonius_api_client.exceptions.AxonWarning")
    config.addinivalue_line("filterwarnings", "ignore::urllib3.exceptions.InsecureRequestWarning")


@pytest.fixture(scope="session")
def api_devices(request):
    """Get a fully loaded Devices API object."""
    auth = get_auth(request)

    obj = Devices(auth=auth)
    assert isinstance(obj.fields_default, list)

    check_apiobj(authobj=auth, apiobj=obj)

    check_apiobj_children(
        apiobj=obj,
        labels=labels.Labels,
        saved_query=saved_query.SavedQuery,
        fields=fields.Fields,
    )

    check_apiobj_xref(apiobj=obj, adapters=Adapters)
    return obj


@pytest.fixture(scope="session")
def api_users(request):
    """Get a fully loaded Users API object."""
    auth = get_auth(request)

    obj = Users(auth=auth)

    assert isinstance(obj.fields_default, list)

    check_apiobj(authobj=auth, apiobj=obj)

    check_apiobj_children(
        apiobj=obj,
        labels=labels.Labels,
        saved_query=saved_query.SavedQuery,
        fields=fields.Fields,
    )

    check_apiobj_xref(apiobj=obj, adapters=Adapters)
    return obj


@pytest.fixture(scope="session")
def api_enforcements(request):
    """Test utility."""
    auth = get_auth(request)
    obj = enforcements.Enforcements(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_run_action(request):
    """Test utility."""
    auth = get_auth(request)
    obj = enforcements.actions.RunAction(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_adapters(request):
    """Test utility."""
    auth = get_auth(request)
    obj = Adapters(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    check_apiobj_children(apiobj=obj, cnx=Cnx)
    return obj


@pytest.fixture(scope="session")
def api_dashboard(request):
    """Test utility."""
    auth = get_auth(request)
    obj = dashboard.Dashboard(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_instances(request):
    """Test utility."""
    auth = get_auth(request)
    obj = instances.Instances(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_system(request):
    """Test utility."""
    auth = get_auth(request)
    obj = system.System(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    check_apiobj_children(
        apiobj=obj,
        settings_core=system.settings.SettingsCore,
        settings_gui=system.settings.SettingsGui,
        settings_lifecycle=system.settings.SettingsLifecycle,
        meta=system.meta.Meta,
        users=system.users.Users,
        roles=system.roles.Roles,
    )
    return obj


@pytest.fixture(scope="session")
def api_signup(request):
    """Test utility."""
    obj = Signup(url=get_url(request))
    return obj


@pytest.fixture(scope="session")
def csv_file_path(api_adapters):
    """Test utility."""
    data = api_adapters.file_upload(
        name=CSV_ADAPTER,
        node=DEFAULT_NODE,
        field_name="file_path",
        file_name=CSV_FILENAME,
        file_content=CSV_FILECONTENT_STR,
    )
    assert isinstance(data, dict)
    assert data["uuid"]
    assert data["filename"]
    return data


@pytest.fixture(scope="session")
def csv_file_path_broken(api_adapters):
    """Test utility."""
    data = api_adapters.file_upload(
        name=CSV_ADAPTER,
        node=DEFAULT_NODE,
        field_name="file_path",
        file_name="BADWOLF",
        file_content="BADWOLF",
    )
    assert isinstance(data, dict)
    assert data["uuid"]
    assert data["filename"]
    return data
