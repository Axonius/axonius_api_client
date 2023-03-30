# -*- coding: utf-8 -*-
"""Tools for working with SSL certificate files."""
import enum
import logging
from typing import Any

LOG = logging.getLogger(__name__)


class Enum(enum.Enum):
    """Pass."""

    @classmethod
    def get_name_by_value(cls, value: Any) -> Any:
        """Pass."""
        for x in cls:
            if x.value == value:
                return x.name
        LOG.getChild(cls.__name__).debug(f"Unmappable {cls.__name__} value={value!r}")
        return None

    @classmethod
    def get_value_by_name(cls, value: Any) -> Any:
        """Pass."""
        for x in cls:
            if x.name == value:
                return x.value
        LOG.getChild(cls.__name__).debug(f"Unmappable {cls.__name__} value={value!r}")
        return None


class SctVersions(Enum):
    """Pass."""

    v1 = 0


class SignatureAlgorithms(Enum):
    """Pass."""

    anonymous = 0
    rsa = 1
    dsa = 2
    ecdsa = 3


class HashAlgorithms(Enum):
    """Pass."""

    NONE = 0
    MD5 = 1
    SHA1 = 2
    SHA224 = 3
    SHA256 = 4
    SHA384 = 5
    SHA512 = 6


class CertTypes(Enum):
    """Pass."""

    cert: str = "CERTIFICATE"
    csr: str = "CERTIFICATE REQUEST"
    pkcs7: str = "PKCS7"


class ChainTypes(Enum):
    """Pass."""

    server = "server/leaf/end-entity"
    is_ca = "intermediate/root CA"
    unknown = "unknown"
    csr = "signing request"
