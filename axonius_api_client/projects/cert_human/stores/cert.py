# -*- coding: utf-8 -*-
"""Make SSL certs and their attributes generally more accessible."""
import datetime
import logging
from typing import Any, Dict, List, Union

import asn1crypto.keys
import asn1crypto.x509
import asn1crypto.core

import OpenSSL
import requests

from ..convert import (
    asn1_to_der,
    der_to_asn1_cert,
    get_der_cert_count,
    get_pem_cert_count,
    get_pkcs7_cert_count,
    pkcs7_to_asn1_cert,
    x509_to_der,
)
from ..enums import CertTypes
from ..ssl_capture import inject_into_urllib3
from ..ssl_context import get_cert, get_chain
from ..utils import bytes_to_hex, str_strip_to_int, parse_url
from .store import Store

LOG: logging.Logger = logging.getLogger(__name__)


class Cert(Store):
    """Make SSL certs and their attributes generally more accessible."""

    FILE_EXTS_PEM: List[str] = [".pem", ".ca-bundle", ".cer", ".crt"]
    """File extensions for certificates in PEM format."""

    FILE_EXTS_DER: List[str] = [".der", ".cer", ".crt"]
    """File extensions for certificates in DER bytes format."""

    FILE_EXTS_PEM_DER: List[str] = [".cer", "crt"]
    """File extensions for certificates in PEM or DER bytes format."""

    FILE_EXTS_PKCS7: List[str] = [".p7b", ".p7r", ".spc", ".pkcs7"]
    """File extensions for certificates in PKCS7 bytes format."""

    FILE_EXTS_PKCS12: List[str] = [".pfx", ".p12", ".pkcs12"]
    """File extensions for certificates in PKCS12 bytes format."""
    # TBD: PKCS#12 not yet supported due to password protection

    # EXTEND
    def __init__(
        self, cert: Union[bytes, asn1crypto.x509.Certificate, OpenSSL.crypto.X509], **kwargs
    ):
        """Pass."""
        kwargs["exp"] = (bytes, asn1crypto.x509.Certificate, OpenSSL.crypto.X509)
        super().__init__(cert=cert, **kwargs)

        if isinstance(cert, bytes):
            self.CERT: bytes = cert
            self.ASN1: asn1crypto.x509.Certificate = der_to_asn1_cert(
                value=cert, source=self.SOURCE
            )
        elif isinstance(cert, asn1crypto.x509.Certificate):
            self.CERT: bytes = asn1_to_der(value=cert)
            self.ASN1: asn1crypto.x509.Certificate = cert
        elif isinstance(cert, OpenSSL.crypto.X509):
            self.CERT: bytes = x509_to_der(value=cert)
            self.ASN1: asn1crypto.x509.Certificate = der_to_asn1_cert(
                value=self.CERT, source=self.SOURCE
            )

    def check_expired(self, error: bool = True) -> bool:
        """Pass."""
        return self._check(
            check=not self.is_expired,
            reason=f"expired on {self.not_valid_after}",
            error=error,
        )

    # EXTEND
    @property
    def section_public_key(self) -> dict:
        """Get the properties for the public key section."""
        ret = super().section_public_key
        ret["serial_number"] = self.serial_number_hex
        return ret

    # EXTEND
    @property
    def section_details(self) -> dict:
        """Get the properties for the details section."""
        ret = super().section_details
        ret.update(
            {
                "is_self_signed": self.is_self_signed_str,
                "is_self_issued": self.is_self_issued,
                "is_expired": self.is_expired,
                "not_valid_before": self.not_valid_before,
                "not_valid_after": self.not_valid_after,
                "issuer_short_form": self.issuer_short,
                "subject_short_form": self.subject_short,
            }
        )
        return ret

    # ABC
    @property
    def public_key_info(self) -> asn1crypto.keys.PublicKeyInfo:
        """Pass."""
        return self.ASN1.public_key

    # ABC
    @property
    def section_subject(self) -> dict:
        """Get the properties for the subject section."""
        return dict(self.ASN1.subject.native)

    # ABC
    @property
    def version(self) -> Union[int, str]:
        """Pass."""
        return str_strip_to_int(value=self.ASN1["tbs_certificate"]["version"].native)

    # ABC
    @classmethod
    def get_cert_type(cls) -> str:
        """Pass."""
        return CertTypes.cert.value

    # ABC
    @classmethod
    def get_file_exts(cls) -> List[str]:
        """Pass."""
        file_exts = [
            *cls.FILE_EXTS_PEM,
            *cls.FILE_EXTS_DER,
            *cls.FILE_EXTS_PEM_DER,
            *cls.FILE_EXTS_PKCS7,
        ]
        return list(set(file_exts))

    # ABC
    @classmethod
    def from_content(cls, value: Union[str, bytes], source: Any = None) -> List["Store"]:
        """Pass."""
        if source is not None and not isinstance(source, dict):
            source = {"source": source}

        source = source or {}

        if get_pem_cert_count(value=value) >= 1:
            source["method"] = "from_content:pem"
            return cls.from_pem(cert=value, source=source)

        if get_pkcs7_cert_count(value=value) >= 1:
            source["method"] = "from_content:pkcs7"
            return cls.from_pkcs7(cert=value, source=source)

        if get_der_cert_count(value=value) >= 1:
            source["method"] = "from_content:der"
            return [cls(cert=value, source=source)]

        msgs = (f"No PEM, PCKS7, or DER certificates found in content from {source}",)
        raise ValueError("\n".join(msgs))

    # ABC
    def to_dict(self, with_extensions: bool = True) -> Dict[str, dict]:
        """Convert this object into a dictionary.

        Returns:
            Dict[str, dict]: keys as sections, values as properties for the section
        """
        ret = {
            "public_key": self.section_public_key,
            "fingerprints": self.section_fingerprints,
            "issuer": self.section_issuer,
            "subject": self.section_subject,
            "details": self.section_details,
            "source": self.section_source,
        }
        if with_extensions:
            ret["extensions"] = [x.to_dict() for x in self.section_extensions]  # abc
        return ret

    # ABC
    def get_extensions(self) -> List[asn1crypto.x509.Extension]:
        """Pass."""
        return [x for x in self.ASN1["tbs_certificate"]["extensions"]]

    # ABC
    @property
    def is_certificate_authority(self) -> bool:
        """Pass."""
        return self.ASN1.ca

    # ABC
    @property
    def signature_octet(self) -> asn1crypto.core.OctetBitString:
        """Pass."""
        return self.ASN1["signature_value"]

    # ABC
    @property
    def sans(self) -> List[str]:
        """Get the subject alternative names for this cert."""
        return self.ASN1.valid_domains + self.ASN1.valid_ips

    # CERT ONLY
    @property
    def serial_number_hex(self) -> str:
        """Pass."""
        return bytes_to_hex(value=self.ASN1["tbs_certificate"]["serial_number"].contents)

    # CERT ONLY
    @property
    def is_expired(self) -> bool:
        """Check if this cert is expired."""
        return datetime.datetime.now(datetime.timezone.utc) > self.ASN1.not_valid_after

    # CERT ONLY
    @property
    def is_self_signed_bool(self) -> bool:
        """Pass."""
        return self.is_self_signed_str not in ["no"]

    # CERT ONLY
    @property
    def is_self_signed_str(self) -> str:
        """Pass."""
        return self.ASN1.self_signed

    # CERT ONLY
    @property
    def is_self_issued(self) -> bool:
        """Pass."""
        return self.ASN1.self_issued

    # CERT ONLY
    @property
    def not_valid_before(self) -> datetime.datetime:
        """Pass."""
        return self.ASN1.not_valid_before

    # CERT ONLY
    @property
    def not_valid_after(self) -> datetime.datetime:
        """Pass."""
        return self.ASN1.not_valid_after

    # CERT ONLY
    @property
    def issuer_short(self) -> str:
        """Pass."""
        return self._to_str_short(obj=self.section_issuer)

    # CERT ONLY
    @property
    def section_issuer(self) -> dict:
        """Get the properties for the issuer section."""
        return dict(self.ASN1.issuer.native)

    # CERT ONLY
    @classmethod
    def from_requests_cert(cls, url: str, **kwargs) -> "Cert":
        """Pass."""
        url = parse_url(url)
        cls.inject_results = inject_into_urllib3()
        source = {"url": url, "method": f"{cls.__module__}.{cls.__name__}.from_requests_cert"}
        kwargs.setdefault("verify", False)
        response: requests.Response = requests.get(url, **kwargs)
        cert: OpenSSL.crypto.X509 = response.raw.captured_cert
        cls._get_log().debug(f"Loaded 1 certificate from {source}")
        return cls(cert=cert, source=source)

    # CERT ONLY
    @classmethod
    def from_requests_chain(cls, url: str, **kwargs) -> List["Cert"]:
        """Pass."""
        url = parse_url(url)
        cls.inject_results = inject_into_urllib3()
        source = {"url": url, "method": f"{cls.__module__}.{cls.__name__}.from_requests_chain"}
        kwargs.setdefault("verify", False)
        response: requests.Response = requests.get(url, **kwargs)
        certs: List[OpenSSL.crypto.X509] = response.raw.captured_chain
        cls._get_log().debug(f"Loaded {len(certs)} certificates from {source}")
        return [cls(cert=x, index=idx, source=source) for idx, x in enumerate(certs)]

    # CERT ONLY
    @classmethod
    def from_host_cert(cls, host: str, port: int = 44) -> "Cert":
        """Pass."""
        source = {
            "host": host,
            "port": port,
            "method": f"{cls.__module__}.{cls.__name__}.from_host_cert",
        }
        cert: bytes = get_cert(host=host, port=port, as_bytes=True)
        cls._get_log().debug(f"Loaded 1 certificate from {source}")
        return cls(cert=cert, source=source)

    # CERT ONLY
    @classmethod
    def from_host_chain(cls, host: str, port: int = 443) -> List["Cert"]:
        """Pass."""
        source = {
            "host": host,
            "port": port,
            "method": f"{cls.__module__}.{cls.__name__}.from_host_chain",
        }
        certs: List[bytes] = get_chain(host=host, port=port, as_bytes=True)
        cls._get_log().debug(f"Loaded {len(certs)} certificates from {source}")
        return [cls(cert=x, index=idx, source=source) for idx, x in enumerate(certs)]

    # CERT ONLY
    @classmethod
    def from_pkcs7(cls, cert: bytes, source: Any = None) -> List["Cert"]:
        """Pass."""
        certs: List[asn1crypto.x509.Certificate] = pkcs7_to_asn1_cert(value=cert, source=source)
        cls._get_log().debug(f"Loaded {len(certs)} certificates from PKCS7 content from {source}")
        return [cls(cert=x, source=source, index=idx) for idx, x in enumerate(certs)]
