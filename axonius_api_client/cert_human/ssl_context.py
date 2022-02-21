# -*- coding: utf-8 -*-
"""Tools for working with SSL certificate files."""

import contextlib
import socket
from typing import Generator, List, Union

import OpenSSL


@contextlib.contextmanager
def get_cnx(host: str, port: int = 443) -> Generator[OpenSSL.SSL.Connection, None, None]:
    """Context manager to create an OpenSSL wrapped socket."""
    try:
        socket.gethostbyname(host)
    except Exception as exc:
        msg = "Unable to resolve" if "nodename nor servname" in str(exc) else str(exc)
        raise ValueError(f"Failed to get address info for host {host!r} port {port!r}: {msg}")

    context = OpenSSL.SSL.Context(OpenSSL.SSL.TLS_METHOD)
    sock = socket.socket()
    cnx = OpenSSL.SSL.Connection(context, sock)
    cnx.set_tlsext_host_name(host.encode("utf-8"))
    cnx.set_connect_state()
    cnx.connect((host, port))
    cnx.do_handshake()

    try:
        yield cnx
    finally:
        cnx.close()


def x509_to_der(
    value: Union[OpenSSL.crypto.X509, List[OpenSSL.crypto.X509]]
) -> Union[OpenSSL.crypto.X509, List[OpenSSL.crypto.X509]]:
    """Pass."""
    if isinstance(value, list):
        return [x509_to_der(value=x) for x in value]

    if not isinstance(value, OpenSSL.crypto.X509):
        raise TypeError(f"Supplied value must be type {OpenSSL.crypto.X509}, not {type(value)}")

    return OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, value)


def get_cert(
    host: str, port: int = 443, as_bytes: bool = True
) -> Union[bytes, OpenSSL.crypto.X509]:
    """Pass."""
    with get_cnx(host=host, port=port) as cnx:
        obj: OpenSSL.crypto.X509 = cnx.get_peer_certificate()
        return x509_to_der(value=obj) if as_bytes else obj


def get_chain(
    host: str, port: int = 443, as_bytes: bool = True
) -> List[Union[bytes, OpenSSL.crypto.X509]]:
    """Pass."""
    with get_cnx(host=host, port=port) as cnx:
        objs: List[OpenSSL.crypto.X509] = cnx.get_peer_cert_chain()
        return x509_to_der(value=objs) if as_bytes else objs
