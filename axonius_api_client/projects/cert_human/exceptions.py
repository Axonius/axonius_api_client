# -*- coding: utf-8 -*-
"""Tools for working with SSL certificate files."""


class CertHumanError(Exception):
    """Pass."""


class PathError(ValueError, CertHumanError):
    """Pass."""


class PathNotFoundError(PathError):
    """Pass."""


class InvalidCertError(CertHumanError):
    """Pass."""

    def __init__(self, reason: str, store):
        """Pass."""
        self.reason: str = reason
        self.store = store

        items = [f"Invalid Certificate: {store}", f"Invalid Certificate reason: {reason}"]
        msgs = [*items, "", store.to_str(), "", *items]
        super().__init__("\n".join(msgs))
