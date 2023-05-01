# -*- coding: utf-8 -*-
"""Test suite."""
import csv
import functools
import hashlib
import random
import re
import secrets
import string
import sys
import time
import typing as t
from io import StringIO

import pytest
import requests
from cachetools import TTLCache, cached
from click.testing import CliRunner
from flaky import flaky


IS_WINDOWS = sys.platform == "win32"
IS_LINUX = sys.platform == "linux"
IS_MAC = sys.platform == "darwin"
SALT_SIZE = 32  # In Bytes
SOURCE: str = string.ascii_lowercase + string.digits


CACHE: TTLCache = TTLCache(maxsize=1024, ttl=600)


# noinspection PyUnusedLocal
def flaky_filter(err, *args):
    """Pass."""
    if issubclass(err[0], requests.exceptions.ReadTimeout):
        time.sleep(30)
    return True


FLAKY = functools.partial(flaky, max_runs=10, rerun_filter=flaky_filter)


def get_field_vals(rows, field):
    """Test utility."""
    from axonius_api_client.tools import listify

    values = [x[field] for x in listify(rows) if x.get(field)]
    values = [x for y in values for x in listify(y)]
    return values


def check_assets(rows):
    """Test utility."""
    assert isinstance(rows, list)
    for row in rows:
        check_asset(row)


def check_asset(row):
    """Test utility."""
    assert isinstance(row, dict)
    assert row["internal_axon_id"]


def exists_query(apiobj, fields=None, not_exist=False):
    """Test utility."""
    from axonius_api_client import Wizard

    if not fields:
        return None

    try:
        fields = apiobj.fields.validate(fields=fields, fields_default=False)
    except Exception as exc:
        pytest.skip(f"Fields {fields} not known for {apiobj}: {exc}")

    if not_exist:
        entries = [{"type": "simple", "value": f"! {x} exists"} for x in fields]
    else:
        entries = [{"type": "simple", "value": f"{x} exists"} for x in fields]

    wizard = Wizard(apiobj=apiobj)
    query = wizard.parse(entries=entries)["query"]
    return query


def get_schema(apiobj, field, key=None, adapter=None):
    """Test utility."""
    from axonius_api_client.constants.fields import AGG_ADAPTER_NAME
    from axonius_api_client.exceptions import NotFoundError

    adapter = adapter or AGG_ADAPTER_NAME

    schemas = get_schemas(apiobj=apiobj, adapter=adapter)
    try:
        schema = apiobj.fields.get_field_schema(
            value=field,
            schemas=schemas,
        )
    except NotFoundError as exc:
        pytest.skip(f"field {field} not found, exc:\n{exc}")
    else:
        return schema[key] if key else schema


def random_string(length: int = 32, source: str = SOURCE):
    """Test utility."""
    result_str = "".join(random.choice(source) for _ in range(length))
    return result_str


def random_strs(num: int = 1, length: int = 32, source: str = SOURCE) -> t.List[str]:
    """Test utility."""
    return [random_string(length=length, source=source) for _ in range(num)]


def random_string_salt(length: int, source: str = SOURCE) -> str:
    """Generate a random string with length, seed it time in milliseconds and salt."""
    result = ""
    for i in range(0, length):
        result += secrets.choice(source)
    salt = secrets.token_bytes(SALT_SIZE)
    return hashlib.sha256(f"{salt}{result}".encode("utf-16")).hexdigest()


def get_rows_exist(apiobj, fields=None, max_rows=1, not_exist=False, **kwargs):
    """Test utility."""
    from axonius_api_client.exceptions import NotFoundError

    query = exists_query(apiobj=apiobj, fields=fields, not_exist=not_exist)
    try:
        rows = apiobj.get(fields=fields, max_rows=max_rows, query=query, **kwargs)
    except NotFoundError as exc:
        pytest.skip(f"fields {fields} not found, exc:\n{exc}")
    else:
        if not rows:
            pytest.skip(f"No {apiobj} assets with fields {fields}")
        return rows[0] if max_rows == 1 else rows


@cached(cache=CACHE)
def get_schemas(apiobj, adapter=None):
    """Test utility."""
    from axonius_api_client.constants.fields import AGG_ADAPTER_NAME

    adapter = adapter or AGG_ADAPTER_NAME

    return apiobj.fields.get()[adapter]


def log_check(caplog, entries, exists=True):
    """Check if entries match caplog."""
    msgs = [rec.message for rec in caplog.records]
    for entry in entries:
        if exists:
            if not any(re.search(entry, m) for m in msgs):
                error = "Did not find entry in log: {!r}\nAll entries:\n{}"
                error = error.format(entry, "\n".join(msgs))
                raise Exception(error)
        else:
            if any(re.search(entry, m) for m in msgs):
                error = "Found unexpected entry in log: {!r}\nAll entries:\n{}"
                error = error.format(entry, "\n".join(msgs))
                raise Exception(error)


def get_cnx_existing(apiobj, name=None, reqkeys=None):
    """Test utility."""
    found = get_cnx(apiobj=apiobj, name=name, reqkeys=reqkeys)

    if not found:
        pytest.skip("No connections found for any adapter!")
    return found


def get_cnx_working(apiobj, name=None, reqkeys=None):
    """Test utility."""
    problems = [
        "symantec_altiris",  # AX-7165
        "alibaba",  # noticed in 4.3 that test fails but connection still green
        "webscan",
    ]
    found = get_cnx(
        apiobj=apiobj, cntkey="success_count", name=name, reqkeys=reqkeys, problems=problems
    )

    if not found:
        pytest.skip("No working connections found for any adapter!")
    return found


def get_cnx_broken(apiobj, name=None, reqkeys=None):
    """Test utility."""
    found = get_cnx(apiobj=apiobj, cntkey="error_count", name=name, reqkeys=reqkeys)

    if not found:
        pytest.skip("No broken connections found for any adapter!")
    return found


# noinspection PyProtectedMember
def get_cnx(apiobj, cntkey="total_count", name=None, reqkeys=None, problems=None):
    """Pass."""
    adapters = apiobj._get(get_clients=False)
    reqkeys = reqkeys or []
    problems = problems or []

    for adapter in adapters:
        for adapter_node in adapter.adapter_nodes:
            if name and adapter_node.adapter_name != name:
                continue

            if cntkey and not getattr(adapter_node.clients_count, cntkey):
                continue

            if problems and adapter_node.adapter_name in problems:
                continue

            cnxs = apiobj.cnx._get(adapter_name=adapter_node.adapter_name_raw)

            has_req = all([x in cnxs.schema_cnx for x in reqkeys])
            if not has_req:
                continue

            for cnx in cnxs.cnxs:
                if cntkey == "total_count":
                    return cnx.to_dict_old()
                if cntkey == "success_count" and cnx.working:
                    return cnx.to_dict_old()
                if cntkey == "error_count" and not cnx.working:
                    return cnx.to_dict_old()
    return None


def get_arg_url(request):
    """Test utility."""
    value = request.config.getoption("--ax-url").rstrip("/")

    if isinstance(value, str):
        value = value.rstrip("/")
    return value


get_url = get_arg_url


def get_key_creds(request):
    """Test utility."""
    key = get_arg_key(request)
    secret = get_arg_secret(request)
    creds = get_arg_credentials(request)
    return {"username": key, "password": secret} if creds else {"keys": key, "secret": secret}


def get_http(request, **kwargs):
    """Test utility."""
    from axonius_api_client.http import Http

    kwargs.setdefault("url", get_url(request))
    kwargs.setdefault("cf_run", get_arg_cf_run(request))
    kwargs.setdefault("cf_error", get_arg_cf_error(request))
    kwargs.setdefault("cf_token", get_arg_cf_token(request))
    kwargs.setdefault("certwarn", False)

    http = Http(**kwargs)
    return http


def get_connect(request, **kwargs):
    """Test utility."""
    from axonius_api_client.connect import Connect

    kwargs.setdefault("url", get_url(request))
    kwargs.setdefault("key", get_arg_key(request))
    kwargs.setdefault("secret", get_arg_secret(request))
    kwargs.setdefault("credentials", get_arg_credentials(request))
    kwargs.setdefault("cf_run", get_arg_cf_run(request))
    kwargs.setdefault("cf_error", get_arg_cf_error(request))
    kwargs.setdefault("cf_token", get_arg_cf_token(request))
    kwargs.setdefault("certwarn", False)

    connect = Connect(**kwargs)
    return connect


def get_arg_key(request):
    """Test utility."""
    return request.config.getoption("--ax-key")


def get_arg_secret(request):
    """Test utility."""
    return request.config.getoption("--ax-secret")


def get_arg_cf_token(request):
    """Test utility."""
    return request.config.getoption("--cf-token")


def get_arg_cf_run(request):
    """Test utility."""
    return request.config.getoption("--cf-run")


def get_arg_cf_error(request):
    """Test utility."""
    return request.config.getoption("--cf-error")


def get_arg_credentials(request):
    """Test utility."""
    value = request.config.getoption("--ax-credentials")
    return value


def get_auth_obj(request):
    """Test utility."""
    from axonius_api_client.auth import AuthApiKey, AuthCredentials

    arg_credentials: bool = get_arg_credentials(request)
    arg_key: str = get_arg_key(request)
    arg_secret: str = get_arg_secret(request)
    http = get_http(request)
    if arg_credentials:
        obj = AuthCredentials(http=http, username=arg_key, password=arg_secret)
    else:
        obj = AuthApiKey(http=http, key=arg_key, secret=arg_secret)
    return obj


def get_auth(request):
    """Test utility."""
    obj = get_auth_obj(request)
    obj.login()
    return obj


def check_apiobj(authobj, apiobj):
    """Test utility."""
    from axonius_api_client import auth
    from axonius_api_client.http import Http

    url = authobj.http.url
    name = authobj.__class__.__name__

    obj_str = str(apiobj)
    obj_repr = repr(apiobj)
    assert name in obj_str
    assert url in obj_str
    assert name in obj_repr
    assert url in obj_repr

    assert isinstance(apiobj.auth, auth.AuthModel)
    assert isinstance(apiobj.http, Http)


def check_apiobj_children(apiobj, **kwargs):
    """Test utility."""
    from axonius_api_client import api, auth
    from axonius_api_client.http import Http

    for k, v in kwargs.items():
        attr = getattr(apiobj, k)
        name = format(attr.__class__.__name__)

        assert isinstance(attr, api.mixins.ChildMixins)
        assert isinstance(attr, v)

        assert isinstance(attr.auth, auth.AuthModel)
        assert isinstance(attr.http, Http)
        assert isinstance(attr.parent, api.mixins.Model)
        assert name in str(attr)
        assert name in repr(attr)


def check_apiobj_xref(apiobj, **kwargs):
    """Test utility."""
    from axonius_api_client import api

    for k, v in kwargs.items():
        attr = getattr(apiobj, k)

        assert isinstance(attr, api.mixins.ModelMixins)
        assert isinstance(attr, v)


def load_clirunner(request, monkeypatch):
    """Test utility."""
    runner = CliRunner(mix_stderr=False)

    url = request.config.getoption("--ax-url")
    key = request.config.getoption("--ax-key")
    secret = request.config.getoption("--ax-secret")

    monkeypatch.setenv("AX_URL", url)
    monkeypatch.setenv("AX_KEY", key)
    monkeypatch.setenv("AX_SECRET", secret)
    return runner


def check_stderr_lines(result):
    """Test utility."""
    stderr = result.stderr.splitlines()

    assert stderr[0].startswith("** WARNING: Unverified HTTPS request!")
    assert stderr[1].startswith("** Connected to "), stderr


class MockError(Exception):
    """Test utility."""


class MockCtx:
    """Test utility."""


# noinspection PyUnusedLocal
def mock_failure(*args, **kwargs):
    """Test utility."""
    raise MockError("badwolf")


def get_mockctx():
    """Test utility."""
    from axonius_api_client.cli.context import Context

    ctx = MockCtx()
    ctx.obj = Context()
    return ctx


def check_csv_cols(content, cols):
    """Test utility."""
    quoting = csv.QUOTE_NONNUMERIC
    fh = StringIO()
    fh.write(content)
    fh.seek(0)
    reader = csv.DictReader(fh, quoting=quoting)
    rows = []
    for row in reader:
        rows.append(row)
        for x in cols:
            assert x in row, "column {!r} not in {}".format(x, list(row))
    return rows
