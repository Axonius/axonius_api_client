# -*- coding: utf-8 -*-
"""Tools for working with SSL certificate files."""

import contextlib
import socket
from typing import Generator, List, Union

import OpenSSL

from .convert import x509_to_der


def resolve_host(host: str) -> str:
    """Pass."""
    try:
        return socket.gethostbyname(host)
    except Exception as exc:
        msg = "Unable to resolve" if "nodename nor servname" in str(exc) else str(exc)
        raise ValueError(f"Failed to get hostname for host {host!r}: {msg}")


@contextlib.contextmanager
def get_cnx(host: str, port: int = 443) -> Generator[OpenSSL.SSL.Connection, None, None]:
    """Context manager to create an OpenSSL wrapped socket."""
    resolve_host(host=host)
    host = host.encode("utf-8")

    context = OpenSSL.SSL.Context(OpenSSL.SSL.TLS_METHOD)
    sock = socket.socket()

    cnx = OpenSSL.SSL.Connection(context, sock)
    cnx.set_tlsext_host_name(host)
    cnx.set_connect_state()
    cnx.connect((host, port))
    cnx.do_handshake()

    try:
        yield cnx
    finally:
        cnx.close()


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
