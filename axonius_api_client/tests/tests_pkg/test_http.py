# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.http."""
import logging

import pytest
import requests

import urllib3.exceptions

from axonius_api_client.exceptions import HttpError
from axonius_api_client.http import Http
from axonius_api_client.projects.url_parser import UrlParser
from axonius_api_client.projects import cert_human
from axonius_api_client.version import __version__

from ..meta import (
    TEST_CLIENT_CERT,
    TEST_CLIENT_CERT_NAME,
    TEST_CLIENT_KEY,
    TEST_CLIENT_KEY_NAME,
)
from ..utils import (
    get_arg_url,
    log_check,
    get_http,
)

InsecureRequestWarning = urllib3.exceptions.InsecureRequestWarning


class TestHttp:
    """Test Http."""

    def test_str_repr(self, request):
        """Test str/repr has URL."""
        ax_url = get_arg_url(request)
        http = Http(url=ax_url)
        assert ax_url in format(http)
        assert ax_url in repr(http)

    def test_parsed_url(self, request):
        """Test url=UrlParser() works."""
        ax_url = get_arg_url(request)
        parsed_url = UrlParser(url=ax_url, default_scheme="https")
        http = Http(url=parsed_url)
        assert ax_url in format(http)
        assert ax_url in repr(http)

    def test_user_agent(self, request):
        """Test user_agent has version in it."""
        ax_url = get_arg_url(request)
        http = Http(url=ax_url)
        assert __version__ in http.user_agent

    # def test_certwarn_true(self, httpbin_secure):
    #     url = httpbin_secure.url
    #     http = Http(url=url, certwarn=True, save_history=True)
    #     with pytest.warns(InsecureRequestWarning):
    #         http()

    # def test_certwarn_false(self, httpbin_secure):
    #     url = httpbin_secure.url
    #     http = Http(url=url, certwarn=False)
    #     with pytest.warns() as record:
    #         response = http()
    #     assert response
    #     assert record

    def test_save_last_true(self, request):
        """Test last req/resp with save_last=True."""
        ax_url = get_arg_url(request)
        http = Http(url=ax_url, save_last=True, certwarn=False)
        with pytest.warns() as record:
            response = http()
        assert response
        assert record
        assert response == http.LAST_RESPONSE
        # request can be different due to redirects
        # assert response.request == http.LAST_REQUEST

    def test_save_last_false(self, request):
        """Test last req/resp with save_last=False."""
        ax_url = get_arg_url(request)
        http = Http(url=ax_url, save_last=False, certwarn=False)
        with pytest.warns() as record:
            response = http()
        assert response
        assert record
        assert not http.LAST_RESPONSE
        assert not http.LAST_REQUEST

    def test_save_history(self, request):
        """Test last resp added to history with save_history=True."""
        ax_url = get_arg_url(request)
        http = Http(url=ax_url, save_history=True, certwarn=False)
        with pytest.warns() as record:
            response = http()
        assert response
        assert record
        assert response in http.HISTORY

    def test_client_cert_missing_one(self, request, tmp_path):
        """Test cert or key supplied, but not the other."""
        ax_url = get_arg_url(request)
        test_path = tmp_path / TEST_CLIENT_CERT_NAME
        test_path.write_text(TEST_CLIENT_CERT)
        with pytest.raises(HttpError):
            Http(url=ax_url, cert_client_cert=test_path, certwarn=False)

        with pytest.raises(HttpError):
            Http(url=ax_url, cert_client_key=test_path, certwarn=False)

    def test_client_cert_separate(self, request, tmp_path):
        """Test cert or key supplied, but not the other."""
        ax_url = get_arg_url(request)
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

        with pytest.warns() as record:
            response = http()
        assert response
        assert record

    def test_client_cert_both(self, request, tmp_path):
        """Test cert or key supplied, but not the other."""
        ax_url = get_arg_url(request)
        both_path = tmp_path / TEST_CLIENT_CERT_NAME
        both_cert = "{}\n{}\n".format(TEST_CLIENT_CERT, TEST_CLIENT_KEY)
        both_path.write_text(both_cert)
        http = Http(url=ax_url, cert_client_both=both_path, certwarn=False)
        with pytest.warns() as record:
            response = http()
        assert response
        assert record

    def test_log_req_attrs_true(self, request, caplog):
        """Test verbose logging of request attrs when log_request_attrs=True."""
        caplog.set_level(logging.DEBUG)
        http = get_http(
            request, log_request_attrs=["url", "headers"], log_level="debug"
        )
        with pytest.warns() as record:
            response = http()
        assert response
        assert record
        entries = ["REQUEST ATTRS:.*{}.*headers".format(http.url)]
        log_check(caplog, entries)

    def test_log_req_attrs_none(self, request, caplog):
        """Test no logging of request attrs when log_request_attrs=None."""
        caplog.set_level(logging.DEBUG)
        http = get_http(request, log_request_attrs=None, log_level="debug")
        with pytest.warns() as record:
            response = http()
        assert response
        assert record
        entries = ["REQUEST ATTRS:"]
        log_check(caplog, entries, exists=False)

    def test_log_resp_attrs_true(self, request, caplog):
        """Test verbose logging of response attrs when log_response_attrs=True."""
        caplog.set_level(logging.DEBUG)
        http = get_http(
            request, log_response_attrs=["url", "headers"], log_level="debug"
        )
        with pytest.warns() as record:
            response = http()
        assert response
        assert record
        entries = ["RESPONSE ATTRS:.*url.*headers"]
        log_check(caplog, entries)

    def test_get_cert(self, request):
        """Test get_cert."""
        http = get_http(request)
        cert = http.get_cert()
        assert isinstance(cert, cert_human.Cert)

    def test_get_cert_chain(self, request):
        """Test get_cert_chain."""
        http = get_http(request)
        chain = http.get_cert_chain()
        assert (
            isinstance(chain, list)
            and chain
            and all(isinstance(c, cert_human.Cert) for c in chain)
        )

    def test_safe_request(self, request):
        """Test safe request."""
        http = get_http(request)
        data = http.safe_request(path="/force_error", method="POST")
        assert isinstance(data, requests.Response) or data is None

    def test_log_response_attrs_all(self, request, caplog):
        """Test no logging of response attrs when log_response_attrs=None."""
        caplog.set_level(logging.DEBUG)
        http = get_http(request, log_response_attrs="all", log_level="debug")
        with pytest.warns() as record:
            response = http()
        assert response
        assert record
        entries = ["RESPONSE ATTRS:"]
        log_check(caplog, entries)

    def test_log_response_attrs_none(self, request, caplog):
        """Test no logging of response attrs when log_response_attrs=None."""
        caplog.set_level(logging.DEBUG)
        http = get_http(request, log_response_attrs=None, log_level="debug")
        with pytest.warns() as record:
            response = http()
        assert response
        assert record
        entries = ["RESPONSE ATTRS:.*"]
        log_check(caplog, entries, exists=False)

    def test_log_resp_body_true(self, request, caplog):
        """Test logging of response body when log_response_body=True."""
        caplog.set_level(logging.DEBUG)
        http = get_http(request, log_response_body=True, log_level="debug")
        with pytest.warns() as record:
            response = http()
        assert response
        assert record
        entries = ["RESPONSE BODY.*"]
        log_check(caplog, entries)

    def test_log_resp_body_false(self, request, caplog):
        """Test no logging of response body when log_response_body=False."""
        caplog.set_level(logging.DEBUG)
        http = get_http(request, log_response_body=False, log_level="debug")
        with pytest.warns() as record:
            response = http()
        assert response
        assert record
        entries = ["RESPONSE BODY.*"]
        log_check(caplog, entries, exists=False)

    def test_log_req_body_true(self, request, caplog):
        """Test logging of request body when log_request_body=True."""
        caplog.set_level(logging.DEBUG)
        http = get_http(request, log_request_body=True, log_level="debug")
        with pytest.warns() as record:
            response = http()
        assert response
        assert record
        entries = ["REQUEST BODY.*"]
        log_check(caplog, entries)

    def test_log_req_body_false(self, request, caplog):
        """Test no logging of request body when log_request_body=False."""
        caplog.set_level(logging.DEBUG)
        http = get_http(request, log_request_body=False, log_level="debug")
        with pytest.warns() as record:
            response = http()
        assert response
        assert record
        entries = ["REQUEST BODY:.*"]
        log_check(caplog, entries, exists=False)

    # TBD
    # def test_verify_ca_bundle(self, request, httpbin_secure, httpbin_ca_bundle):
    #     Test quiet_urllib=False no warning from urllib3 when using ca bundle.
    #     url = httpbin_secure.url
    #     http = Http(url=url, certwarn=False)
    #     with pytest.warns() as record:
    #         response = http()
    #     assert response.status_code == 200
    #     assert record
