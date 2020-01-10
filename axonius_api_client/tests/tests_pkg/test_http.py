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

TEST_CLIENT_CERT_NAME = "client_cert.crt"
TEST_CLIENT_CERT = """
-----BEGIN CERTIFICATE-----
MIIEtDCCApygAwIBAgIJAPuK1/Z7X2zbMA0GCSqGSIb3DQEBDQUAMFgxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMRkwFwYDVQQKDBBBeG9uaXVzIENJ
IFRlc3RzMRkwFwYDVQQDDBBBeG9uaXVzQ0lUZXN0c0NBMB4XDTE5MTIyNDEzMTYx
NFoXDTM5MDIyMjEzMTYxNFowgYsxCzAJBgNVBAYTAklMMREwDwYDVQQIDAhUZWwg
QXZpdjEKMAgGA1UEBwwBLjEKMAgGA1UEEQwBLjEQMA4GA1UECgwHQXhvbml1czEM
MAoGA1UECwwDUiZEMQwwCgYDVQQDDANCb2IxIzAhBgkqhkiG9w0BCQEWFGJvYkBh
eG9uaXVzdGVzdHMubGFuMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
t/p+x2hlsidVdoDkEnAV7S0t4DTQE4Iir8VGm/Rjb9Gv+O3T/VWPGYYm2roiSS0q
0DCNOSy8qx28+vccgdPdyflCte9/mas6dTRvXDM3nDLloqI9lQy8Tf1X3rhRDs8a
EZCmfiATUETPr7vp3+LjriHpSnc/siaUFdDxEWRIbAIR3zNDv7MJD7k16HQCK+5k
iCtJJXcelYC856vEASORJibUU/Q15KqgegM/ATf6NLem5fYO2dZhQMSj8nW8Cw2Q
pAo+uUdeDMLscREEG933zH0qDCNaGyjAY7JUqlHXEBtL2GSADNp2WGLyK4xMdTiB
HqGi05DvFKRXnBvs1YOdnQIDAQABo00wSzAxBgNVHSUEKjAoBggrBgEFBQcDAQYI
KwYBBQUHAwIGCCsGAQUFBwMDBggrBgEFBQcDBDAJBgNVHRMEAjAAMAsGA1UdDwQE
AwIF4DANBgkqhkiG9w0BAQ0FAAOCAgEAlyog4NTiu4jvEOisGtm4fWupNBaEC25B
c9+hntj2454NG3i3s5hkB65A6tFEoWWNSI74CEw/VKzecjqOzAuW4d5qYxA/jtX4
50Ws0fqzPxKvJTnhzzgOAHpiyxWrJASlp3fhK73Z2aRY6xNr8RoAXsQabj5wU3gm
kNzUZel5VVcB0Entmjcp2COqIvIm81Wumz+URE732hoC5ZnRDBAlu8zrMqptHU+4
WBgGBoQUMI3AJcE2UmZlCofsXni+jdr8ZN1j/xbu79W7xCHcQzm3//teWy2KAXp/
JfFfJ6tkO63hVGV9xGlIC0DK6Z17qy1uEwNKfu2qFvl6msCNT8AeyM5DJwEX//3S
ITxeZCPzznQx38Hth/ZOuCx5C8FT+mLv8Eoac+bC45HOckCK3wACYIPUCzwSDzxn
2AWBWP9ltF5/wJu854s23ylJ0Wu2NJArq5vuuA8SSf2Hb4f3Q4J6097iAQ0zunYK
t06o6EU8iDGxCZ+0Ev1Ocx/6d6wU1W/TBrN1veDQxsd5SQpNc0Q18m5YCcq1yDyt
DvpaMDAyxvLZtDAfPOd/KgpWUThIcdhAmT+tzde8bTrT306PPzbi5pIgaCsNGBb8
w4gw3wK/xMly7xZxoLD3YujN/sCcOFY3nhkB+L71GRlX8qYV5uS9fdbTKGZD7SYs
Ck4QKLYy+P0=
-----END CERTIFICATE-----
"""

TEST_CLIENT_KEY_NAME = "client_cert.key"
TEST_CLIENT_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAt/p+x2hlsidVdoDkEnAV7S0t4DTQE4Iir8VGm/Rjb9Gv+O3T
/VWPGYYm2roiSS0q0DCNOSy8qx28+vccgdPdyflCte9/mas6dTRvXDM3nDLloqI9
lQy8Tf1X3rhRDs8aEZCmfiATUETPr7vp3+LjriHpSnc/siaUFdDxEWRIbAIR3zND
v7MJD7k16HQCK+5kiCtJJXcelYC856vEASORJibUU/Q15KqgegM/ATf6NLem5fYO
2dZhQMSj8nW8Cw2QpAo+uUdeDMLscREEG933zH0qDCNaGyjAY7JUqlHXEBtL2GSA
DNp2WGLyK4xMdTiBHqGi05DvFKRXnBvs1YOdnQIDAQABAoIBAGOGeiDrg+AtURlL
PpYO1n24rBGW4F09UABgKwNg4I30FEsIdV6dc00uekRm3vdRHNEFAtDEN8glzT7C
gURmVZvWYNVFG3UI4RXYaMmq11GDYyBovgGsow1ZmLheY1MsjACmjLq8JVaN8wAx
GqLH/b0MkUR8YBPCtOdcYZyz8E2kohvw2P8DBmzUCFXuELHRh5eJ4nRv9ZdF8jw2
YOYnnBFrWJzE9YA+UCi67oGpMumcu91+tsenc3tvxXJX/HCSBiCc3GEHSROw0SjQ
TKLLPC+pT5wfmHGFeBPvKFpcfncx50IiTAcnHuBTQJvUvoNkiViBhS5ZG8Pranlq
w+fBlyECgYEA3wqTnkZFWR6Rl1cSUZRIAeKga380lNcnydhLbmBhiFxr7KoGiuyZ
cBcGqock0/sng6AwEl9d59ni3I5/2p4DtJmYxx8QU2XmUXSKdGH34qIXL6T27ow0
292vYIUFAT4vyawkKtO7FlKc+p5frL+dzIDcNOJPj0wfMivRDd33dokCgYEA0yo2
X9hLqNoq5X+UUVfhlgAswb7wDelx19up3QWX12eRMnwztTp070L/aoMpJaQuXUTC
HwF4Muffe8XsHMM+n9Jb8SToacspXwF0QrciVVowfdN/tyyP9ZVYzM9jSTm7K0NA
upfUccDxhgSNv6zNQNKix2qoNIQQuq4OxQpaqXUCgYEAxzmgT/D+wrL+YwtAbqQf
iaePmVV/dy+T98R+5DGtDOtY74WT4IWkLK40ox+h8sNVMUplhhOvQoiqDk4uv+0C
7E+CWuJRZ90OVFXf0kMr80DLqyAT/VI5aObkXzeSF+EfOGnNyH9ljnPuiiHq3dgu
sFut1oMLg7j/6IWg710ETNkCgYEAz/PWMHU1rUeMzw3g5mqBQdNSQErk5Q5sioNM
uNj1O7BGkU03LtYuqiF0n1QjhWo2Lquz8Azmblti/uVfLMQqPAJRgR0ztFvaljE8
aScorJ1w+7j5IU7FRriZBrmFsWslI+nLKPa0xIGaWLzLS2PFjnzgyToEBBO61dzr
tqgHuLECgYBA5nJsbMc36x55d61/4XLkX4Pmoh/LtTEZt9LyoWXUOq86vZuP1W/u
fcCY7mv+lRAoiAC1Z38YjGgJmZINH9EoaVnZJNeaO/86qemnlwYQ5/DIViycPZWI
oXO3sikOr2yrDS95jHjVzU0iW3xzu8bM9D01swBx0T5kYKWZo4ywpQ==
-----END RSA PRIVATE KEY-----
"""


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

    @pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
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

    def test_client_cert_missing_one(self, request, tmp_path):
        """Test cert or key supplied, but not the other."""
        ax_url = utils.get_url(request)
        test_path = tmp_path / TEST_CLIENT_CERT_NAME
        test_path.write_text(TEST_CLIENT_CERT)

        with pytest.raises(exceptions.HttpError):
            axonapi.Http(url=ax_url, cert_client_cert=test_path, certwarn=False)

        with pytest.raises(exceptions.HttpError):
            axonapi.Http(url=ax_url, cert_client_key=test_path, certwarn=False)

    def test_client_cert_seperate(self, request, tmp_path):
        """Test cert or key supplied, but not the other."""
        ax_url = utils.get_url(request)
        cert_path = tmp_path / TEST_CLIENT_CERT_NAME
        cert_path.write_text(TEST_CLIENT_CERT)
        key_path = tmp_path / TEST_CLIENT_KEY_NAME
        key_path.write_text(TEST_CLIENT_KEY)

        http = axonapi.Http(
            url=ax_url,
            cert_client_cert=cert_path,
            cert_client_key=key_path,
            certwarn=False,
        )

        http()

    def test_client_cert_both(self, request, tmp_path):
        """Test cert or key supplied, but not the other."""
        ax_url = utils.get_url(request)
        both_path = tmp_path / TEST_CLIENT_CERT_NAME
        both_cert = "{}\n{}\n".format(TEST_CLIENT_CERT, TEST_CLIENT_KEY)
        both_path.write_text(both_cert)

        http = axonapi.Http(url=ax_url, cert_client_both=both_path, certwarn=False)

        http()

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
