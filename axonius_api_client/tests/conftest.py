# -*- coding: utf-8 -*-
"""Conf for py.test."""
import os
import pathlib

import pytest

from .meta import CSV_FILECONTENT_STR, CSV_FILENAME, USER_NAME
from .utils import check_apiobj, check_apiobj_children, check_apiobj_xref, get_auth, get_url

AX_URL = os.environ.get("AX_URL", None) or None
AX_KEY = os.environ.get("AX_KEY", None) or None
AX_SECRET = os.environ.get("AX_SECRET", None) or None
ARTIFACTS = pathlib.Path(__file__).parent.parent.parent / "artifacts"
os.environ.setdefault("AX_LOG_FILE_PATH", str(ARTIFACTS))


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


@pytest.fixture(scope="session")
def api_devices(request):
    """Get a fully loaded Devices API object."""
    from axonius_api_client.api import Adapters, Devices, Wizard, WizardCsv, WizardText, DataScopes
    from axonius_api_client.api.assets import Fields, Labels, SavedQuery

    auth = get_auth(request)

    obj = Devices(auth=auth)
    assert isinstance(obj.fields_default, list)

    check_apiobj(authobj=auth, apiobj=obj)

    check_apiobj_children(
        apiobj=obj,
        labels=Labels,
        saved_query=SavedQuery,
        fields=Fields,
    )

    check_apiobj_xref(apiobj=obj, adapters=Adapters)
    assert isinstance(obj.wizard, Wizard)
    assert isinstance(obj.wizard_text, WizardText)
    assert isinstance(obj.wizard_csv, WizardCsv)
    assert isinstance(obj.data_scopes, DataScopes)
    return obj


@pytest.fixture(scope="session")
def api_users(request):
    """Get a fully loaded Users API object."""
    from axonius_api_client.api import Adapters, Users, Wizard, WizardCsv, WizardText, DataScopes
    from axonius_api_client.api.assets import Fields, Labels, SavedQuery

    auth = get_auth(request)

    obj = Users(auth=auth)

    assert isinstance(obj.fields_default, list)

    check_apiobj(authobj=auth, apiobj=obj)

    check_apiobj_children(
        apiobj=obj,
        labels=Labels,
        saved_query=SavedQuery,
        fields=Fields,
    )

    check_apiobj_xref(apiobj=obj, adapters=Adapters)
    assert isinstance(obj.wizard, Wizard)
    assert isinstance(obj.wizard_text, WizardText)
    assert isinstance(obj.wizard_csv, WizardCsv)
    assert isinstance(obj.data_scopes, DataScopes)

    return obj


@pytest.fixture(scope="session")
def api_enforcements(request):
    """Test utility."""
    from axonius_api_client.api import Enforcements

    auth = get_auth(request)
    obj = Enforcements(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_adapters(request):
    """Test utility."""
    from axonius_api_client.api import Adapters, Cnx

    auth = get_auth(request)
    obj = Adapters(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    check_apiobj_children(apiobj=obj, cnx=Cnx)
    return obj


@pytest.fixture(scope="session")
def api_dashboard(request):
    """Test utility."""
    from axonius_api_client.api import Dashboard

    auth = get_auth(request)
    obj = Dashboard(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_instances(request):
    """Test utility."""
    from axonius_api_client.api import Instances

    auth = get_auth(request)
    obj = Instances(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_system_roles(request):
    """Test utility."""
    from axonius_api_client.api import Instances, SystemRoles

    auth = get_auth(request)
    obj = SystemRoles(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    check_apiobj_xref(apiobj=obj, instances=Instances)

    return obj


@pytest.fixture(scope="session")
def api_data_scopes(request):
    """Test utility."""
    from axonius_api_client.api import Instances, DataScopes, Users, Devices

    auth = get_auth(request)
    obj = DataScopes(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    check_apiobj_xref(apiobj=obj, instances=Instances, users=Users, devices=Devices)

    return obj


@pytest.fixture(scope="session")
def api_system_users(request):
    """Test utility."""
    from axonius_api_client.api import SystemRoles, SystemUsers

    auth = get_auth(request)
    obj = SystemUsers(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    check_apiobj_xref(apiobj=obj, roles=SystemRoles)

    return obj


@pytest.fixture(scope="session")
def api_meta(request):
    """Test utility."""
    from axonius_api_client.api import Meta

    auth = get_auth(request)
    obj = Meta(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_settings_lifecycle(request):
    """Test utility."""
    from axonius_api_client.api import SettingsLifecycle

    auth = get_auth(request)
    obj = SettingsLifecycle(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_settings_global(request):
    """Test utility."""
    from axonius_api_client.api import SettingsGlobal

    auth = get_auth(request)
    obj = SettingsGlobal(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_settings_gui(request):
    """Test utility."""
    from axonius_api_client.api import SettingsGui

    auth = get_auth(request)
    obj = SettingsGui(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_settings_ip(request):
    """Test utility."""
    from axonius_api_client.api import SettingsIdentityProviders

    auth = get_auth(request)
    obj = SettingsIdentityProviders(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_signup(request):
    """Test utility."""
    from axonius_api_client.api import Signup

    obj = Signup(url=get_url(request))
    return obj


@pytest.fixture(scope="session")
def api_remote_support(request):
    """Test utility."""
    from axonius_api_client.api import RemoteSupport

    auth = get_auth(request)
    obj = RemoteSupport(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def api_activity_logs(request):
    """Test utility."""
    from axonius_api_client.api import ActivityLogs

    auth = get_auth(request)
    obj = ActivityLogs(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture(scope="session")
def csv_file_path(api_adapters):
    """Test utility."""
    from axonius_api_client.constants.adapters import CSV_ADAPTER

    data = api_adapters.file_upload(
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
def csv_file_path_broken(api_adapters):
    """Test utility."""
    from axonius_api_client.constants.adapters import CSV_ADAPTER

    data = api_adapters.file_upload(
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
def smtp_setup(api_settings_global):
    """Pass."""

    def setup():
        try:
            api_settings_global.update_section(
                section="email_settings", enabled=True, smtpHost="10.0.2.110", smtpPort=25
            )
        except Exception:
            pass

    def teardown():
        try:
            api_settings_global.update_section(
                section="email_settings", enabled=False, smtpHost=None, smtpPort=None
            )
        except Exception:
            pass

    return setup, teardown


@pytest.fixture(scope="function")
def temp_user(api_system_users):
    """Pass."""
    roles = api_system_users.roles._get()
    users = api_system_users._get()
    for user in users:
        if user.user_name == USER_NAME:
            api_system_users._delete(uuid=user.uuid)

    role_id = roles[0].uuid

    tuser = api_system_users._add(user_name=USER_NAME, role_id=role_id, password=USER_NAME)

    yield tuser

    try:
        api_system_users._delete(uuid=tuser.uuid)
    except Exception:
        pass


@pytest.fixture(scope="session")
def api_openapi(request):
    """Test utility."""
    from axonius_api_client.api import OpenAPISpec

    auth = get_auth(request)
    obj = OpenAPISpec(auth=auth)
    check_apiobj(authobj=auth, apiobj=obj)
    return obj


@pytest.fixture
def datafiles(request):
    """Pass."""

    def get_datafile(filename):
        path = pathlib.Path(__file__).parent / "datafiles" / filename
        if not path.is_file():
            msg = f"datafile {filename!r} not found at path {path}"
            if skip_if_missing:
                pytest.skip(msg)
            else:
                raise Exception(msg)
        return path

    markers = {k.name: k for k in request.node.iter_markers()}
    found = f"found markers {list(markers)}"
    example = 'like @pytest.mark.datafiles("file.txt")'
    if "datafiles" not in markers:
        raise ValueError(f"datafiles marker must exist {example} ({found})")

    marker = markers["datafiles"]
    filenames = marker.args
    kwargs = marker.kwargs

    skip_if_missing = kwargs.get("skip_if_missing", False)
    if not filenames:
        raise ValueError("datafiles marker needs a file to load {example} ({found})")

    paths = [get_datafile(x) for x in filenames]
    return paths
