# -*- coding: utf-8 -*-
"""Authenticating with Axonius."""
from .api_key import AuthApiKey
from .credentials import AuthCredentials
from .model import AuthModel
from .null import AuthNull

# backwards compatibility
ApiKey = AuthApiKey
Credentials = AuthCredentials


__all__ = (
    "AuthModel",
    "AuthApiKey",
    "AuthCredentials",
    "AuthNull",
    "ApiKey",
    "Credentials",
)
