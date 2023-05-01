# -*- coding: utf-8 -*-
"""Make SSL certs and their attributes generally more accessible."""
import logging
from typing import Any, Dict, List, Union

import asn1crypto.core
import asn1crypto.csr
import asn1crypto.keys
import asn1crypto.x509
import OpenSSL

from ..convert import (
    asn1_to_der,
    der_to_asn1_csr,
    get_der_csr_count,
    get_pem_csr_count,
    x509_to_der,
)
from ..enums import CertTypes, ChainTypes
from ..ssl_extensions import SSLExtension
from ..utils import str_strip_to_int
from .store import Store

LOG: logging.Logger = logging.getLogger(__name__)


class CertRequest(Store):
    """Make SSL certs and their attributes generally more accessible."""

    FILE_EXTS_PEM: List[str] = [".csr"]
    """File extensions for certificates in PEM format (base64 encoded DER bytes)."""

    FILE_EXTS_DER: List[str] = [".csr"]
    """File extensions for certificates in DER bytes format."""

    FILE_EXTS_PEM_DER: List[str] = [".csr"]
    """File extensions for certificates in PEM or DER bytes format."""

    # EXTEND
    def __init__(
        self,
        cert: Union[bytes, asn1crypto.csr.CertificationRequest, OpenSSL.crypto.X509Req],
        **kwargs,
    ):
        """Pass."""
        kwargs["exp"] = (bytes, asn1crypto.csr.CertificationRequest, OpenSSL.crypto.X509Req)
        super().__init__(cert=cert, **kwargs)

        if isinstance(cert, bytes):
            self.CERT: bytes = cert
            self.ASN1: asn1crypto.csr.CertificationRequest = der_to_asn1_csr(
                value=cert, source=self.SOURCE
            )
        elif isinstance(cert, asn1crypto.csr.CertificationRequest):
            self.CERT: bytes = asn1_to_der(value=cert)
            self.ASN1: asn1crypto.csr.CertificationRequest = cert
        elif isinstance(cert, OpenSSL.crypto.X509Req):
            self.CERT: bytes = x509_to_der(value=cert)
            self.ASN1: asn1crypto.csr.CertificationRequest = der_to_asn1_csr(
                value=self.CERT, source=self.SOURCE
            )

    # EXTEND
    @property
    def section_details(self) -> dict:
        """Get the properties for the details section."""
        ret = super().section_details
        ret.update(
            {
                "subject_short_form": self.subject_short,
            }
        )
        return ret

    # OVERRIDE
    @property
    def chain_type(self) -> str:
        """Pass."""
        return ChainTypes.csr.value

    # ABC
    @classmethod
    def get_cert_type(cls) -> str:
        """Pass."""
        return CertTypes.csr.value

    # ABC
    @classmethod
    def get_file_exts(cls) -> List[str]:
        """Pass."""
        file_exts = [*cls.FILE_EXTS_PEM, *cls.FILE_EXTS_DER, *cls.FILE_EXTS_PEM_DER]
        return list(set(file_exts))

    # ABC
    @classmethod
    def from_content(cls, value: Union[str, bytes], source: Any = None) -> List["Store"]:
        """Pass."""
        if source is not None and not isinstance(source, dict):
            source = {"source": source}

        source = source or {}

        if get_pem_csr_count(value=value) >= 1:
            source["method"] = "from_content:pem"
            return cls.from_pem(cert=value, source=source)

        if get_der_csr_count(value=value) >= 1:
            source["method"] = "from_content:der"
            return [cls(cert=value, source=source)]

        msgs = (f"No PEM or DER certificate requests found in content from {source}",)
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
            "subject": self.section_subject,
            "details": self.section_details,
            "source": self.section_source,
        }
        if with_extensions:
            ret["extensions"] = [x.to_dict() for x in self.section_extensions]
        return ret

    # ABC
    @property
    def is_certificate_authority(self) -> bool:
        """Pass."""
        ext = self.extensions_by_id.get("basic_constraints")
        return ext.value.get("ca", False) if isinstance(ext, SSLExtension) else False

    # ABC
    @property
    def sans(self) -> List[str]:
        """Get the subject alternative names for this cert."""
        ext = self.extensions_by_id.get("subject_alt_name")
        return ext.value if isinstance(ext, SSLExtension) else []

    # ABC
    def get_extensions(self) -> List[asn1crypto.x509.Extension]:
        """Pass."""
        ret = []
        attrs = self.request_info["attributes"]
        for attr in attrs:
            for value in attr["values"]:
                if isinstance(value, asn1crypto.x509.Extensions):
                    ret += [x for x in value if x not in ret]
        return ret

    # ABC
    @property
    def section_subject(self) -> dict:
        """Get the properties for the subject section."""
        return dict(self.request_info["subject"].native)

    # ABC
    @property
    def public_key_info(self) -> asn1crypto.keys.PublicKeyInfo:
        """Pass."""
        return self.request_info["subject_pk_info"]

    # ABC
    @property
    def signature_octet(self) -> asn1crypto.core.OctetBitString:
        """Pass."""
        return self.ASN1["signature"]

    # ABC
    @property
    def version(self) -> Union[int, str]:
        """Pass."""
        return str_strip_to_int(value=self.request_info["version"].native)

    # CSR ONLY
    @property
    def request_info(self) -> asn1crypto.csr.CertificationRequestInfo:
        """Pass."""
        return self.ASN1["certification_request_info"]
