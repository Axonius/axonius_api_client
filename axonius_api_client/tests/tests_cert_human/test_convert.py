# -*- coding: utf-8 -*-
"""Test suite."""
import pytest

from axonius_api_client import cert_human

convert = cert_human.convert


class TestGetDerCertCount:
    @pytest.mark.datafiles("certs/server_rsa.crt.pem")
    def test_match(self, datafiles):
        path = datafiles[0]
        server_crt = cert_human.Cert.from_file(path=path)[0]
        value = server_crt.to_der()
        ret = cert_human.convert.get_der_cert_count(value=value)
        assert ret == 1

    def test_no_match(self):
        value = b"XXX"
        ret = cert_human.convert.get_der_cert_count(value=value)
        assert ret == 0


class TestGetDerCsrCount:
    @pytest.mark.datafiles("certs/server_rsa.csr.pem")
    def test_match(self, datafiles):
        path = datafiles[0]
        server_csr = cert_human.CertRequest.from_file(path=path)[0]
        value = server_csr.to_der()
        ret = cert_human.convert.get_der_csr_count(value=value)
        assert ret == 1

    def test_no_match(self):
        value = b"XXX"
        ret = cert_human.convert.get_der_csr_count(value=value)
        assert ret == 0


class TestGetPemCertCount:
    @pytest.mark.datafiles("certs/server_rsa.crt.pem", "certs/server_ec.crt.pem")
    def test_match(self, datafiles):
        chain = []
        for datafile in datafiles:
            chain += cert_human.Cert.from_file(path=datafile)

        value = b"\n\n".join([x.to_pem() for x in chain])
        ret = cert_human.convert.get_pem_cert_count(value=value)
        assert ret == len(chain)

    def test_no_match(self):
        value = b"XXX"
        ret = cert_human.convert.get_pem_cert_count(value=value)
        assert ret == 0


class TestGetPemCsrCount:
    @pytest.mark.datafiles("certs/server_rsa.csr.pem")
    def test_match(self, datafiles):
        path = datafiles[0]
        value = path.read_bytes()
        ret = cert_human.convert.get_pem_csr_count(value=value)
        assert ret == 1

    def test_no_match(self):
        value = b"XXX"
        ret = cert_human.convert.get_pem_csr_count(value=value)
        assert ret == 0


class TestGetPkcs7CertCount:
    @pytest.mark.datafiles("certs/server_rsa.crt.p7b")
    def test_match(self, datafiles):
        path = datafiles[0]
        value = path.read_bytes()
        ret = cert_human.convert.get_pkcs7_cert_count(value=value)
        assert ret == 2

    def test_no_match(self):
        value = b"XXX"
        ret = cert_human.convert.get_pkcs7_cert_count(value=value)
        assert ret == 0


class TestPemToBytes:
    def test_no_pem(self):
        value = b"XXX"
        with pytest.raises(ValueError) as exc:
            cert_human.convert.pem_to_bytes(value=value)

        assert "No PEM encoded" in str(exc.value)

    @pytest.mark.datafiles("certs/server_rsa.csr.pem")
    def test_match(self, datafiles):
        path = datafiles[0]
        value = path.read_bytes()
        items = cert_human.convert.pem_to_bytes(value=value)
        assert len(items) == 1
        assert isinstance(items, list) and items
        for item in items:
            assert isinstance(item, dict) and item


class TestPemToBytesTypes:
    @pytest.mark.datafiles("certs/server_rsa.crt.pem")
    def test_no_types_supplied(self, datafiles):
        path = datafiles[0]
        value = path.read_bytes()
        items = cert_human.convert.pem_to_bytes_types(value=value)
        assert len(items) == 1
        assert isinstance(items, list) and items
        for item in items:
            assert isinstance(item, dict) and item

    @pytest.mark.datafiles("certs/server_rsa.crt.pem")
    def test_types_match(self, datafiles):
        path = datafiles[0]
        value = path.read_bytes()
        items = cert_human.convert.pem_to_bytes_types(
            value=value, types=cert_human.enums.CertTypes.cert.value
        )
        assert len(items) == 1
        assert isinstance(items, list) and items
        for item in items:
            assert isinstance(item, dict) and item

    @pytest.mark.datafiles("certs/server_rsa.csr.pem")
    def test_types_no_match(self, datafiles):
        path = datafiles[0]
        value = path.read_bytes()
        with pytest.raises(ValueError) as exc:
            cert_human.convert.pem_to_bytes_types(
                value=value, types=cert_human.enums.CertTypes.cert.value
            )
        assert "0 items of type" in str(exc.value)
