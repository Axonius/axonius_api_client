# -*- coding: utf-8 -*-
"""Tools for working with SSL certificate files."""
from typing import List, Optional, Union

import asn1crypto.cms
import asn1crypto.csr
import asn1crypto.pem
import asn1crypto.x509
import OpenSSL

from .enums import CertTypes
from .utils import bytes_to_str, check_type, listify, str_to_bytes


def get_der_cert_count(value: Union[str, bytes]) -> int:
    """Pass."""
    check_type(value=value, exp=(str, bytes))
    try:
        der_to_asn1_cert(value=value)
    except Exception:
        return 0
    else:
        return 1


def get_der_csr_count(value: Union[str, bytes]) -> int:
    """Pass."""
    check_type(value=value, exp=(str, bytes))
    try:
        der_to_asn1_csr(value=value)
    except Exception:
        return 0
    else:
        return 1


def get_pem_cert_count(value: Union[str, bytes]) -> int:
    """Pass."""
    check_type(value=value, exp=(str, bytes))
    try:
        certs = pem_to_bytes_types(value=value, types=CertTypes.cert.value)
    except Exception:
        return 0
    else:
        return len(certs)


def get_pem_csr_count(value: Union[str, bytes]) -> int:
    """Pass."""
    check_type(value=value, exp=(str, bytes))
    try:
        certs = pem_to_bytes_types(value=value, types=CertTypes.csr.value)
    except Exception:
        return 0
    else:
        return len(certs)


def get_pkcs7_cert_count(value: Union[str, bytes]) -> int:
    """Pass."""
    check_type(value=value, exp=(str, bytes))
    try:
        certs = pkcs7_to_asn1_cert(value=value)
    except Exception:
        return 0
    else:
        return len(certs)


def detect_is_pem(value: Union[str, bytes]) -> bool:
    """Check if the supplied value is an SSL Certificate in PEM format."""
    value: bytes = str_to_bytes(value=value, strict=False)
    ret: bool = False
    if isinstance(value, bytes):
        ret: bool = asn1crypto.pem.detect(byte_string=value)
    return ret


def pem_to_bytes_types(
    value: Union[str, bytes],
    types: Optional[Union[str, List[str]]] = None,
    source: Optional[str] = None,
) -> List[dict]:
    """Pass."""
    types = listify(types)
    items: List[dict] = pem_to_bytes(value=value, source=source)
    certs = [x for x in items if x["cert_type"] in types] if types else items

    if not certs:
        raise ValueError(
            f"{len(certs)} items of type {types} found in {len(items)} items from {source}"
        )

    return certs


def pem_to_bytes(value: Union[str, bytes], source: Optional[str] = None) -> List[dict]:
    """Pass."""
    check_type(value=value, exp=(str, bytes))
    pem_bytes = str_to_bytes(value=value)

    if not detect_is_pem(value=pem_bytes):
        raise ValueError(f"No PEM encoded certificate found in supplied value from {source}")

    keys = ["cert_type", "cert_headers", "cert", "source", "index"]
    gen = asn1crypto.pem.unarmor(pem_bytes=pem_bytes, multiple=True)
    items = [dict(zip(keys, [*item, source, idx])) for idx, item in enumerate(gen)]
    return items


def pkcs7_to_asn1_cert(
    value: bytes, source: Optional[str] = None
) -> List[asn1crypto.x509.Certificate]:
    """Pass."""
    objs: List[asn1crypto.cms.ContentInfo] = pkcs7_to_asn1(value=value, source=source)
    certs: List[asn1crypto.x509.Certificate] = []
    for obj in objs:
        certs += [x.chosen for x in obj["content"]["certificates"]]
    if not certs:
        raise ValueError(f"No certificates found from {source}")
    return certs


def pkcs7_to_asn1(
    value: Union[str, bytes], source: Optional[str] = None
) -> List[asn1crypto.cms.ContentInfo]:
    """Pass."""

    def loader(value):
        try:
            obj = asn1crypto.cms.ContentInfo.load(encoded_data=value)
        except Exception as exc:
            raise ValueError(f"Invalid SSL Certificate in PKCS7 format from {source}: {exc}")

        try:
            obj.native
        except Exception as exc:
            raise ValueError(f"Invalid SSL Certificate in PKCS7 format format from {source}: {exc}")
        return obj

    check_type(value=value, exp=(str, bytes))
    if detect_is_pem(value=value):
        objs = pem_to_bytes_types(value=value, types=CertTypes.pkcs7.value, source=source)
        value = [x["cert"] for x in objs]

    return [loader(x) for x in value] if isinstance(value, list) else [loader(value)]


def der_to_asn1_cert(value: bytes, source: Optional[str] = None) -> asn1crypto.x509.Certificate:
    """Pass."""
    check_type(value=value, exp=bytes)

    try:
        obj = asn1crypto.x509.Certificate.load(encoded_data=value)
    except Exception as exc:
        raise ValueError(f"Invalid SSL Certificate in DER bytes format from {source}: {exc}")

    try:
        obj.native
    except Exception as exc:
        raise ValueError(f"Invalid SSL Certificate in DER bytes format from {source}: {exc}")

    return obj


def der_to_asn1_csr(
    value: bytes, source: Optional[str] = None
) -> asn1crypto.csr.CertificationRequest:
    """Pass."""
    check_type(value=value, exp=bytes)

    try:
        obj = asn1crypto.csr.CertificationRequest.load(encoded_data=value)
    except Exception as exc:
        raise ValueError(
            f"Invalid SSL Certificate Request in DER bytes format from {source}: {exc}"
        )

    try:
        obj.native
    except Exception as exc:
        raise ValueError(
            f"Invalid SSL Certificate Request in DER bytes format from {source}: {exc}"
        )

    return obj


def der_to_pem_cert(value: bytes, headers: Optional[dict] = None) -> bytes:
    """Convert from DER to PEM format.

    Args:
        value (bytes): The DER cert to convert to PEM
        cert_type (str, optional): the text to use in the `BEGIN` and `END` barriers
        headers (Optional[dict], optional): header lines to write after the `BEGIN` barrier
    """
    return der_to_pem(value=value, cert_type=CertTypes.cert.value, headers=headers)


def der_to_pem(
    value: bytes, cert_type: str, headers: Optional[dict] = None, as_str: bool = False
) -> Union[str, bytes]:
    """Convert from DER to PEM format.

    Args:
        value (bytes): The DER cert to convert to PEM
        cert_type (str, optional): the text to use in the `BEGIN` and `END` barriers
        headers (Optional[dict], optional): header lines to write after the `BEGIN` barrier
    """
    check_type(value=value, exp=bytes)
    ret = asn1crypto.pem.armor(type_name=cert_type, der_bytes=value, headers=headers)
    if as_str:
        ret = bytes_to_str(value=ret)
    return ret


def asn1_to_der(
    value: Union[asn1crypto.x509.Certificate, asn1crypto.csr.CertificationRequest]
) -> bytes:
    """Pass."""
    check_type(value=value, exp=(asn1crypto.x509.Certificate, asn1crypto.csr.CertificationRequest))
    return value.dump()


def x509_to_der(
    value: Union[
        OpenSSL.crypto.X509,
        OpenSSL.crypto.X509Req,
        List[Union[OpenSSL.crypto.X509, OpenSSL.crypto.X509Req]],
    ]
) -> Union[bytes, List[bytes]]:
    """Pass."""
    if isinstance(value, list):
        return [x509_to_der(value=x) for x in value]

    check_type(value=value, exp=(OpenSSL.crypto.X509, OpenSSL.crypto.X509Req))
    if isinstance(value, OpenSSL.crypto.X509):
        return OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, value)
    if isinstance(value, OpenSSL.crypto.X509Req):
        return OpenSSL.crypto.dump_certificate_request(OpenSSL.crypto.FILETYPE_ASN1, value)
