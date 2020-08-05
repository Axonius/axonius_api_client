#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import configparser
from typing import IO

from axonius_api_client.constants import NO, YES
from axonius_api_client.exceptions import ApiError, ToolsError
from axonius_api_client.tools import coerce_bool


def crjoin(obj):
    return "#    " + "\n#    ".join([str(x) for x in obj])


def commajoin(obj):
    return ", ".join(sorted(list(set([str(x).lower() for x in obj]))))


INVALID_ERR = "invalid value {value!r}".format
MISSING_ERR = "missing required key".format

SECTION_KEY = "section"
BOOL_VALIDS = [f"True: {commajoin(YES)}", f"False: {commajoin(NO)}"]

FIELD_KEY = "field"
FIELD_REQUIRED = True
FIELD_FALLBACK = None
FIELD_TYPE = "string as 'adapter:field'"
FIELD_DESCRIPTION = "field name to use with 'operator' on 'value'"
FIELD_DOC = f"""
# key: {FIELD_KEY}
# type: {FIELD_TYPE}
# required: {FIELD_REQUIRED}
# default: {FIELD_FALLBACK}
# description: {FIELD_DESCRIPTION}
"""

VALUE_KEY = "value"
VALUE_REQUIRED = False
VALUE_FALLBACK = None
VALUE_TYPE = "dependent on operator"
VALUE_DESCRIPTION = (
    "value to use for 'operator' against 'field', required for certain operators"
)
VALUE_DOC = f"""
# key: {VALUE_KEY}
# required: {VALUE_REQUIRED}
# type: {VALUE_TYPE}
# default: {VALUE_FALLBACK}
# description: {VALUE_DESCRIPTION}
"""

TYPE_KEY = "type"
TYPE_REQUIRED = False
TYPE_FALLBACK = "simple"
TYPE_TYPE = "choice of strings"
TYPE_DESCRIPTION = "section type"
TYPE_VALIDS = ["simple", "complex", "nested"]
TYPE_DOC = f"""
# key: {TYPE_KEY}
# required: {TYPE_REQUIRED}
# type: {TYPE_TYPE}
# default: {TYPE_FALLBACK}
# description: {TYPE_DESCRIPTION}
# valid choices:
{crjoin(TYPE_VALIDS)}
"""

DATE = "date"
IPADDRESS = "ipaddress"
SUBNET = "subnet"
VERSION = "version"
TAG = "tag"
STRING = "string"
NUMERIC = "numeric"
IMAGE = "image"
ARRAY = "array"

EQUALS = "equals"
EXISTS = "exists"
LESS_THAN = "less_than"
MORE_THAN = "more_than"
NEXT_HOURS = "next_hours"
LAST_HOURS = "last_hours"
IN = "in"
IN_SUBNET = "in_subnet"
IS_IPV6 = "is_ipv6"
IS_IPV4 = "is_ipv4"
REGEX = "regex"

OPERATOR_KEY = "operator"
OPERATOR_REQUIRED = False
OPERATOR_FALLBACK = "exists"
OPERATOR_DESCRIPTION = "operator to use for 'value' against 'field'"
OPERATOR_TYPE = "choice of strings"
OPERATOR_VALIDS = {
    EQUALS: [DATE, IPADDRESS, SUBNET, VERSION, TAG, STRING, ARRAY, NUMERIC],
    EXISTS: [DATE, IPADDRESS, SUBNET, VERSION, ARRAY, TAG, IMAGE, STRING, NUMERIC],
    LESS_THAN: [DATE, VERSION, NUMERIC, ARRAY],
    MORE_THAN: [DATE, VERSION, NUMERIC, ARRAY],
    NEXT_HOURS: [DATE],
    LAST_HOURS: [DATE],
    IN: [STRING, IPADDRESS, SUBNET, VERSION, NUMERIC, TAG],
    IN_SUBNET: [IPADDRESS],
    IS_IPV4: [IPADDRESS],
    IS_IPV6: [IPADDRESS],
    REGEX: [IPADDRESS, STRING, SUBNET, VERSION, TAG],
}
OPERATOR_DOC = f"""
# key: {OPERATOR_KEY}
# required: {OPERATOR_REQUIRED}
# type: {OPERATOR_TYPE}
# default: {OPERATOR_FALLBACK}
# description: {OPERATOR_DESCRIPTION}
# valid choices:
{crjoin(OPERATOR_VALIDS)}
"""

NOT_KEY = "not"
NOT_REQUIRED = False
NOT_FALLBACK = "false"
NOT_DESCRIPTION = (
    "only match assets where the 'operator' does not match 'value' for 'field'"
)
NOT_TYPE = "boolean"
NOT_VALIDS = BOOL_VALIDS
NOT_DOC = f"""
# key: {NOT_KEY}
# required: {NOT_REQUIRED}
# type: {NOT_TYPE}
# default: {NOT_FALLBACK}
# description: {NOT_DESCRIPTION}
# valid values:
{crjoin(NOT_VALIDS)}
"""


class QueryFilterKeyError(ApiError):
    def __init__(self, query_filter, key, msg, doc=None):
        doc = f"\nKey documentation:\n{doc}" if doc else ""
        self.query_filter = query_filter
        self.name = query_filter.name
        self.key = key
        self.msg = msg
        self.doc = doc

        super().__init__(
            f"Error in filter section {self.name!r} with key {key!r}: {msg}{doc}"
        )


class QueryFilter:
    def __init__(self, query_ini, apiobj=None):
        self.query_ini = query_ini
        self.apiobj = apiobj

    def __call__(self, name):
        self.name = name
        self.section = self.query_ini.parser[name]
        self.type_method = getattr(self, f"do_{self.filter_type}")
        return self.type_method()

    def get_key(
        self, key, fallback=None, required=False, lower=True, strip=True, doc=None,
    ):
        if required and key not in self.section:
            raise QueryFilterKeyError(
                query_filter=self, key=key, msg=MISSING_ERR(), doc=doc,
            )

        value = self.section.get(option=key, fallback=fallback)

        if isinstance(value, str):
            if lower:
                value = value.lower()

            if strip:
                value = value.strip()

        return value

    def get_key_enum(self, key, valids, doc=None, fallback=None, required=False):
        value = self.get_key(
            key=key, fallback=fallback, required=required, lower=True, strip=True,
        )

        if value not in valids:
            raise QueryFilterKeyError(
                query_filter=self, key=key, msg=INVALID_ERR(value=value), doc=doc,
            )

        return value

    def get_key_bool(self, key, doc=None, fallback=None, required=False):
        value = self.get_key(
            key=key, fallback=fallback, required=required, lower=True, strip=True,
        )

        try:
            value = coerce_bool(obj=value)
        except ToolsError:
            raise QueryFilterKeyError(
                query_filter=self, key=key, msg=INVALID_ERR(value=value), doc=doc,
            )

        return value

    @property
    def filter_type(self):
        return self.get_key_enum(
            key=TYPE_KEY, fallback=TYPE_FALLBACK, valids=TYPE_VALIDS, doc=TYPE_DOC
        )

    @property
    def operator_not(self):
        return self.get_key_bool(
            key=NOT_KEY, fallback=NOT_FALLBACK, required=NOT_REQUIRED, doc=NOT_DOC
        )

    @property
    def operator(self):
        return self.get_key_enum(
            key=OPERATOR_KEY,
            fallback=OPERATOR_FALLBACK,
            valids=OPERATOR_VALIDS,
            required=OPERATOR_REQUIRED,
            doc=OPERATOR_DOC,
        )

    @property
    def operator_value(self):
        return self.get_key(
            key=VALUE_KEY,
            required=VALUE_REQUIRED,
            lower=False,
            strip=False,
            doc=VALUE_DOC,
        )

    @property
    def field(self):
        return self.get_key(
            key=FIELD_KEY, required=FIELD_REQUIRED, lower=True, strip=True, doc=FIELD_DOC
        )

    def do_simple(self):
        return {
            SECTION_KEY: self.name,
            NOT_KEY: self.operator_not,
            OPERATOR_KEY: self.operator,
            VALUE_KEY: self.operator_value,
            FIELD_KEY: self.field,
        }

    def do_nested(self):
        pass

    def do_complex(self):
        pass


class QueryIni:

    SKIPS = ["DEFAULT"]

    def __init__(self):
        self.parser = configparser.ConfigParser()

    def __call__(self, fh: IO) -> dict:
        self.parser.read_file(fh)
        parsed = []
        query_filter = QueryFilter(query_ini=self)

        for section in self.parser:
            if section in self.SKIPS:
                continue

            parsed.append(query_filter(name=section))
        return parsed


query_ini = QueryIni()
parsed = query_ini(fh=open("test.ini"))
