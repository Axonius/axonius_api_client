# -*- coding: utf-8 -*-
"""Conf for py.test."""
import os
import pathlib

import pytest

from .meta import CSV_FILECONTENT_STR, CSV_FILENAME, USER_NAME
from .utils import check_apiobj_children, check_apiobj_xref, get_url

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


def load_asset_api(obj):
    """Pass."""
    from axonius_api_client.api import (
        Adapters,
        Wizard,
        WizardCsv,
        WizardText,
        DataScopes,
    )
    from axonius_api_client.api.assets import Fields, Labels, SavedQuery

    assert isinstance(obj.fields_default, list)

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
    obj.ORIGINAL_ROWS = obj.get(max_rows=5)
    obj.IDS = [x["internal_axon_id"] for x in obj.ORIGINAL_ROWS]

    try:
        obj.COMPLEX_ROWS = obj.get(
            max_rows=5, fields=obj.FIELD_COMPLEX, wiz_entries=f"simple {obj.FIELD_COMPLEX} exists"
        )
    except Exception:
        obj.COMPLEX_ROWS = []
    return obj


@pytest.fixture(scope="session")
def api_client(request):
    """Test utility."""
    from axonius_api_client.connect import Connect

    url = request.config.getoption("--ax-url")
    key = request.config.getoption("--ax-key")
    secret = request.config.getoption("--ax-secret")
    if isinstance(url, str):
        url = url.rstrip("/")

    client = Connect(url=url, key=key, secret=secret, certwarn=False, save_history=True)
    client.start()
    return client


@pytest.fixture(scope="session")
def api_openapi(api_client):
    """Test utility."""
    return api_client.openapi


@pytest.fixture(scope="session")
def api_vulnerabilities(api_client):
    """Get a fully loaded Vulnerabilities API object."""
    from axonius_api_client.api import Vulnerabilities

    obj = api_client.vulnerabilities
    assert isinstance(obj, Vulnerabilities)
    return load_asset_api(obj)


@pytest.fixture(scope="session")
def api_devices(api_client):
    """Get a fully loaded Devices API object."""
    from axonius_api_client.api import Devices

    obj = api_client.devices
    assert isinstance(obj, Devices)
    return load_asset_api(obj)


@pytest.fixture(scope="session")
def api_users(api_client):
    """Get a fully loaded Users API object."""
    from axonius_api_client.api import Users

    obj = api_client.users
    assert isinstance(obj, Users)
    return load_asset_api(obj)


@pytest.fixture(scope="session")
def api_enforcements(api_client):
    """Test utility."""
    return api_client.enforcements


@pytest.fixture(scope="session")
def api_adapters(api_client):
    """Test utility."""
    return api_client.adapters


@pytest.fixture(scope="session")
def api_dashboard(api_client):
    """Test utility."""
    return api_client.dashboard


@pytest.fixture(scope="session")
def api_instances(api_client):
    """Test utility."""
    return api_client.instances


@pytest.fixture(scope="session")
def api_system_roles(api_client):
    """Test utility."""
    return api_client.system_roles


@pytest.fixture(scope="session")
def api_data_scopes(api_client):
    """Test utility."""
    return api_client.data_scopes


@pytest.fixture(scope="session")
def api_system_users(api_client):
    """Test utility."""
    return api_client.system_users


@pytest.fixture(scope="session")
def api_meta(api_client):
    """Test utility."""
    return api_client.meta


@pytest.fixture(scope="session")
def api_settings_lifecycle(api_client):
    """Test utility."""
    return api_client.settings_lifecycle


@pytest.fixture(scope="session")
def api_settings_global(api_client):
    """Test utility."""
    return api_client.settings_global


@pytest.fixture(scope="session")
def api_settings_gui(api_client):
    """Test utility."""
    return api_client.settings_gui


@pytest.fixture(scope="session")
def api_settings_ip(api_client):
    """Test utility."""
    return api_client.settings_ip


@pytest.fixture(scope="session")
def api_signup(request):
    """Test utility."""
    from axonius_api_client.api import Signup

    obj = Signup(url=get_url(request))
    return obj


@pytest.fixture(scope="session")
def api_remote_support(api_client):
    """Test utility."""
    return api_client.remote_support


@pytest.fixture(scope="session")
def api_activity_logs(api_client):
    """Test utility."""
    return api_client.activity_logs


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


@pytest.fixture(scope="session")
def core_node(api_instances):
    """Pass."""
    return api_instances.get_core()


@pytest.fixture(scope="session")
def tunnel_feature_check(api_instances):
    """Pass."""
    if not api_instances.has_saas_enabled:
        pytest.skip("saas_enabled=False, can not test for tunnels")


@pytest.fixture(scope="session")
def tunnel_count_check(api_instances, tunnel_feature_check):
    """Pass."""
    tunnels = api_instances.get_tunnels()
    if not tunnels:
        pytest.skip("No tunnels configured, can not test for tunnels")
