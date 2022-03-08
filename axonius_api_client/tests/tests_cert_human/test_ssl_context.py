# -*- coding: utf-8 -*-
"""Test suite."""
import OpenSSL
import pytest
from axonius_api_client.cert_human import ssl_context


def test_resolve_host_fail():
    with pytest.raises(ValueError):
        ssl_context.resolve_host(host="foobar")


def test_resolve_host_ok():
    data = ssl_context.resolve_host(host="axonius.com")
    assert isinstance(data, str)


def test_get_cnx():
    with ssl_context.get_cnx(host="axonius.com") as cnx:
        cert = cnx.get_peer_certificate()
    assert isinstance(cert, OpenSSL.crypto.X509)
    der = ssl_context.x509_to_der(value=cert)
    assert isinstance(der, bytes) and der
    ders = ssl_context.x509_to_der(value=[cert])
    assert isinstance(ders, list) and len(ders) == 1 and ders[0] == der


def test_x509_to_der_badtype():
    with pytest.raises(TypeError):
        ssl_context.x509_to_der("")


def test_get_cert_bytes():
    data = ssl_context.get_cert(host="axonius.com")
    assert isinstance(data, bytes) and data


def test_get_cert_X509():
    data = ssl_context.get_cert(host="axonius.com", as_bytes=False)
    assert isinstance(data, OpenSSL.crypto.X509)


def test_get_chain_bytes():
    data = ssl_context.get_chain(host="axonius.com")
    assert isinstance(data, list) and data
    for item in data:
        assert isinstance(item, bytes) and item


def test_get_chain_X509():
    data = ssl_context.get_chain(host="axonius.com", as_bytes=False)
    assert isinstance(data, list) and data
    for item in data:
        assert isinstance(item, OpenSSL.crypto.X509)
