# -*- coding: utf-8 -*-
"""Tools for working with SSL certificate files."""
import dataclasses
import datetime
import logging
import struct
from typing import Any, Generator, List, Optional, Tuple

import asn1crypto.x509

from .ct_logs import load_ct_logs
from .enums import HashAlgorithms, SctVersions, SignatureAlgorithms
from .utils import (
    b64_to_hex,
    bytes_to_b64,
    bytes_to_hex,
    bytes_to_str,
    check_type,
    get_subcls,
    human_dict,
    human_key_value,
    str_strip_to_int,
)

LOG: logging.Logger = logging.getLogger(__name__)


class SSLExtension:
    """Pass."""

    EXTN_ID: str = ""
    NAME: str = ""
    DOTTED: str = ""
    BYTES_AS_HEX: bool = True

    def __init__(self, ext: asn1crypto.x509.Extension):
        """Pass."""
        self.EXT: asn1crypto.x509.Extension = ext
        self.LOG: logging.Logger = LOG.getChild(self.__class__.__name__)

    def __str__(self) -> str:
        """Pass."""
        return f"EXTENSION: {self.name} ( {self.dotted} ) [CRITICAL: {self.critical}]"

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()

    @classmethod
    def load(cls, ext: asn1crypto.x509.Extension, **kwargs) -> "SSLExtension":
        """Pass."""
        check_type(value=ext, exp=asn1crypto.x509.Extension)
        extn_id = ext.native["extn_id"]
        dotted = ext.children[0].dotted
        for subcls in get_subcls(SSLExtension):
            if subcls.EXTN_ID == extn_id or subcls.DOTTED == dotted:
                return subcls(ext=ext, **kwargs)

        LOG.getChild(cls.__name__).debug(f"Unmapped extension ID {extn_id!r} dotted {dotted!r}")
        return cls(ext=ext)

    @classmethod
    def load_list(cls, exts: List[asn1crypto.x509.Extension], **kwargs) -> List["SSLExtension"]:
        """Pass."""
        check_type(value=exts, exp=list)
        return [cls.load(ext=x, **kwargs) for x in exts]

    def to_dict(self) -> dict:
        """Pass."""
        return {
            "name": self.name,
            "dotted": self.dotted,
            "id": self.extn_id,
            "critical": self.critical,
            "value": self.value,
        }

    def to_str(self) -> List[str]:
        """Pass."""
        items = [f"# {self}", *self.value_to_str]
        return items

    @property
    def value_for_str(self) -> Any:
        """Pass."""
        return self.value

    @property
    def value_to_str(self) -> List[str]:
        """Pass."""
        value = self.value_for_str
        if isinstance(value, dict):
            return human_dict(value=value)

        if isinstance(value, list) and all([isinstance(x, dict) for x in value]):
            items = []
            for idx, obj in enumerate(value):
                items += [f"  - Item #{idx + 1}:", *human_dict(value=obj, indent=4)]
            return items

        return [human_key_value(key="Value", value=self.value)]

    @property
    def name(self) -> str:
        """Pass."""
        return self.NAME or "UNMAPPED EXTENSION: {}".format(self.extn_id.replace("_", " ").title())

    @property
    def dotted(self) -> str:
        """Pass."""
        return self.EXT.children[0].dotted

    @property
    def extn_id(self) -> str:
        """Pass."""
        return self.EXT.native["extn_id"]

    @property
    def critical(self) -> bool:
        """Pass."""
        return self.EXT.native["critical"]

    @property
    def native_value(self) -> Any:
        """Pass."""
        return self.EXT.native["extn_value"]

    @property
    def value(self) -> Any:
        """Pass."""
        return self.parse_native(value=self.native_value)

    @classmethod
    def parse_native(cls, value: Any) -> Any:
        """Pass."""
        if isinstance(value, dict):
            return {k: cls.parse_native(value=v) for k, v in value.items()}
        if isinstance(value, (tuple, list)):
            return [cls.parse_native(value=x) for x in value]
        if isinstance(value, bytes):
            if cls.BYTES_AS_HEX:
                return bytes_to_hex(value=value)
            else:
                return bytes_to_str(value=value, strict=False)
        if isinstance(value, set):
            return list(value)
        return value


class CARevocationUrl(SSLExtension):
    """Pass."""

    EXTN_ID: str = "2.16.840.1.113730.1.4"
    NAME: str = "Certificate Authority Revocation URL"
    DOTTED: str = "2.16.840.1.113730.1.4"
    BYTES_AS_HEX: bool = False


class NetscapeCertificateComment(SSLExtension):
    """Pass."""

    EXTN_ID: str = "2.16.840.1.113730.1.13"
    NAME: str = "Netscape Certificate Comment"
    DOTTED: str = "2.16.840.1.113730.1.13"
    BYTES_AS_HEX: bool = False


class NetscapeCertificateType(SSLExtension):
    """Pass."""

    EXTN_ID: str = "netscape_certificate_type"
    NAME: str = "Netscape Certificate Type"
    DOTTED: str = "2.16.840.1.113730.1.1"


class AuthorityKeyIdentifier(SSLExtension):
    """Pass."""

    EXTN_ID: str = "authority_key_identifier"
    NAME: str = "Authority Key Identifier"
    DOTTED: str = "2.5.29.35"


class SubjectKeyIdentifier(SSLExtension):
    """Pass."""

    EXTN_ID: str = "key_identifier"
    NAME: str = "Subject Key Identifier"
    DOTTED: str = "2.5.29.14"


class SubjectAlternativeName(SSLExtension):
    """Pass."""

    EXTN_ID: str = "subject_alt_name"
    NAME: str = "Subject Alternative Name"
    DOTTED: str = "2.5.29.17"


class KeyUsage(SSLExtension):
    """Pass."""

    EXTN_ID: str = "key_usage"
    NAME: str = "Key Usage"
    DOTTED: str = "2.5.29.15"


class ExtendedKeyUsage(SSLExtension):
    """Pass."""

    EXTN_ID: str = "extended_key_usage"
    NAME: str = "Extended Key Usage"
    DOTTED: str = "2.5.29.37"


class CRLDistributionPoints(SSLExtension):
    """Pass."""

    EXTN_ID: str = "crl_distribution_points"
    NAME: str = "CRL Distribution Points"
    DOTTED: str = "2.5.29.31"


class CertificatePolicies(SSLExtension):
    """Pass."""

    EXTN_ID: str = "certificate_policies"
    NAME: str = "Certificate Policies"
    DOTTED: str = "2.5.29.32"


class AuthorityInformationAccess(SSLExtension):
    """Pass."""

    EXTN_ID: str = "authority_information_access"
    NAME: str = "Certificate Authority Information Access"
    DOTTED: str = "1.3.6.1.5.5.7.1.1"


class BasicConstraints(SSLExtension):
    """Pass."""

    EXTN_ID: str = "basic_constraints"
    NAME: str = "Basic Constraints"
    DOTTED: str = "2.5.29.19"

    @property
    def value_for_str(self) -> Any:
        """Pass."""
        value = self.value
        return {
            "certificate_authority": value["ca"],
            "path_length_constraint": value["path_len_constraint"],
        }


class SignedCertificateTimestampList(SSLExtension):
    """Pass."""

    EXTN_ID: str = "signed_certificate_timestamp_list"
    NAME: str = "Embedded Signed Certificate Timestamp List"
    DOTTED: str = "1.3.6.1.4.1.11129.2.4.2"

    @property
    def value(self) -> List[dict]:
        """Pass."""
        try:
            return [x.to_dict() for x in SctParser.from_bytes(data=self.EXT.children[2].contents)]
        except Exception:
            self.LOG.debug(f"Failed to parse SCT data from {self.EXT}", exc_info=True)
            return []

    @property
    def value_for_str(self) -> Any:
        """Pass."""

        def handle(item):
            """Pass."""
            operator = item.pop("log_operator")
            ret = {f"operator_{k}": operator.get(k) for k in op_keys}
            ret.update(item)
            return ret

        value = self.value
        op_keys = ["name", "description", "url"]
        return [handle(x) for x in value]


@dataclasses.dataclass
class SctParser:
    """Pass."""

    raw_version: int
    raw_log_key_id: bytes
    raw_timestamp: int
    raw_extensions: bytes
    raw_hash_algorithm: int
    raw_signature_algorithm: int
    raw_signature: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> List["SctParser"]:
        """Pass."""
        len_data, data = cls._split_header(data=data)
        return [
            cls._parse_section(data=x) for x in cls._split_sections(data=data, len_data=len_data)
        ]

    def to_dict(self) -> dict:
        """Pass."""
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "log_operator": self.log_operator,
            "log_key_id": self.log_key_id,
            "signature": self.signature,
            "signature_algorithm": self.signature_algorithm,
            "extensions": self.extensions,
        }

    @property
    def version(self) -> int:
        """Pass."""
        return str_strip_to_int(value=SctVersions.get_name_by_value(value=self.raw_version))

    @property
    def timestamp(self) -> datetime.datetime:
        """Pass."""
        return datetime.datetime.fromtimestamp(self.raw_timestamp / 1000.0)

    @property
    def signature_algorithm(self) -> Optional[str]:
        """Pass."""
        # want return like 'ecdsa-with-SHA256'
        sig_algo = SignatureAlgorithms.get_name_by_value(value=self.raw_signature_algorithm)
        hash_algo = HashAlgorithms.get_name_by_value(value=self.raw_hash_algorithm)
        return f"{sig_algo}-with-{hash_algo}"

    @property
    def signature(self) -> str:
        """Pass."""
        return bytes_to_hex(value=self.raw_signature)

    @property
    def log_key_id(self) -> str:
        """Pass."""
        return bytes_to_hex(value=self.raw_log_key_id)

    @property
    def log_key_id_base64(self) -> str:
        """Pass."""
        return bytes_to_b64(value=self.raw_log_key_id)

    @property
    def extensions(self) -> str:
        """Pass."""
        return self.raw_extensions.decode("utf-8", "xmlcharrefreplace")

    @property
    def log_operator(self) -> dict:
        """Pass."""
        lookup = self.log_key_id_base64
        data = load_ct_logs()
        operators: List[dict] = data["operators"]
        for operator in operators:
            logs: List[dict] = operator["logs"]
            for log in logs:
                if lookup == log["log_id"]:
                    ret = {
                        "log_id": b64_to_hex(value=log["log_id"]),
                        "key": b64_to_hex(value=log["key"]),
                        "name": operator["name"],
                        "email": operator["email"],
                    }
                    ret.update(log)
                    ret = {k: v for k, v in sorted(ret.items())}
                    return ret

        return {
            "description": f"Unable to find operator for bas64 Log Key ID: {lookup!r}",
            "log_id": self.log_key_id,
            "key": "",
            "url": "",
            "mmd": 86400,
        }

    @classmethod
    def _parse_section(cls, data: bytes) -> "SctParser":
        """Pass."""
        packed, data = cls._split_bytes(data, 41)
        raw_version, raw_log_key_id, raw_timestamp = struct.unpack("!B32sQ", packed)

        extensions_len, data = cls._split_len_struct(data)
        raw_extensions, data = cls._split_bytes(data, extensions_len)

        raw_hash_algorithm, raw_signature_algorithm, raw_signature_len = struct.unpack(
            "!BBH", data[:4]
        )
        raw_signature = data[4:]
        if len(raw_signature) != raw_signature_len:
            raise ValueError(
                f"Signature should have been {raw_signature_len}b, not {len(raw_signature)}b"
            )

        return cls(
            raw_version=raw_version,
            raw_log_key_id=raw_log_key_id,
            raw_timestamp=raw_timestamp,
            raw_extensions=raw_extensions,
            raw_hash_algorithm=raw_hash_algorithm,
            raw_signature_algorithm=raw_signature_algorithm,
            raw_signature=raw_signature,
        )

    @classmethod
    def _split_header(cls, data: bytes):
        """Pass."""
        header, data = cls._split_bytes(data, 2)
        header_len = header[1] ^ 0x80
        if header_len == 1:
            _, data = cls._split_bytes(data, 1)
        elif header_len == 2:
            _, data = cls._split_bytes(data, 2)
        else:
            raise ValueError(f"Unexpected header length {header_len}")

        len_struct, data = cls._split_len_struct(data=data)

        if len(data) != len_struct:
            raise ValueError(f"Data after headers should have been {len_struct}b, not {len(data)}b")

        return len_struct, data

    @classmethod
    def _split_sections(cls, data: bytes, len_data: int) -> Generator[bytes, None, None]:
        """Pass."""
        len_read = 0

        while len_read < len_data:
            len_struct, data = cls._split_len_struct(data=data)
            sct_data, data = cls._split_bytes(data, len_struct)
            len_read += len_struct + 2
            yield sct_data

    @staticmethod
    def _split_bytes(data: bytes, count: int) -> Tuple[bytes, bytes]:
        """Split data into (part1, part2) where part1 has count bytes."""
        if len(data) < count:
            raise ValueError(f"Expected {count} bytes, received only {len(data)}")
        return data[:count], data[count:]

    @classmethod
    def _split_len_struct(cls, data: bytes) -> Tuple[int, bytes]:
        """Pass."""
        len_packed, data = cls._split_bytes(data, 2)
        len_unpacked = struct.unpack("!H", len_packed)[0]
        return len_unpacked, data
