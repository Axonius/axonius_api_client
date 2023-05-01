# -*- coding: utf-8 -*-
"""Base example for setting up the API client."""
import sys
import types
import typing as t
from typing import List, Optional

import OpenSSL
from urllib3 import connectionpool, poolmanager

INJECT_WITH_PYOPENSSL: bool = True

if sys.version_info >= (3, 10, 1):
    # get_verified_chain is mo' betta
    INJECT_WITH_PYOPENSSL: bool = False


class CaptureHTTPSResponse(connectionpool.HTTPSConnectionPool.ResponseCls):
    """Bring the captured_ attributes from the connection object down to the response object."""

    def __init__(self, *args, **kwargs):
        """Bring the captured_ attributes from the connection object down to the response object."""
        super().__init__(*args, **kwargs)
        connection = getattr(self, "_connection", None)
        self.captured_cert: Optional[OpenSSL.crypto.X509] = getattr(
            connection, "captured_cert", None
        )
        self.captured_chain: List[OpenSSL.crypto.X509] = getattr(connection, "captured_chain", [])
        self.captured_cert_errors: List[dict] = getattr(connection, "captured_cert_errors", [])
        self.captured_chain_errors: List[dict] = getattr(connection, "captured_chain_errors", [])


class CaptureHTTPSConnection(connectionpool.HTTPSConnectionPool.ConnectionCls):
    """Capture SSL certificates and save them as attributes on a connection object."""

    def capture_cert(self) -> t.Tuple[t.Optional[OpenSSL.crypto.X509], t.List[dict]]:
        """Capture the SSL certificate from the socket while it is open."""
        # works with pyopenssl and ssl, python 3.9+ tested
        sock = getattr(self, "sock", None)
        getpeercert = getattr(sock, "getpeercert", None)
        cert: t.Optional[OpenSSL.crypto.X509] = None
        errors: t.List[dict] = []

        if callable(getpeercert):
            how = f"certificate from {sock}"
            method = f"getpeercert={getpeercert}"
            try:
                cert_bytes: bytes = getpeercert(True)
                cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_bytes)
            except Exception as exc:
                errors.append({"how": how, "method": method, "exc": exc})
        return cert, errors

    def capture_chain(self) -> t.Tuple[t.List[OpenSSL.crypto.X509], t.List[dict]]:
        """Capture the SSL certificate chain from the socket while it is open."""
        sock = getattr(self, "sock", None)
        sslobj: t.Optional[t.Any] = getattr(sock, "_sslobj", None)
        connection: t.Optional[t.Any] = getattr(sock, "connection", None)

        get_verified_chain: t.Optional[callable] = getattr(sslobj, "get_verified_chain", None)
        get_unverified_chain: t.Optional[callable] = getattr(sslobj, "get_unverified_chain", None)
        get_peer_cert_chain: t.Optional[callable] = getattr(connection, "get_peer_cert_chain", None)

        info = [
            f"socket={sock}",
            f"sslobj={sslobj}",
            f"connection={connection}",
            f"get_verified_chain={get_verified_chain}",
            f"get_unverified_chain={get_unverified_chain}",
            f"get_peer_cert_chain={get_peer_cert_chain}",
        ]
        info = ", ".join(info)
        errors: t.List[dict] = []
        chain: t.List[OpenSSL.crypto.X509] = []

        if callable(get_verified_chain):
            # only available on python 3.10.1+
            how = f"python 3.10.1+ {info}"
            method = f"get_verified_chain={get_verified_chain}"
            try:
                chain = [
                    OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, x.public_bytes())
                    for x in get_verified_chain()
                ]
            except Exception as exc:
                errors.append({"how": how, "method": method, "exc": exc})

        if not chain and callable(get_unverified_chain):
            # only available on python 3.10.1+
            how = f"python 3.10.1+ {info}"
            method = f"get_unverified_chain={get_unverified_chain}"
            try:
                chain = [
                    OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, x.public_bytes())
                    for x in get_unverified_chain()
                ]
            except Exception as exc:
                errors.append({"how": how, "method": method, "exc": exc})

        if not chain and callable(get_peer_cert_chain):
            how = f"import urllib3.contrib.pyopenssl as m; m.inject_into_urllib3() {info}"
            method = f"get_peer_cert_chain={get_peer_cert_chain}"
            try:
                chain = [x for x in self.sock.connection.get_peer_cert_chain()]
            except Exception as exc:
                errors.append({"how": how, "method": method, "exc": exc})

        return chain, errors

    def __init__(self, *args, **kwargs):
        """Establish our capture attributes."""
        super().__init__(*args, **kwargs)
        self.captured_cert: Optional[OpenSSL.crypto.X509] = None
        self.captured_chain: List[OpenSSL.crypto.X509] = []
        self.captured_cert_errors: List[dict] = []
        self.captured_chain_errors: List[dict] = []

    def connect(self):
        """Connect as usual, but then capture the SSL certificate & chain."""
        # how to force disable cert verification
        # self.cert_reqs = "CERT_NONE"
        super().connect()
        self.captured_cert, self.captured_cert_errors = self.capture_cert()
        self.captured_chain, self.captured_chain_errors = self.capture_chain()


class CaptureHTTPSConnectionPool(connectionpool.HTTPSConnectionPool):
    """Pool manager used when capturing certificates."""

    ConnectionCls = CaptureHTTPSConnection
    ResponseCls = CaptureHTTPSResponse


class Patches:
    """State tracker to know what has been patched."""

    https_pool = poolmanager.pool_classes_by_scheme["https"]
    pyopenssl_injected: bool = False


def import_pyopenssl() -> t.Optional[types.ModuleType]:
    """Import pyopenssl if it is available."""
    try:
        import urllib3.contrib.pyopenssl

        return urllib3.contrib.pyopenssl
    except ImportError:
        return None


def import_pyopenssl_and_call(
    func: str, reasons: t.Optional[t.List[str]] = None
) -> t.Tuple[bool, t.List[str]]:
    """Import pyopenssl and call the given function."""
    performed: bool = False
    reasons: t.List[str] = reasons if isinstance(reasons, list) else []
    pyopenssl = import_pyopenssl()
    if pyopenssl:
        _func = getattr(pyopenssl, func, None)
        if callable(_func):
            try:
                ret = _func()
                performed = True
                reasons.append(f"pyopenssl.{func}() returned: {ret!r}")
            except Exception as exc:
                reasons.append(f"pyopenssl.{func}() failed: {exc}")
        else:
            reasons.append(f"pyopenssl.{func}() not callable")
    else:
        reasons.append("pyopenssl not available")
    return performed, reasons


def inject_into_urllib3(with_pyopenssl: bool = INJECT_WITH_PYOPENSSL) -> t.Tuple[bool, t.List[str]]:
    """Apply the cert capturing patch to urllib."""
    performed: bool = False
    reasons: t.List[str] = []
    if with_pyopenssl:
        if Patches.pyopenssl_injected:
            reasons.append("pyopenssl already patched into urllib3")
        elif not INJECT_WITH_PYOPENSSL:
            reasons.append("pyopenssl on 3.10.1+ not needed")
        else:
            performed, reasons = import_pyopenssl_and_call(
                func="inject_into_urllib3", reasons=reasons
            )

    if poolmanager.pool_classes_by_scheme["https"] == CaptureHTTPSConnectionPool:
        reasons.append(f"HTTPS pool class is already patched with {CaptureHTTPSConnectionPool}")
    else:
        Patches.https_pool = poolmanager.pool_classes_by_scheme["https"]
        performed = True
        poolmanager.pool_classes_by_scheme["https"] = CaptureHTTPSConnectionPool
        reasons.append(f"HTTPS pool class patched with {CaptureHTTPSConnectionPool}")
    return performed, reasons


def extract_from_urllib3(
    with_pyopenssl: bool = INJECT_WITH_PYOPENSSL,
) -> t.Tuple[bool, t.List[str]]:
    """Remove the cert capturing patch from urllib."""
    performed: bool = False
    reasons: t.List[str] = []

    if with_pyopenssl:
        if Patches.pyopenssl_injected:
            performed, reasons = import_pyopenssl_and_call(
                func="extract_from_urllib3", reasons=reasons
            )
        elif not INJECT_WITH_PYOPENSSL:
            reasons.append("pyopenssl on 3.10.1+ not needed")
        else:
            reasons.append("pyopenssl is not patched into urllib3")

    if poolmanager.pool_classes_by_scheme["https"] == CaptureHTTPSConnectionPool:
        poolmanager.pool_classes_by_scheme["https"] = Patches.https_pool
        reasons.append(f"HTTPS pool class unpatched to {Patches.https_pool}")
        performed = True
    else:
        reasons.append(f"HTTPS pool class is not patched with {CaptureHTTPSConnectionPool}")
    return performed, reasons
