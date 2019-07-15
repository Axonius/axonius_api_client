# -*- coding: utf-8 -*-
"""Constants for this package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

MAX_PAGE_SIZE = 2000
""":obj:`int`: Maximum page size that REST API allows."""

DEFAULT_PAGE_SIZE = 1000
""":obj:`int`: Default page size to use for public API methods."""

GUI_PAGE_SIZES = [25, 50, 100]
""":obj:`list` of :obj:`int`: Valid page sizes for GUI paging."""

GENERIC_FIELD_PREFIX = "specific_data.data"
""":obj:`str`: Prefix that all generic fields should begin with."""

ADAPTER_FIELD_PREFIX = "adapters_data.{adapter_name}"
""":obj:`str`: Prefix that all adapter fields should begin with."""

LOG_REQUEST_ATTRS_BRIEF = [
    "request to {request.url!r}",
    "method={request.method!r}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: Request attributes to log when verbose=False."""

LOG_REQUEST_ATTRS_VERBOSE = [
    "request to {request.url!r}",
    "method={request.method!r}",
    "headers={request.headers}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: Request attributes to log when verbose=True."""

LOG_RESPONSE_ATTRS_BRIEF = [
    "response from {response.url!r}",
    "method={response.request.method!r}",
    "status={response.status_code!r}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: Response attributes to log when verbose=False."""

LOG_RESPONSE_ATTRS_VERBOSE = [
    "response from {response.url!r}",
    "method={response.request.method!r}",
    "headers={response.headers}",
    "status={response.status_code!r}",
    "reason={response.reason!r}",
    "elapsed={response.elapsed}",
    "size={size}",
]
""":obj:`list` of :obj:`str`: Response attributes to log when verbose=True."""
