# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""


def load_der(value: bytes):
    """Load the bytes DER cert file into a python object."""
    import OpenSSL

    return OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, value)


def der_to_pem(der):
    """Convert a binary bytes DER cert to ascii PEM cert."""
    import OpenSSL

    return OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, der)
