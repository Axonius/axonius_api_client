# -*- coding: utf-8 -*-
"""Axonius API Client HTTP errors."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .. import exceptions


class HttpError(exceptions.PackageError):
    """Parent exception for all Authentication errors."""
