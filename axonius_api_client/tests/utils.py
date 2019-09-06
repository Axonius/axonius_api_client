# -*- coding: utf-8 -*-
"""Test suite."""
from __future__ import absolute_import, division, print_function, unicode_literals

import re

import axonius_api_client as axonapi


def log_check(caplog, entries):
    """Check if entries match caplog."""
    msgs = [rec.message for rec in caplog.records]
    for entry in entries:
        if not any(re.search(entry, m) for m in msgs):
            error = "Did not find entry in log: {!r}\nAll entries:\n{}"
            error = error.format(entry, "\n".join(msgs))
            raise Exception(error)


def get_url(request):
    """Pass."""
    return request.config.getoption("--ax-url")


def get_key_creds(request):
    """Pass."""
    key = request.config.getoption("--ax-key")
    secret = request.config.getoption("--ax-secret")
    return {"key": key, "secret": secret}


def get_auth(request):
    """Pass."""
    http = axonapi.Http(url=get_url(request), certwarn=False)

    auth = axonapi.ApiKey(http=http, **get_key_creds(request))
    auth.login()
    return auth


def check_apiobj(authobj, apiobj):
    """Pass."""
    url = authobj._http.url
    authclsname = format(authobj.__class__.__name__)

    assert authclsname in format(apiobj)
    assert authclsname in repr(apiobj)
    assert url in format(apiobj)
    assert url in repr(apiobj)

    assert isinstance(apiobj._router, axonapi.api.routers.Router)


def check_apiobj_children(apiobj, **kwargs):
    """Pass."""
    for k, v in kwargs.items():
        attr = getattr(apiobj, k)
        attrclsname = format(attr.__class__.__name__)

        assert isinstance(attr, axonapi.api.mixins.Child)
        assert isinstance(attr, v)
        assert attrclsname in format(attr)
        assert attrclsname in repr(attr)


def check_apiobj_xref(apiobj, **kwargs):
    """Pass."""
    for k, v in kwargs.items():
        attr = getattr(apiobj, k)

        assert isinstance(attr, axonapi.api.mixins.Model)
        assert isinstance(attr, v)
