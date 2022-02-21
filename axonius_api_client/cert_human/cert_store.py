# -*- coding: utf-8 -*-
"""Tools for working with SSL certificate files."""
import datetime
import logging
from typing import Dict, List, Optional, Union

import asn1crypto.cms
import asn1crypto.pem
import asn1crypto.x509

from .extensions import Extension
from .paths import PathLike, find_file_exts, pathlib, read_bytes, write_bytes
from .ssl_context import get_cert, get_chain
from .tools import bytes_to_hex, check_type, human_dict, int_to_hex, str_strip_to_int, str_to_bytes

LOG: logging.Logger = logging.getLogger(__name__)
CERT_TYPE: str = "CERTIFICATE"

# XXX requests check?
# XXX add is_valid(): is_expired or is_self_signed


class CertStore:
    """Make SSL certs and their attributes generally more accessible."""

    EXTS_PEM: List[str] = [".pem", ".ca-bundle"]
    EXTS_PEM_DER: List[str] = [*EXTS_PEM, ".cer", ".crt", ".der"]
    EXTS_PKCS7: List[str] = [".p7b", ".p7r", ".spc"]
    EXTS: List[str] = [*EXTS_PEM_DER, *EXTS_PKCS7]
    """Supported file formats:

    .cer        B64 or DER  - one or more certs
    .crt        B64 or DER  - one or more certs
    .pem        B64         - one or more certs
    .ca-bundle  B64         - one or more certs
    .p7b        PKCS#7      - one or more certs
    .p7r        PKCS#7      - one or more certs
    .spc        PKCS#7      - one or more certs
    .der        DER         - one cert

    Unsupported features:
    - Passphrase protected (pycrptodome or cryptography needed as requirements)
    - PKCS#12 format (.pfx, .p12)
    """

    SHORT_TRANS: dict = {
        "country_name": "C",
        "state_or_province_name": "ST",
        "locality_name": "L",
        "organization_name": "O",
        "organizational_unit_name": "OU",
        "common_name": "CN",
    }
    SHORT_JOIN: Optional[str] = ", "

    def __init__(
        self,
        cert: bytes,
        cert_type: str = CERT_TYPE,
        cert_headers: Optional[dict] = None,
        index: int = 0,
        source: Optional[PathLike] = None,
    ):
        """Pass."""
        self.LOG: logging.Logger = LOG.getChild(self.__class__.__name__)

        self.CERT: bytes = cert
        self.CERT_TYPE: str = cert_type
        self.CERT_HEADERS: Optional[dict] = cert_headers
        self.INDEX: int = index
        self.SOURCE: Optional[PathLike] = source

        # XXX try/cls
        self.ASN: asn1crypto.x509.Certificate = asn1crypto.x509.Certificate.load(encoded_data=cert)

    @classmethod
    def from_host_cert(
        cls, host: str, port: int = 443, source: Optional[PathLike] = None
    ) -> "CertStore":
        """Pass."""
        source = source or f"certificate from {host}:{port}"
        der: bytes = get_cert(host=host, port=port, as_bytes=True)
        return cls(cert=der, source=source)

    @classmethod
    def from_host_chain(
        cls, host: str, port: int = 443, source: Optional[PathLike] = None
    ) -> List["CertStore"]:
        """Pass."""
        source = source or f"certificate chain from {host}:{port}"
        ders: List[bytes] = get_chain(host=host, port=port, as_bytes=True)
        return [cls(cert=x, index=idx, source=source) for idx, x in enumerate(ders)]

    @classmethod
    def from_pem(
        cls, value: Union[str, bytes], source: Optional[PathLike] = None
    ) -> List["CertStore"]:
        """Pass."""
        source = source or f"{type(value).__name__} value from_pem"
        return [cls(**obj) for obj in cls._pem_to_bytes(value=value, source=source)]

    @classmethod
    def from_pkcs7(cls, value: bytes, source: PathLike = None) -> List["CertStore"]:
        """Pass."""
        source = source or f"{type(value).__name__} value from_pkcs7"
        ders: List[bytes] = cls._pkcs7_to_bytes(value=value)
        return [cls(cert=x, source=source, index=idx) for idx, x in enumerate(ders)]

    @classmethod
    def from_path_file(cls, path: PathLike, **kwargs) -> List["CertStore"]:
        """Pass."""
        path, data = read_bytes(path=path, exts=cls.EXTS)

        if path.suffix in cls.EXTS_PEM or cls._is_pem(value=data):
            return cls.from_pem(value=data, source=path)

        if path.suffix in cls.EXTS_PKCS7:
            return cls.from_pkcs7(value=data, source=path)

        return [cls(cert=data, **kwargs)]

    @classmethod
    def from_path_directory(cls, path: PathLike) -> Dict[str, List["CertStore"]]:
        """Pass."""
        path, files = find_file_exts(path=path, exts=cls.EXTS, error=True)
        return {x.name: cls.from_path_file(path=x) for x in files}

    def to_pem(self) -> bytes:
        """Get the certificate in PEM format (base64 encoded DER)."""
        return self._der_to_pem(
            value=self.to_der(), cert_type=self.CERT_TYPE, headers=self.CERT_HEADERS
        )

    def to_path_file(self, **kwargs) -> pathlib.Path:
        """Pass."""
        kwargs["content"] = self.to_pem()
        return write_bytes(**kwargs)

    @staticmethod
    def to_path_file_stores(stores: List["CertStore"], **kwargs) -> pathlib.Path:
        """Pass."""

        def get_pem(obj):
            check_type(value=obj, exp=CertStore)
            return obj.to_pem()

        check_type(value=stores, exp=list)
        kwargs["content"] = "\n".join([get_pem(x) for x in stores])
        return write_bytes(**kwargs)

    def to_der(self) -> bytes:
        """Get the certificate in DER format."""
        return self.ASN.dump()

    def to_dict(self, with_extensions: bool = True) -> Dict[str, dict]:
        """Convert this object into a dictionary.

        Returns:
            Dict[str, dict]: keys as sections, values as proprties for the section
        """
        ret = {
            "public_key": self.public_key,
            "fingerprints": self.fingerprints,
            "issuer": self.issuer,
            "subject": self.subject,
            "details": self.details,
        }
        if with_extensions:
            ret["extensions"] = [x.to_dict() for x in self.get_extensions()]
        return ret

    def to_str(
        self, with_extensions: bool = True, join: Optional[str] = "\n"
    ) -> Union[str, List[str]]:
        """Convert this object into a list of strings."""
        items = []

        if with_extensions:
            exts = self.get_extensions()
            for ext in exts:
                items += ["", *ext.to_str()]

        for section, attrs in self.to_dict(with_extensions=False).items():
            items += ["", f"# {section.upper()}", *human_dict(value=attrs)]

        return join.join(items) if isinstance(join, str) else items

    def to_str_subject(self) -> str:
        """Pass."""
        return self._to_str_short(obj=self.subject)

    def to_str_issuer(self) -> str:
        """Pass."""
        return self._to_str_short(obj=self.issuer)

    @property
    def fingerprints(self) -> dict:
        """Get the properties for the fingerprints section."""
        return {"SHA256": self.fingerprint_sha256_hex, "SHA1": self.fingerprint_sha1_hex}

    @property
    def issuer(self) -> dict:
        """Get the properties for the issuer section."""
        return dict(self.ASN.issuer.native)

    @property
    def subject(self) -> dict:
        """Get the properties for the subject section."""
        return dict(self.ASN.subject.native)

    @property
    def public_key(self) -> dict:
        """Get the properties for the public key section."""
        return {
            "key": self.public_key_hex,
            "key_size": self.public_key_size,
            **self.public_key_algorithm,
            "signature": self.signature_hex,
            "signature_algorithm": self.signature_algorithm,
            "serial_number": self.serial_number_hex,
        }

    def get_extensions(self) -> List[Extension]:
        """Get the extensions section."""
        return Extension.load_list(exts=[x for x in self.ASN["tbs_certificate"]["extensions"]])

    def is_domain_ip_valid(self, value: str, err: bool = False) -> bool:
        """Check if a given domain or IP is valid for this cert.

        Args:
            value (str): domain or IP to check
            err (bool, optional): raise an exception if its not valid

        Returns:
            bool: if the supplied value is valid for this cert

        Raises:
            ValueError: If the supplied value is not valid and err is True
        """
        is_valid = self.ASN.is_valid_domain_ip(value)
        if not is_valid and err:
            msgs = [
                f"{value!r} is not a valid domain or IP for this certificate",
                "Valid domain & IPs:",
                *self.valid_domain_ips,
            ]
            raise ValueError("\n".join(msgs))
        return is_valid

    @property
    def is_expired(self) -> bool:
        """Check if this cert is expired."""
        return datetime.datetime.now(datetime.timezone.utc) > self.ASN.not_valid_after

    @property
    def is_elliptic_curve(self) -> bool:
        """Check if this cert is an EC or RSA cert."""
        return self.public_key_algorithm["algorithm"] == "ec"

    @property
    def is_self_signed(self) -> bool:
        """Pass."""
        return self.ASN.self_signed

    @property
    def is_self_issued(self) -> bool:
        """Pass."""
        return self.ASN.self_issued not in ["no"]

    @property
    def fingerprint_sha256_hex(self) -> str:
        """Pass."""
        return bytes_to_hex(value=self.ASN.sha256)

    @property
    def fingerprint_sha1_hex(self) -> str:
        """Pass."""
        return bytes_to_hex(value=self.ASN.sha1)

    @property
    def serial_number_hex(self) -> str:
        """Pass."""
        return bytes_to_hex(value=self.ASN["tbs_certificate"]["serial_number"].contents)

    @property
    def signature_hex(self) -> str:
        """Pass."""
        return bytes_to_hex(value=self.ASN.signature)

    @property
    def signature_algorithm(self) -> str:
        """Pass."""
        return self.ASN.signature_algo

    @property
    def public_key_hex(self) -> str:
        """Get the public key value in hex format."""
        if self.is_elliptic_curve:
            return bytes_to_hex(value=self.ASN.public_key["public_key"].native)
        return int_to_hex(value=self.ASN.public_key["public_key"].native["modulus"])

    @property
    def public_key_size(self) -> int:
        """Pass."""
        return self.ASN.public_key.bit_size

    @property
    def public_key_algorithm(self) -> dict:
        """Get the algorithm object for the public key.

        Notes:
            rsa: {"algorithm": "rsa", "parameters": null}
            ec: {"algorithm": "ec", "parameters": "secp256r1"}

        Returns:
            dict: dict with 'algorithm' and 'parameters' keys
        """
        ret = dict(self.ASN.public_key["algorithm"].native)
        if not ret["algorithm"] == "ec":
            ret["exponent"] = self.ASN.public_key["public_key"].native["public_exponent"]
        return ret

    @property
    def details(self) -> dict:
        """Get the properties for the details section."""
        return {
            "version": self.version,
            "valid_domains": self.valid_domains,
            "valid_ips": self.valid_ips,
            "is_self_signed": self.is_self_signed,
            "is_self_issued": self.is_self_issued,
            "is_expired": self.is_expired,
            "not_valid_before": self.not_valid_before,
            "not_valid_after": self.not_valid_after,
        }

    @property
    def not_valid_before(self) -> datetime.datetime:
        """Pass."""
        return self.ASN.not_valid_before

    @property
    def not_valid_after(self) -> datetime.datetime:
        """Pass."""
        return self.ASN.not_valid_after

    @property
    def valid_domains(self) -> List[str]:
        """Pass."""
        return self.ASN.valid_domains

    @property
    def valid_ips(self) -> List[str]:
        """Pass."""
        return self.ASN.valid_ips

    @property
    def valid_domain_ips(self) -> List[str]:
        """Get the subject common name and all subject alternative names for this cert.

        Notes:
            If no subject alt name, and the common name in the subject looks like
            a domain, that is considered the valid list.

            The common name should not be used if the subject alt name is present.
            ref: https://tools.ietf.org/html/rfc6125#section-6.4.4
        """
        return self.valid_domains + self.valid_ips

    @property
    def version(self) -> Union[int, str]:
        """Pass."""
        return str_strip_to_int(value=self.ASN["tbs_certificate"]["version"].native)

    @property
    def source(self) -> str:
        """Pass."""
        return "" if self.SOURCE is None else f"{self.SOURCE}"

    @classmethod
    def _pem_to_bytes(cls, value: Union[str, bytes], source: Optional[str] = None) -> List[dict]:
        """Pass."""
        check_type(value=value, exp=(str, bytes))
        pem_bytes = str_to_bytes(value=value)

        if not cls._is_pem(value=pem_bytes):
            raise ValueError("No PEM encoded certificate found in supplied value")

        keys = ["cert_type", "cert_headers", "cert", "source", "index"]
        gen = enumerate(asn1crypto.pem.unarmor(pem_bytes=pem_bytes, multiple=True))
        return [dict(zip(keys, [*item, source, idx])) for idx, item in gen]

    @classmethod
    def _pkcs7_to_bytes(cls, value: bytes, source: Optional[str] = None) -> List[bytes]:
        """Pass."""
        check_type(value=value, exp=bytes)
        obj = asn1crypto.cms.ContentInfo.load(encoded_data=value)
        return [x.dump() for x in obj["content"]["certificates"]]

    @staticmethod
    def _der_to_pem(
        value: bytes, cert_type: str = CERT_TYPE, headers: Optional[dict] = None
    ) -> bytes:
        """Convert from DER to PEM format.

        Args:
            value (bytes): The DER cert to convert to PEM
            cert_type (str, optional): the text to use in the BEGIN and END barriers
            headers (Optional[dict], optional): header lines to write after the BEGIN barrier
        """
        check_type(value=value, exp=bytes)
        return asn1crypto.pem.armor(type_name=cert_type, der_bytes=value, headers=headers)

    @staticmethod
    def _is_pem(value: Union[str, bytes]) -> bool:
        """Check if the supplied value is an SSL Certificate in PEM format."""
        value = str_to_bytes(value=value, strict=False)
        return asn1crypto.pem.detect(byte_string=value) if isinstance(value, bytes) else False

    @classmethod
    def _short_trans(cls, obj: dict) -> dict:
        """Pass."""
        return {v: obj[k] for k, v in cls.SHORT_TRANS.items() if k in obj}

    @classmethod
    def _to_str_short(cls, obj: dict) -> Union[str, List[str]]:
        """Get a short one liner string of subject or issuer."""
        items = [f"{k}={v}" for k, v in cls._short_trans(obj=obj).items()]
        return cls.SHORT_JOIN.join(items) if isinstance(cls.SHORT_JOIN, str) else items

    def __str__(self) -> str:
        """Pass."""
        items = [
            f"INDEX={self.INDEX + 1}",
            f"SUBJECT={self.to_str_subject()!r}",
            f"ISSUER={self.to_str_issuer()!r}",
            f"SOURCE={self.source!r}",
        ]
        return ", ".join(items)

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()
