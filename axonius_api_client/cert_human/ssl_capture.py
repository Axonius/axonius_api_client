# -*- coding: utf-8 -*-
"""Base example for setting up the API client."""
import logging
import sys
from typing import List, Optional

import OpenSSL
import urllib3.connectionpool
import urllib3.contrib.pyopenssl
import urllib3.poolmanager

LOG: logging.Logger = logging.getLogger(__name__)

INJECT_WITH_PYOPENSSL: bool = True

if sys.version_info >= (3, 10, 1):
    # get_verified_chain is mo' betta
    INJECT_WITH_PYOPENSSL: bool = False


class CaptureHTTPSResponse(urllib3.connectionpool.HTTPSConnectionPool.ResponseCls):
    """Pass."""

    def __init__(self, *args, **kwargs):
        """Pass."""
        super().__init__(*args, **kwargs)
        connection = getattr(self, "_connection", None)
        for attr in dir(connection):
            if attr.startswith("captured_"):
                setattr(self, attr, getattr(connection, attr))


class CaptureHTTPSConnection(urllib3.connectionpool.HTTPSConnectionPool.ConnectionCls):
    """Pass."""

    def set_captured_cert(self):
        """Pass."""
        logger = LOG.getChild(f"{self.__class__.__name__}")
        info = f"certificate from {self.sock}"
        logger.debug(f"Fetching {info}")

        # works with pyopenssl and ssl, python 3.9+ tested
        how = "n/a"
        if callable(getattr(self.sock, "getpeercert", None)):
            method = "self.sock.getpeercert(True)"
            logger.debug(f"Fetching {info} using method {method}")
            try:
                cert_bytes: bytes = self.sock.getpeercert(True)
            except Exception as exc:
                self.captured_cert_errors.append({"how": how, "method": method, "exc": exc})
                logger.exception(f"Failure fetching {info} using method {method}")
            else:
                self.captured_cert: OpenSSL.crypto.X509 = OpenSSL.crypto.load_certificate(
                    OpenSSL.crypto.FILETYPE_ASN1, cert_bytes
                )
                logger.debug(f"Fetched {info} using method {method}: {self.captured_cert}")
                return

        if not self.captured_cert:
            logger.error(f"Unable to fetch {info}")

    def set_captured_chain(self):
        """Pass."""
        logger = LOG.getChild(f"{self.__class__.__name__}")
        info = f"certificate chain from {self.sock}"
        logger.debug(f"Fetching {info}")

        if hasattr(self.sock, "_sslobj"):
            # only available on python 3.10.1+
            how = "python 3.10.1+"

            if callable(getattr(self.sock._sslobj, "get_verified_chain", None)):
                method = "self.sock._sslobj.get_verified_chain()"
                logger.debug(f"Fetching {info} using method {method}")
                try:
                    chain_ssl = self.sock._sslobj.get_verified_chain()
                    # List[_ssl.Certificate]
                except Exception as exc:
                    self.captured_chain_errors.append({"how": how, "method": method, "exc": exc})
                    logger.exception(f"Failure fetching {info} using method {method}")
                else:
                    self.captured_chain: List[OpenSSL.crypto.X509] = [
                        OpenSSL.crypto.load_certificate(
                            OpenSSL.crypto.FILETYPE_PEM, x.public_bytes()
                        )
                        for x in chain_ssl
                    ]
                    logger.debug(f"Fetched {info} using method {method}: {self.captured_chain}")
                    return

            if callable(getattr(self.sock._sslobj, "get_unverified_chain", None)):
                method = "self.sock._sslobj.get_unverified_chain()"
                logger.debug(f"Fetching {info} using method {method}")
                try:
                    chain_ssl = self.sock._sslobj.get_unverified_chain()
                    # List[_ssl.Certificate]
                except Exception as exc:
                    self.captured_chain_errors.append({"how": how, "method": method, "exc": exc})
                    logger.exception(f"Failure fetching {info} using method {method}")
                else:
                    self.captured_chain: List[OpenSSL.crypto.X509] = [
                        OpenSSL.crypto.load_certificate(
                            OpenSSL.crypto.FILETYPE_PEM, x.public_bytes()
                        )
                        for x in chain_ssl
                    ]
                    logger.debug(f"Fetched {info} using method {method}: {self.captured_chain}")
                    return

        if hasattr(self.sock, "connection"):
            # only available if pyopenssl has been injected into urllib3 via:
            how = "import urllib3.contrib.pyopenssl as m; m.inject_into_urllib3()"

            if callable(getattr(self.sock.connection, "get_peer_cert_chain", None)):
                method = "self.sock.connection.get_peer_cert_chain()"
                logger.debug(f"Fetching {info} using method {method}")
                try:
                    self.captured_chain: List[
                        OpenSSL.crypto.X509
                    ] = self.sock.connection.get_peer_cert_chain()
                except Exception as exc:
                    self.captured_chain_errors.append({"how": how, "method": method, "exc": exc})
                    logger.exception(f"Failure fetching {info} using method {method}")
                else:
                    logger.debug(f"Fetched {info} using method {method}: {self.captured_chain}")
                    return

        if not self.captured_chain:
            logger.error(f"Unable to fetch {info}")

    def connect(self):
        """Pass."""
        # force disable cert verification
        # self.cert_reqs = "CERT_NONE"

        self.captured_cert: Optional[OpenSSL.crypto.X509] = None
        self.captured_cert_errors: List[dict] = []

        self.captured_chain: Optional[List[OpenSSL.crypto.X509]] = None
        self.captured_chain_errors: List[dict] = []

        super().connect()
        self.set_captured_cert()
        self.set_captured_chain()


class CaptureHTTPSConnectionPool(urllib3.connectionpool.HTTPSConnectionPool):
    """Pass."""

    ConnectionCls = CaptureHTTPSConnection
    ResponseCls = CaptureHTTPSResponse


class Patches:
    """Pass."""

    https_pool = urllib3.poolmanager.pool_classes_by_scheme["https"]
    pyopenssl_injected: bool = False


def inject_into_urllib3(with_pyopenssl: bool = INJECT_WITH_PYOPENSSL):
    """Pass."""
    if with_pyopenssl:
        if Patches.pyopenssl_injected:
            LOG.debug("pyopenssl already patched into urllib3")
        else:
            urllib3.contrib.pyopenssl.inject_into_urllib3()
            Patches.pyopenssl_injected = True
            LOG.debug("pyopenssl patched into urllib3")

    if urllib3.poolmanager.pool_classes_by_scheme["https"] == CaptureHTTPSConnectionPool:
        LOG.debug(f"HTTPS pool class is already patched with {CaptureHTTPSConnectionPool}")
    else:
        Patches.https_pool = urllib3.poolmanager.pool_classes_by_scheme["https"]
        urllib3.poolmanager.pool_classes_by_scheme["https"] = CaptureHTTPSConnectionPool
        LOG.debug(f"HTTPS pool class patched with {CaptureHTTPSConnectionPool}")


def extract_from_urllib3(with_pyopenssl: bool = INJECT_WITH_PYOPENSSL):
    """Pass."""
    if with_pyopenssl:
        if Patches.pyopenssl_injected:
            urllib3.contrib.pyopenssl.extract_from_urllib3()
            Patches.pyopenssl_injected = False
            LOG.debug("pyopenssl unpatched from urllib3")
        else:
            LOG.debug("pyopenssl is not patched into urllib3")

    if urllib3.poolmanager.pool_classes_by_scheme["https"] == CaptureHTTPSConnectionPool:
        urllib3.poolmanager.pool_classes_by_scheme["https"] = Patches.https_pool
        LOG.debug(f"HTTPS pool class unpatched to {Patches.https_pool}")
    else:
        LOG.debug(f"HTTPS pool class is not patched with {CaptureHTTPSConnectionPool}")
