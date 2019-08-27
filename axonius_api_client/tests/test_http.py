# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.http."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import sys

import pytest
import requests

import axonius_api_client as axonapi


class TestParserUrl(object):
    """Test axonapi.ParserUrl."""

    def test_schemehostport443(self):
        """Test a proper URL gets parsed the same."""
        u = axonapi.ParserUrl("https://host:443/blah")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"
        assert u.parsed.path == "/blah"
        assert u.url_full == "https://host:443/blah"
        assert u.url == "https://host:443"

    def test_str_repr(self):
        """Test str/repr has URL path."""
        u = axonapi.ParserUrl("https://host:443/blah")
        assert u.parsed.path in format(u)
        assert u.parsed.path in repr(u)

    def test_schemehost_noport443(self):
        """Test port gets added for https scheme."""
        u = axonapi.ParserUrl("https://host")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_host_noschemeport(self):
        """Test exc when no port or scheme in URL."""
        exc = axonapi.HttpError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            axonapi.ParserUrl("host", default_scheme="")

    def test_unknownschemehost_noport(self):
        """Test exc when no port and non http/https scheme."""
        exc = axonapi.HttpError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            axonapi.ParserUrl("httpx://host")

    def test_hostport443_withslash(self):
        """Test scheme added with port 443 and no scheme in URL."""
        u = axonapi.ParserUrl("host:443/")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_hostport443_noscheme(self):
        """Test scheme added with port 443 and no scheme in URL."""
        u = axonapi.ParserUrl("host:443", default_scheme="")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_hostport80_noscheme(self):
        """Test scheme added with port 80 and no scheme in URL."""
        u = axonapi.ParserUrl("host:80", default_scheme="")
        assert u.hostname == "host"
        assert u.port == 80
        assert u.scheme == "http"

    def test_schemehost_noport80(self):
        """Test port added with no port and http scheme in URL."""
        u = axonapi.ParserUrl("http://host")
        assert u.hostname == "host"
        assert u.port == 80
        assert u.scheme == "http"


class TestHttp(object):
    """Test axonapi.http.Http."""

    def test_str_repr(self, httpbin_secure):
        """Test str/repr has URL."""
        url = httpbin_secure.url
        http = axonapi.Http(url=url)
        assert httpbin_secure.url in format(http)
        assert httpbin_secure.url in repr(http)

    def test_parsed_url(self, httpbin_secure):
        """Test url=ParserUrl() works."""
        url = httpbin_secure.url
        parsed_url = axonapi.ParserUrl(url=url, default_scheme="https")
        http = axonapi.Http(url=parsed_url)
        assert httpbin_secure.url in format(http)
        assert httpbin_secure.url in repr(http)

    def test_user_agent(self, httpbin_secure):
        """Test user_agent has version in it."""
        url = httpbin_secure.url
        http = axonapi.Http(url=url)
        assert axonapi.version.__version__ in http.user_agent

    def test_not_quiet_urllib(self, httpbin_secure):
        """Test quiet_urllib=False shows warning from urllib3."""
        url = httpbin_secure.url
        http = axonapi.Http(url=url, quiet_urllib=False)
        with pytest.warns(requests.urllib3.exceptions.InsecureRequestWarning):
            http()

    @pytest.mark.skipif(
        sys.version_info < (3, 6), reason="requires python3.6 or higher"
    )
    def test_verify_ca_bundle(self, httpbin_secure, httpbin_ca_bundle):
        """Test quiet_urllib=False no warning from urllib3 when using ca bundle."""
        url = httpbin_secure.url
        http = axonapi.Http(url=url, log_level_urllib=False, certwarn=False)
        response = http()
        assert response.status_code == 200

    def test_save_last_true(self, httpbin_secure):
        """Test last req/resp with save_last=True."""
        url = httpbin_secure.url
        http = axonapi.Http(url=url, save_last=True, certwarn=False)
        response = http()
        assert response == http._LAST_RESPONSE
        assert response.request == http._LAST_REQUEST

    def test_save_last_false(self, httpbin_secure):
        """Test last req/resp with save_last=False."""
        url = httpbin_secure.url
        http = axonapi.Http(url=url, save_last=False, certwarn=False)
        http()
        assert not http._LAST_RESPONSE
        assert not http._LAST_REQUEST

    def test_save_history(self, httpbin_secure):
        """Test last resp added to history with save_history=True."""
        url = httpbin_secure.url
        http = axonapi.Http(url=url, save_history=True, certwarn=False)
        response = http()
        assert response in http._HISTORY

    def test_log_req_attrs_true(self, httpbin_secure, caplog, log_check):
        """Test verbose logging of request attrs when log_request_attrs=True."""
        caplog.set_level(logging.DEBUG)
        url = httpbin_secure.url
        http = axonapi.Http(url=url, log_request_attrs=True, certwarn=False)
        http()
        entries = ["request.*{}.*headers".format(httpbin_secure.url + "/")]
        assert len(caplog.records) == 1
        log_check(caplog, entries)

    def test_log_req_attrs_false(self, httpbin_secure, caplog, log_check):
        """Test brief logging of request attrs when log_request_attrs=False."""
        caplog.set_level(logging.DEBUG)
        url = httpbin_secure.url
        http = axonapi.Http(url=url, log_request_attrs=False, certwarn=False)
        http()
        entries = ["request.*{}".format(httpbin_secure.url + "/")]
        assert len(caplog.records) == 1
        log_check(caplog, entries)

    def test_log_req_attrs_none(self, httpbin_secure, caplog, log_check):
        """Test no logging of request attrs when log_request_attrs=None."""
        caplog.set_level(logging.DEBUG)
        url = httpbin_secure.url
        http = axonapi.Http(url=url, log_request_attrs=None, certwarn=False)
        http()
        assert not caplog.records

    def test_log_resp_attrs_true(self, httpbin_secure, caplog, log_check):
        """Test verbose logging of response attrs when log_response_attrs=True."""
        caplog.set_level(logging.DEBUG)
        url = httpbin_secure.url
        http = axonapi.Http(url=url, log_response_attrs=True, certwarn=False)
        http()
        entries = ["response.*{}.*headers".format(httpbin_secure.url + "/")]
        assert len(caplog.records) == 1
        log_check(caplog, entries)

    def test_log_resp_attrs_false(self, httpbin_secure, caplog, log_check):
        """Test brief logging of response attrs when log_response_attrs=False."""
        caplog.set_level(logging.DEBUG)
        url = httpbin_secure.url
        http = axonapi.Http(url=url, log_response_attrs=False, certwarn=False)
        http()
        entries = ["response.*{}".format(httpbin_secure.url + "/")]
        assert len(caplog.records) == 1
        log_check(caplog, entries)

    def test_log_response_attrs_none(self, httpbin_secure, caplog, log_check):
        """Test no logging of response attrs when log_response_attrs=None."""
        caplog.set_level(logging.DEBUG)
        url = httpbin_secure.url
        http = axonapi.Http(url=url, log_response_attrs=None, certwarn=False)
        http()
        assert not caplog.records

    def test_log_resp_body_true(self, httpbin_secure, caplog, log_check):
        """Test logging of response body when log_response_body=True."""
        caplog.set_level(logging.DEBUG)
        url = httpbin_secure.url
        http = axonapi.Http(url=url, log_response_body=True, certwarn=False)
        http()
        entries = ["response body:.*"]
        assert len(caplog.records) == 1
        log_check(caplog, entries)

    def test_log_resp_body_false(self, httpbin_secure, caplog, log_check):
        """Test no logging of response body when log_response_body=False."""
        caplog.set_level(logging.DEBUG)
        url = httpbin_secure.url
        http = axonapi.Http(url=url, log_response_body=False, certwarn=False)
        http()
        assert not caplog.records

    def test_log_req_body_true(self, httpbin_secure, caplog, log_check):
        """Test logging of request body when log_request_body=True."""
        caplog.set_level(logging.DEBUG)
        url = httpbin_secure.url
        http = axonapi.Http(url=url, log_request_body=True, certwarn=False)
        http()
        entries = ["request body:.*"]
        assert len(caplog.records) == 1
        log_check(caplog, entries)

    def test_log_req_body_false(self, httpbin_secure, caplog, log_check):
        """Test no logging of request body when log_request_body=False."""
        caplog.set_level(logging.DEBUG)
        url = httpbin_secure.url
        http = axonapi.Http(url=url, log_request_body=False, certwarn=False)
        http()
        assert not caplog.records
