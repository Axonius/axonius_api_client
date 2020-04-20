# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.http."""
import logging
import sys

import pytest
import requests

from axonius_api_client.exceptions import HttpError
from axonius_api_client.http import Http, ParserUrl
from axonius_api_client.version import __version__

from ..meta import (
    TEST_CLIENT_CERT,
    TEST_CLIENT_CERT_NAME,
    TEST_CLIENT_KEY,
    TEST_CLIENT_KEY_NAME,
)
from ..utils import get_url, log_check

InsecureRequestWarning = requests.urllib3.exceptions.InsecureRequestWarning


class TestParserUrl:
    """Test ParserUrl."""

    def test_schemehostport443(self):
        """Test a proper URL gets parsed the same."""
        u = ParserUrl("https://host:443/blah")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"
        assert u.parsed.path == "/blah"
        assert u.url_full == "https://host:443/blah"
        assert u.url == "https://host:443"

    def test_str_repr(self):
        """Test str/repr has URL path."""
        u = ParserUrl("https://host:443/blah")
        assert u.parsed.path in format(u)
        assert u.parsed.path in repr(u)

    def test_schemehost_noport443(self):
        """Test port gets added for https scheme."""
        u = ParserUrl("https://host")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_justhost(self):
        """Test schema added for just host."""
        u = ParserUrl("host")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_justhostport(self):
        """Test schema added for just host and port."""
        u = ParserUrl("host:443")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_host_noschemeport(self):
        """Test exc when no port or scheme in URL."""
        exc = HttpError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            ParserUrl("host", default_scheme="")

    def test_unknownschemehost_noport(self):
        """Test exc when no port and non http/https scheme."""
        exc = HttpError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            ParserUrl("httpx://host")

    def test_hostport443_withslash(self):
        """Test scheme added with port 443 and no scheme in URL."""
        u = ParserUrl("host:443/")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_hostport443_noscheme(self):
        """Test scheme added with port 443 and no scheme in URL."""
        u = ParserUrl("host:443", default_scheme="")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_hostport80_noscheme(self):
        """Test scheme added with port 80 and no scheme in URL."""
        u = ParserUrl("host:80", default_scheme="")
        assert u.hostname == "host"
        assert u.port == 80
        assert u.scheme == "http"

    def test_schemehost_noport80(self):
        """Test port added with no port and http scheme in URL."""
        u = ParserUrl("http://host")
        assert u.hostname == "host"
        assert u.port == 80
        assert u.scheme == "http"


class TestHttp:
    """Test Http."""

    def test_str_repr(self, request):
        """Test str/repr has URL."""
        ax_url = get_url(request)

        http = Http(url=ax_url)

        assert ax_url in format(http)
        assert ax_url in repr(http)

    def test_parsed_url(self, request):
        """Test url=ParserUrl() works."""
        ax_url = get_url(request)

        parsed_url = ParserUrl(url=ax_url, default_scheme="https")

        http = Http(url=parsed_url)

        assert ax_url in format(http)
        assert ax_url in repr(http)

    def test_user_agent(self, request):
        """Test user_agent has version in it."""
        ax_url = get_url(request)

        http = Http(url=ax_url)
        assert __version__ in http.user_agent

    def test_certwarn_true(self, request, httpbin_secure):
        """Test quiet_urllib=False shows warning from urllib3."""
        url = httpbin_secure.url
        http = Http(url=url, certwarn=True, save_history=True)

        with pytest.warns(InsecureRequestWarning):
            http()

    def test_certwarn_false(self, request, httpbin_secure):
        """Test quiet_urllib=False shows warning from urllib3."""
        url = httpbin_secure.url
        http = Http(url=url, certwarn=False)

        http()

    @pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
    def test_verify_ca_bundle(self, request, httpbin_secure, httpbin_ca_bundle):
        """Test quiet_urllib=False no warning from urllib3 when using ca bundle."""
        url = httpbin_secure.url
        http = Http(url=url, certwarn=False)
        response = http()
        assert response.status_code == 200

    def test_save_last_true(self, request):
        """Test last req/resp with save_last=True."""
        ax_url = get_url(request)

        http = Http(url=ax_url, save_last=True, certwarn=False)
        response = http()
        assert response == http.LAST_RESPONSE
        assert response.request == http.LAST_REQUEST

    def test_save_last_false(self, request):
        """Test last req/resp with save_last=False."""
        ax_url = get_url(request)

        http = Http(url=ax_url, save_last=False, certwarn=False)

        http()

        assert not http.LAST_RESPONSE
        assert not http.LAST_REQUEST

    def test_save_history(self, request):
        """Test last resp added to history with save_history=True."""
        ax_url = get_url(request)

        http = Http(url=ax_url, save_history=True, certwarn=False)

        response = http()

        assert response in http.HISTORY

    def test_client_cert_missing_one(self, request, tmp_path):
        """Test cert or key supplied, but not the other."""
        ax_url = get_url(request)
        test_path = tmp_path / TEST_CLIENT_CERT_NAME
        test_path.write_text(TEST_CLIENT_CERT)

        with pytest.raises(HttpError):
            Http(url=ax_url, cert_client_cert=test_path, certwarn=False)

        with pytest.raises(HttpError):
            Http(url=ax_url, cert_client_key=test_path, certwarn=False)

    def test_client_cert_seperate(self, request, tmp_path):
        """Test cert or key supplied, but not the other."""
        ax_url = get_url(request)
        cert_path = tmp_path / TEST_CLIENT_CERT_NAME
        cert_path.write_text(TEST_CLIENT_CERT)
        key_path = tmp_path / TEST_CLIENT_KEY_NAME
        key_path.write_text(TEST_CLIENT_KEY)

        http = Http(
            url=ax_url,
            cert_client_cert=cert_path,
            cert_client_key=key_path,
            certwarn=False,
        )

        http()

    def test_client_cert_both(self, request, tmp_path):
        """Test cert or key supplied, but not the other."""
        ax_url = get_url(request)
        both_path = tmp_path / TEST_CLIENT_CERT_NAME
        both_cert = "{}\n{}\n".format(TEST_CLIENT_CERT, TEST_CLIENT_KEY)
        both_path.write_text(both_cert)

        http = Http(url=ax_url, cert_client_both=both_path, certwarn=False)

        http()

    def test_log_req_attrs_true(self, request, caplog):
        """Test verbose logging of request attrs when log_request_attrs=True."""
        caplog.set_level(logging.DEBUG)

        ax_url = get_url(request)

        http = Http(
            url=ax_url,
            log_request_attrs=["url", "headers"],
            certwarn=False,
            log_level="debug",
        )

        http()

        assert len(caplog.records) == 1

        entries = ["REQUEST ATTRS:.*{}.*headers".format(http.url)]
        log_check(caplog, entries)

    def test_log_req_attrs_none(self, request, caplog):
        """Test no logging of request attrs when log_request_attrs=None."""
        caplog.set_level(logging.DEBUG)

        ax_url = get_url(request)

        http = Http(
            url=ax_url, log_request_attrs=None, certwarn=False, log_level="debug"
        )

        http()

        assert not caplog.records

    def test_log_resp_attrs_true(self, request, caplog):
        """Test verbose logging of response attrs when log_response_attrs=True."""
        caplog.set_level(logging.DEBUG)

        ax_url = get_url(request)

        http = Http(
            url=ax_url,
            log_response_attrs=["url", "headers"],
            certwarn=False,
            log_level="debug",
        )

        http()

        assert len(caplog.records) == 1

        entries = ["RESPONSE ATTRS:.*{}.*headers".format(http.url)]
        log_check(caplog, entries)

    def test_log_response_attrs_all(self, request, caplog):
        """Test no logging of response attrs when log_response_attrs=None."""
        caplog.set_level(logging.DEBUG)

        ax_url = get_url(request)

        http = Http(
            url=ax_url, log_response_attrs="all", certwarn=False, log_level="debug"
        )

        http()

        assert caplog.records

    def test_log_response_attrs_none(self, request, caplog):
        """Test no logging of response attrs when log_response_attrs=None."""
        caplog.set_level(logging.DEBUG)

        ax_url = get_url(request)

        http = Http(
            url=ax_url, log_response_attrs=None, certwarn=False, log_level="debug"
        )

        http()

        assert not caplog.records

    def test_log_resp_body_true(self, request, caplog):
        """Test logging of response body when log_response_body=True."""
        caplog.set_level(logging.DEBUG)

        ax_url = get_url(request)

        http = Http(
            url=ax_url, log_response_body=True, certwarn=False, log_level="debug"
        )

        http()

        assert len(caplog.records) == 1

        entries = ["RESPONSE BODY:.*"]
        log_check(caplog, entries)

    def test_log_resp_body_false(self, request, caplog):
        """Test no logging of response body when log_response_body=False."""
        caplog.set_level(logging.DEBUG)

        ax_url = get_url(request)

        http = Http(
            url=ax_url, log_response_body=False, certwarn=False, log_level="debug"
        )

        http()

        assert not caplog.records

    def test_log_req_body_true(self, request, caplog):
        """Test logging of request body when log_request_body=True."""
        caplog.set_level(logging.DEBUG)

        ax_url = get_url(request)

        http = Http(url=ax_url, log_request_body=True, certwarn=False, log_level="debug")

        http()

        assert len(caplog.records) == 1

        entries = ["REQUEST BODY:.*"]
        log_check(caplog, entries)

    def test_log_req_body_false(self, request, caplog):
        """Test no logging of request body when log_request_body=False."""
        caplog.set_level(logging.DEBUG)

        ax_url = get_url(request)

        http = Http(
            url=ax_url, log_request_body=False, certwarn=False, log_level="debug"
        )

        http()

        assert not caplog.records
