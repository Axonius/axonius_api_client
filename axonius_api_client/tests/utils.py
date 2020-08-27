# -*- coding: utf-8 -*-
"""Test suite."""
import csv
import re
import sys
from io import StringIO

import pytest
from click.testing import CliRunner

from axonius_api_client import api, auth
from axonius_api_client.cli.context import Context
from axonius_api_client.http import Http

IS_WINDOWS = sys.platform == "win32"
IS_LINUX = sys.platform == "linux"
IS_MAC = sys.platform == "darwin"


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


#
def get_cnx_existing(apiobj, name=None):
    """Pass."""
    found = None
    adapters = apiobj.get()
    for adapter in adapters:
        if name and adapter["name"] != name:
            continue
        cnxs = adapter["cnx"]
        for cnx in cnxs:
            found = cnxs[0]
            found["schemas"] = adapter["schemas"]["cnx"]
            break

    if not found:
        pytest.skip("No connections found for any adapter!")
    return found


def get_cnx_working(apiobj, name=None, reqkeys=None):
    """Pass."""
    problem_children = [
        "symantec_altiris",  # AX-7165
    ]
    reqkeys = reqkeys or []

    found = None
    adapters = apiobj.get()
    for adapter in adapters:
        if name and adapter["name"] != name:
            continue
        if adapter["name"] in problem_children:
            continue
        schema = adapter["schemas"]["cnx"]

        if reqkeys and not [x for x in reqkeys if x in schema]:
            continue

        cnxs = adapter["cnx"]
        for cnx in cnxs:
            if cnx["working"]:
                found = cnxs[0]
                found["schemas"] = schema
                break

    if not found:
        pytest.skip("No working connections found for any adapter!")
    return found


def get_cnx_broken(apiobj, name=None):
    """Pass."""
    found = None
    adapters = apiobj.get()
    for adapter in adapters:
        if name and adapter["name"] != name:
            continue
        cnxs = adapter["cnx"]
        for cnx in cnxs:
            if not cnx["working"]:
                found = cnxs[0]
                found["schemas"] = adapter["schemas"]["cnx"]
                break

    if not found:
        pytest.skip("No broken connections found for any adapter!")
    return found


def get_url(request):
    """Pass."""
    return request.config.getoption("--ax-url").rstrip("/")


def get_key_creds(request):
    """Pass."""
    key = request.config.getoption("--ax-key")
    secret = request.config.getoption("--ax-secret")
    return {"key": key, "secret": secret}


def get_auth(request):
    """Pass."""
    http = Http(url=get_url(request), certwarn=False)

    obj = auth.ApiKey(http=http, **get_key_creds(request))
    obj.login()
    return obj


def check_apiobj(authobj, apiobj):
    """Pass."""
    url = authobj._http.url
    authclsname = format(authobj.__class__.__name__)
    assert authclsname in format(apiobj)
    assert authclsname in repr(apiobj)
    assert url in format(apiobj)
    assert url in repr(apiobj)

    assert isinstance(apiobj.auth, auth.Model)
    assert isinstance(apiobj.http, Http)
    assert isinstance(apiobj.router, api.routers.Router)


def check_apiobj_children(apiobj, **kwargs):
    """Pass."""
    for k, v in kwargs.items():
        attr = getattr(apiobj, k)
        attrclsname = format(attr.__class__.__name__)

        assert isinstance(attr, api.mixins.ChildMixins)
        assert isinstance(attr, v)

        assert isinstance(attr.auth, auth.Model)
        assert isinstance(attr.http, Http)
        assert isinstance(attr.router, api.routers.Router)
        assert isinstance(attr.parent, api.mixins.Model)
        assert attrclsname in format(attr)
        assert attrclsname in repr(attr)


def check_apiobj_xref(apiobj, **kwargs):
    """Pass."""
    for k, v in kwargs.items():
        attr = getattr(apiobj, k)

        assert isinstance(attr, api.mixins.ModelMixins)
        assert isinstance(attr, v)


def load_clirunner(request, monkeypatch):
    """Pass."""
    runner = CliRunner(mix_stderr=False)

    url = request.config.getoption("--ax-url")
    key = request.config.getoption("--ax-key")
    secret = request.config.getoption("--ax-secret")

    monkeypatch.setenv("AX_URL", url)
    monkeypatch.setenv("AX_KEY", key)
    monkeypatch.setenv("AX_SECRET", secret)
    return runner


def check_stderr_lines(result):
    """Pass."""
    stderr = result.stderr.splitlines()

    assert stderr[0].startswith("** WARNING: Unverified HTTPS request!")
    assert stderr[1].startswith("** Connected to "), stderr


class MockError(Exception):
    """Pass."""


class MockCtx:
    """Pass."""


def mock_failure(*args, **kwargs):
    """Pass."""
    raise MockError("badwolf")


def get_mockctx():
    """Pass."""
    ctx = MockCtx()
    ctx.obj = Context()
    return ctx


def check_csv_cols(content, cols):
    """Pass."""
    QUOTING = csv.QUOTE_NONNUMERIC
    fh = StringIO()
    fh.write(content)
    fh.seek(0)
    reader = csv.DictReader(fh, quoting=QUOTING)
    rows = []
    for row in reader:
        rows.append(row)
        for x in cols:
            assert x in row, "column {!r} not in {}".format(x, list(row))
    return rows
