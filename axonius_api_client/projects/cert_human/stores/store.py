# -*- coding: utf-8 -*-
"""Make SSL certs and their attributes generally more accessible."""
import abc
import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import asn1crypto.algos
import asn1crypto.keys
import asn1crypto.x509
import asn1crypto.core

from ..convert import asn1_to_der, der_to_pem, pem_to_bytes_types
from ..enums import ChainTypes
from ..exceptions import InvalidCertError
from ..paths import PathLike, find_file_exts, pathlib, read_bytes, write_bytes
from ..ssl_extensions import SSLExtension
from ..utils import bytes_to_hex, check_type, human_dict, int_to_hex, str_to_bytes

LOG: logging.Logger = logging.getLogger(__name__)


class Store(abc.ABC):
    """Pass."""

    @classmethod
    @abc.abstractmethod
    def from_content(cls, value: Union[str, bytes], source: Any = None) -> List["Store"]:
        """Pass."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def get_cert_type(cls) -> str:
        """Pass."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def get_file_exts(cls) -> List[str]:
        """Pass."""
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def section_subject(self) -> dict:
        """Get the properties for the subject section."""
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def version(self) -> Union[int, str]:
        """Pass."""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_extensions(self) -> List[asn1crypto.x509.Extensions]:
        """Pass."""
        raise NotImplementedError()

    @abc.abstractmethod
    def to_dict(self, with_extensions: bool = True) -> Dict[str, dict]:
        """Convert this object into a dictionary.

        Returns:
            Dict[str, dict]: keys as sections, values as properties for the section
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def sans(self) -> List[str]:
        """Get the subject alternative names for this cert."""
        raise NotImplementedError()

    def _check(self, check: bool, reason: str, error: bool = True) -> bool:
        """Pass."""
        if not check:
            if error:
                raise InvalidCertError(reason=reason, store=self)
            return False
        return True

    def check_sans(self, error: bool = True) -> bool:
        """Pass."""
        return self._check(
            check=bool(self.sans), reason="has no Subject Alternative Names", error=error
        )

    def check_is_ca(self, error: bool = True) -> bool:
        """Pass."""
        return self._check(
            check=self.is_certificate_authority,
            reason="is not a Certificate Authority",
            error=error,
        )

    def to_str(
        self, join: Optional[str] = "\n", with_extensions: bool = True
    ) -> Union[str, List[str]]:
        """Convert this object into a list of strings."""
        items = []

        if with_extensions:
            exts = self.section_extensions
            for ext in exts:
                items += ["", *ext.to_str()]

        sections = self.to_dict(with_extensions=False)
        for section, attrs in sections.items():
            items += ["", f"# {section.upper()}", *human_dict(value=attrs)]

        return join.join(items) if isinstance(join, str) else items

    @property
    def section_fingerprints(self) -> dict:
        """Get the properties for the fingerprints section."""
        return {"SHA256": self.fingerprint_sha256_hex, "SHA1": self.fingerprint_sha1_hex}

    @property
    def section_source(self) -> dict:
        """Pass."""
        src = self.SOURCE if isinstance(self.SOURCE, dict) else {"source": self.SOURCE}
        return {"chain_order": self.INDEX + 1, "chain_type": self.chain_type, **src}

    @property
    @abc.abstractmethod
    def public_key_info(self) -> asn1crypto.keys.PublicKeyInfo:
        """Pass."""
        raise NotImplementedError()

    @property
    def public_key_algorithm(self) -> asn1crypto.keys.PublicKeyAlgorithm:
        """Pass."""
        return self.public_key_info["algorithm"]

    @property
    def public_key_bit_size(self) -> int:
        """Pass."""
        return self.public_key_info.bit_size

    @property
    def public_key_byte_size(self) -> int:
        """Pass."""
        return self.public_key_info.byte_size

    @property
    def public_key_hex(self) -> str:
        """Get the public key value in hex format."""
        if self.is_elliptic_curve:
            return bytes_to_hex(value=self.public_key_info["public_key"].native)
        return int_to_hex(value=self.public_key_info["public_key"].native["modulus"])

    @property
    def signature_algorithm(self) -> asn1crypto.algos.SignedDigestAlgorithm:
        """Pass."""
        return self.ASN1["signature_algorithm"]

    @property
    def signature_algorithm_str(self) -> str:
        """Pass."""
        return self.signature_algorithm.signature_algo

    @property
    @abc.abstractmethod
    def signature_octet(self) -> asn1crypto.core.OctetBitString:
        """Pass."""
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def is_certificate_authority(self) -> bool:
        """Pass."""
        raise NotImplementedError()

    @property
    def signature_hex(self) -> str:
        """Pass."""
        return bytes_to_hex(value=self.signature_octet.native)

    @property
    def section_extensions(self) -> List[SSLExtension]:
        """Get the extensions section."""
        return SSLExtension.load_list(exts=self.get_extensions())

    @property
    def extensions_by_id(self) -> Dict[str, SSLExtension]:
        """Pass."""
        return {x.extn_id: x for x in self.section_extensions}

    @property
    def section_public_key(self) -> dict:
        """Get the properties for the public key section."""
        return {
            "key": self.public_key_hex,
            "bit_size": self.public_key_bit_size,
            "byte_size": self.public_key_byte_size,
            **self.public_key_algorithm_dict,
            "signature": self.signature_hex,
            "signature_algorithm": self.signature_algorithm_str,
        }

    @property
    def section_details(self) -> dict:
        """Get the properties for the details section."""
        return {
            "type": self.CERT_TYPE,
            "version": self.version,
            "subject_alternative_names": self.sans,
            "is_certificate_authority": self.is_certificate_authority,
        }

    @property
    def public_key_algorithm_dict(self) -> dict:
        """Get the algorithm object for the public key.

        Notes:
            rsa: {"algorithm": "rsa", "parameters": null}
            ec: {"algorithm": "ec", "parameters": "secp256r1"}

        Returns:
            dict: dict with 'algorithm' and 'parameters' keys
        """
        ret = dict(self.public_key_algorithm.native)
        if not self.is_elliptic_curve:
            ret["exponent"] = self.public_key_info["public_key"].native["public_exponent"]
        return ret

    @classmethod
    def _get_log(cls) -> logging.Logger:
        return LOG.getChild(cls.__name__)

    @property
    def subject_short(self) -> str:
        """Pass."""
        return self._to_str_short(obj=self.section_subject)

    def is_valid_host(
        self, host: str, and_cn: bool = True, error: bool = True
    ) -> Tuple[bool, List[str]]:
        """Check if a given domain or IP is valid for this cert.

        Args:
            host (str): domain or IP to check
            error (bool, optional): raise an exception if it is not valid

        Returns:
            bool: if the supplied host is valid for this cert

        Raises:
            ValueError: If the supplied host is not valid and error is True
        """
        valid_hosts = self.get_valid_hosts(and_cn=and_cn)
        if not valid_hosts and error:
            raise ValueError("No Subject Alternative Names defined for this certificate")

        is_valid = host in valid_hosts

        if not is_valid and error:
            msgs = [
                f"Host {host!r} is not valid for this certificate",
                "Valid hosts:",
                *valid_hosts,
            ]
            raise ValueError("\n".join(msgs))
        return is_valid, valid_hosts

    def get_valid_hosts(self, and_cn: bool = True) -> List[str]:
        """Pass."""
        cname = self.section_subject["common_name"]
        return [cname] if and_cn else [] + self.sans

    @classmethod
    def from_pem(
        cls,
        cert: Union[str, bytes],
        source: Any = None,
    ) -> List["Store"]:
        """Pass."""
        types = cls.get_cert_type()
        certs: List[dict] = pem_to_bytes_types(value=cert, source=source, types=types)
        cls._get_log().debug(
            f"Loaded {len(certs)} certificates of type {types!r} from PEM content from {source}"
        )
        return [cls(**x) for x in certs]

    @classmethod
    def from_file(cls, path: PathLike) -> List["Store"]:
        """Pass."""
        path, data = read_bytes(path=path)
        source = {"value": path}
        return cls.from_content(value=data, source=source)

    @classmethod
    def from_directory(cls, path: PathLike) -> Dict[str, List["Store"]]:
        """Pass."""
        path, files = find_file_exts(path=path, exts=cls.get_file_exts(), error=True)
        return {x.name: cls.from_file(path=x) for x in files}

    def to_pem(self, as_str: bool = False, with_comments: bool = True) -> Union[str, bytes]:
        """Get the certificate in PEM format (base64 encoded DER)."""
        ret = der_to_pem(
            value=self.to_der(), cert_type=self.CERT_TYPE, headers=self.CERT_HEADERS, as_str=as_str
        )
        if with_comments:
            # TBD: look into storing in headers instead of comments
            items = [
                f"# date exported: {datetime.datetime.utcnow().isoformat()}",
                f"# subject: {self.subject_short}",
            ]
            if hasattr(self, "issuer_short"):
                items.append(f"# issuer: {self.issuer_short}")

            for k, v in self.section_source.items():
                items.append(f"# source {k}: {v}")

            items = "\n".join(items) + "\n"
            if isinstance(ret, bytes):
                items = str_to_bytes(items)

            ret = items + ret
        return ret

    def to_pem_file(self, **kwargs) -> pathlib.Path:
        """Pass."""
        kwargs["content"] = self.to_pem()
        return write_bytes(**kwargs)

    @classmethod
    def to_pem_file_stores(cls, stores: List["Store"], **kwargs) -> pathlib.Path:
        """Pass."""

        def get_pem(obj):
            check_type(value=obj, exp=cls)
            return obj.to_pem()

        check_type(value=stores, exp=list)
        kwargs["content"] = b"\n\n".join([get_pem(x) for x in stores])
        return write_bytes(**kwargs)

    def to_der(self) -> bytes:
        """Get the certificate in DER format."""
        return asn1_to_der(value=self.ASN1)

    @property
    def fingerprint_sha256_hex(self) -> str:
        """Pass."""
        return bytes_to_hex(value=self.public_key_info.sha256)

    @property
    def fingerprint_sha1_hex(self) -> str:
        """Pass."""
        return bytes_to_hex(value=self.public_key_info.sha1)

    @property
    def is_elliptic_curve(self) -> bool:
        """Check if this cert is an EC or RSA cert."""
        return self.public_key_algorithm["algorithm"].native == "ec"

    @property
    def chain_type(self) -> str:
        """Pass."""
        if self.INDEX == 0:
            return ChainTypes.server.value
        if self.is_certificate_authority:
            return ChainTypes.is_ca.value
        return ChainTypes.unknown.value

    def __str__(self) -> str:
        """Pass."""
        idx = self.INDEX + 1
        try:
            subject = self.subject_short
        except Exception as exc:
            subject = str(exc)

        items = [
            f"subject={subject!r}",
            f"chain_order=#{idx}",
            f"chain_type={self.chain_type!r}",
            f"source={self.SOURCE}",
        ]
        return ", ".join(items)

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()

    def __init__(self, cert: Any, exp: Any, **kwargs):
        """Pass."""
        self.LOG: logging.Logger = self._get_log()
        self.CERT: bytes = cert
        self.CERT_TYPE: str = kwargs.get("cert_type", self.get_cert_type())
        self.CERT_HEADERS: Optional[dict] = kwargs.get("cert_headers")
        self.INDEX: int = kwargs.get("index", 0)
        self.SOURCE: Any = kwargs.get("source")
        self.ASN1: Any = None
        check_type(value=cert, exp=exp)

    @classmethod
    def _short_trans(cls, obj: dict) -> dict:
        """Pass."""
        return {v: obj[k] for k, v in cls.SHORT_TRANS.items() if k in obj}

    @classmethod
    def _to_str_short(cls, obj: dict) -> Union[str, List[str]]:
        """Get a short one-liner string of subject or issuer."""
        items = [f"{k}={v}" for k, v in cls._short_trans(obj=obj).items()]
        return cls.SHORT_JOIN.join(items) if isinstance(cls.SHORT_JOIN, str) else items

    SHORT_TRANS: dict = {
        "country_name": "C",
        "state_or_province_name": "ST",
        "locality_name": "L",
        "organization_name": "O",
        "organizational_unit_name": "OU",
        "common_name": "CN",
    }
    """Translation map to convert an issuer or subject dictionary into it's short-form key names."""

    SHORT_JOIN: Optional[str] = ", "
    """String to join issuer or subject short-form output."""
