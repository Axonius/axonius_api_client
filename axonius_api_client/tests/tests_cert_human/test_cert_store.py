# -*- coding: utf-8 -*-
"""Test suite."""
"""
import asn1crypto.x509
import pytest
from axonius_api_client import cert_human


@pytest.mark.datafiles("pkcs7_rsa_2.p7b")
class TestPkcs7:
    def test_f_pkcs7_to_asn1(self, datafile):
        value = datafile.read_bytes()
        data = cert_human.Cert._pkcs7_to_asn1(value=value)
        assert isinstance(data, list)
        assert len(data) == 2
        for cert in data:
            assert isinstance(cert, asn1crypto.x509.Certificate)

    def test_from_pkcs7(self, datafile):
        value = datafile.read_bytes()
        data = cert_human.Cert.from_pkcs7(value=value)
        assert isinstance(data, list)
        assert len(data) == 2
        for idx, cert in enumerate(data):
            assert isinstance(cert, cert_human.Cert)
            assert cert.INDEX == idx

    def test_from_file(self, datafile):
        data = cert_human.Cert.from_file(path=datafile)
        assert isinstance(data, list)
        assert len(data) == 2
        for idx, cert in enumerate(data):
            assert isinstance(cert, cert_human.Cert)
            assert cert.INDEX == idx

"""
