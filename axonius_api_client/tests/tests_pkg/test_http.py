# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.http."""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import sys

import pytest
import requests

import axonius_api_client as axonapi
from axonius_api_client import exceptions

from .. import utils

InsecureRequestWarning = requests.urllib3.exceptions.InsecureRequestWarning


class TestParserUrl(object):
    """Test axonapi.http.ParserUrl."""

    def test_schemehostport443(self):
        """Test a proper URL gets parsed the same."""
        u = axonapi.http.ParserUrl("https://host:443/blah")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"
        assert u.parsed.path == "/blah"
        assert u.url_full == "https://host:443/blah"
        assert u.url == "https://host:443"

    def test_str_repr(self):
        """Test str/repr has URL path."""
        u = axonapi.http.ParserUrl("https://host:443/blah")
        assert u.parsed.path in format(u)
        assert u.parsed.path in repr(u)

    def test_schemehost_noport443(self):
        """Test port gets added for https scheme."""
        u = axonapi.http.ParserUrl("https://host")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_host_noschemeport(self):
        """Test exc when no port or scheme in URL."""
        exc = exceptions.HttpError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            axonapi.http.ParserUrl("host", default_scheme="")

    def test_unknownschemehost_noport(self):
        """Test exc when no port and non http/https scheme."""
        exc = exceptions.HttpError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            axonapi.http.ParserUrl("httpx://host")

    def test_hostport443_withslash(self):
        """Test scheme added with port 443 and no scheme in URL."""
        u = axonapi.http.ParserUrl("host:443/")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_hostport443_noscheme(self):
        """Test scheme added with port 443 and no scheme in URL."""
        u = axonapi.http.ParserUrl("host:443", default_scheme="")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_hostport80_noscheme(self):
        """Test scheme added with port 80 and no scheme in URL."""
        u = axonapi.http.ParserUrl("host:80", default_scheme="")
        assert u.hostname == "host"
        assert u.port == 80
        assert u.scheme == "http"

    def test_schemehost_noport80(self):
        """Test port added with no port and http scheme in URL."""
        u = axonapi.http.ParserUrl("http://host")
        assert u.hostname == "host"
        assert u.port == 80
        assert u.scheme == "http"


class TestHttp(object):
    """Test axonapi.http.Http."""

    def test_str_repr(self, request):
        """Test str/repr has URL."""
        ax_url = utils.get_url(request)

        http = axonapi.Http(url=ax_url)

        assert ax_url in format(http)
        assert ax_url in repr(http)

    def test_parsed_url(self, request):
        """Test url=ParserUrl() works."""
        ax_url = utils.get_url(request)

        parsed_url = axonapi.http.ParserUrl(url=ax_url, default_scheme="https")

        http = axonapi.Http(url=parsed_url)

        assert ax_url in format(http)
        assert ax_url in repr(http)

    def test_user_agent(self, request):
        """Test user_agent has version in it."""
        ax_url = utils.get_url(request)

        http = axonapi.Http(url=ax_url)
        assert axonapi.version.__version__ in http.user_agent

    def test_certwarn_true(self, request, httpbin_secure):
        """Test quiet_urllib=False shows warning from urllib3."""
        url = httpbin_secure.url
        http = axonapi.Http(url=url, certwarn=True, save_history=True)

        with pytest.warns(InsecureRequestWarning):
            http()

    def test_certwarn_false(self, request, httpbin_secure):
        """Test quiet_urllib=False shows warning from urllib3."""
        url = httpbin_secure.url
        http = axonapi.Http(url=url, certwarn=False)

        http()

    @pytest.mark.skipif(
        sys.version_info < (3, 6), reason="requires python3.6 or higher"
    )
    def test_verify_ca_bundle(self, request, httpbin_secure, httpbin_ca_bundle):
        """Test quiet_urllib=False no warning from urllib3 when using ca bundle."""
        url = httpbin_secure.url
        http = axonapi.Http(url=url, certwarn=False)
        response = http()
        assert response.status_code == 200

    def test_save_last_true(self, request):
        """Test last req/resp with save_last=True."""
        ax_url = utils.get_url(request)

        http = axonapi.Http(url=ax_url, save_last=True, certwarn=False)
        response = http()
        assert response == http._LAST_RESPONSE
        assert response.request == http._LAST_REQUEST

    def test_save_last_false(self, request):
        """Test last req/resp with save_last=False."""
        ax_url = utils.get_url(request)

        http = axonapi.Http(url=ax_url, save_last=False, certwarn=False)

        http()

        assert not http._LAST_RESPONSE
        assert not http._LAST_REQUEST

    def test_save_history(self, request):
        """Test last resp added to history with save_history=True."""
        ax_url = utils.get_url(request)

        http = axonapi.Http(url=ax_url, save_history=True, certwarn=False)

        response = http()

        assert response in http._HISTORY

    def test_log_req_attrs_true(self, request, caplog):
        """Test verbose logging of request attrs when log_request_attrs=True."""
        caplog.set_level(logging.DEBUG)

        ax_url = utils.get_url(request)

        http = axonapi.Http(
            url=ax_url, log_request_attrs=True, certwarn=False, log_level="debug"
        )

        http()

        assert len(caplog.records) == 1

        entries = ["request.*{}.*headers".format(http.url)]
        utils.log_check(caplog, entries)

    def test_log_req_attrs_false(self, request, caplog):
        """Test brief logging of request attrs when log_request_attrs=False."""
        caplog.set_level(logging.DEBUG)

        ax_url = utils.get_url(request)

        http = axonapi.Http(
            url=ax_url, log_request_attrs=False, certwarn=False, log_level="debug"
        )

        http()

        assert len(caplog.records) == 1

        entries = ["request.*{}".format(http.url)]
        utils.log_check(caplog, entries)

    def test_log_req_attrs_none(self, request, caplog):
        """Test no logging of request attrs when log_request_attrs=None."""
        caplog.set_level(logging.DEBUG)

        ax_url = utils.get_url(request)

        http = axonapi.Http(
            url=ax_url, log_request_attrs=None, certwarn=False, log_level="debug"
        )

        http()

        assert not caplog.records

    def test_log_resp_attrs_true(self, request, caplog):
        """Test verbose logging of response attrs when log_response_attrs=True."""
        caplog.set_level(logging.DEBUG)

        ax_url = utils.get_url(request)

        http = axonapi.Http(
            url=ax_url, log_response_attrs=True, certwarn=False, log_level="debug"
        )

        http()

        assert len(caplog.records) == 1

        entries = ["response.*{}.*headers".format(http.url)]
        utils.log_check(caplog, entries)

    def test_log_resp_attrs_false(self, request, caplog):
        """Test brief logging of response attrs when log_response_attrs=False."""
        caplog.set_level(logging.DEBUG)

        ax_url = utils.get_url(request)

        http = axonapi.Http(
            url=ax_url, log_response_attrs=False, certwarn=False, log_level="debug"
        )
        http()

        assert len(caplog.records) == 1

        entries = ["response.*{}".format(http.url)]
        utils.log_check(caplog, entries)

    def test_log_response_attrs_none(self, request, caplog):
        """Test no logging of response attrs when log_response_attrs=None."""
        caplog.set_level(logging.DEBUG)

        ax_url = utils.get_url(request)

        http = axonapi.Http(
            url=ax_url, log_response_attrs=None, certwarn=False, log_level="debug"
        )

        http()

        assert not caplog.records

    def test_log_resp_body_true(self, request, caplog):
        """Test logging of response body when log_response_body=True."""
        caplog.set_level(logging.DEBUG)

        ax_url = utils.get_url(request)

        http = axonapi.Http(
            url=ax_url, log_response_body=True, certwarn=False, log_level="debug"
        )

        http()

        assert len(caplog.records) == 1

        entries = ["response body:.*"]
        utils.log_check(caplog, entries)

    def test_log_resp_body_false(self, request, caplog):
        """Test no logging of response body when log_response_body=False."""
        caplog.set_level(logging.DEBUG)

        ax_url = utils.get_url(request)

        http = axonapi.Http(
            url=ax_url, log_response_body=False, certwarn=False, log_level="debug"
        )

        http()

        assert not caplog.records

    def test_log_req_body_true(self, request, caplog):
        """Test logging of request body when log_request_body=True."""
        caplog.set_level(logging.DEBUG)

        ax_url = utils.get_url(request)

        http = axonapi.Http(
            url=ax_url, log_request_body=True, certwarn=False, log_level="debug"
        )

        http()

        assert len(caplog.records) == 1

        entries = ["request body:.*"]
        utils.log_check(caplog, entries)

    def test_log_req_body_false(self, request, caplog):
        """Test no logging of request body when log_request_body=False."""
        caplog.set_level(logging.DEBUG)

        ax_url = utils.get_url(request)

        http = axonapi.Http(
            url=ax_url, log_request_body=False, certwarn=False, log_level="debug"
        )

        http()

        assert not caplog.records
