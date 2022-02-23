# -*- coding: utf-8 -*-
"""Tools for working with SSL certificate files."""


class CertHumanError(Exception):
    """Pass."""


class PathError(ValueError, CertHumanError):
    """Pass."""


class PathNotFoundError(PathError):
    """Pass."""
