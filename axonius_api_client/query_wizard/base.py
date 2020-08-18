#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import logging
from typing import List, Optional, Union

from ..api.assets.asset_mixin import AssetMixin
from ..constants import LOG_LEVEL_WIZARD
from ..data_classes.wizard import (EXTERNAL_REFS, ExprTemplates, Keys, Section,
                                   Sections)
from ..exceptions import ApiError, NotFoundError
from ..logs import get_obj_log
from ..tools import check_empty, check_type, get_or_flag
from .section_parser import SectionParser

# XXX Csv reader?


class QueryWizard:
    def __init__(
        self, apiobj: AssetMixin, log_level: Union[int, str] = LOG_LEVEL_WIZARD,
    ):
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        """:obj:`logging.Logger`: Logger for this object."""

        self.apiobj: AssetMixin = apiobj
        self.sections: dict = {}
        self.parsed: dict = {}
        self.unparsed: dict = {}

    def from_dict(self, sections: dict):
        check_type(value=sections, name="sections", exp=dict)
        check_empty(value=sections, name="sections")
        return self.parse_sections(sections=sections)

    def parse_sections(self, sections: dict) -> dict:
        self.unparsed = {k.lower().strip(): v for k, v in sections.items()}
        self.parsed = {}
        for name, section in self.unparsed.items():
            self._parse_section(name=name)
        return self.parsed

    def parse_expression(
        self,
        value: Union[List[str], str],
        reference_types: Optional[List[str]] = None,
        parent_name: Optional[str] = None,
    ) -> dict:
        reference_types = reference_types or EXTERNAL_REFS
        exprs = self._parse_expression(
            value=value, reference_types=reference_types, parent_name=parent_name
        )
        aqls = ""

        for expr in exprs:
            section = self.parsed[expr["name"]]
            aql = section["aql"].strip()
            not_flag = section.get(Keys.not_flag.key, False)

            if not_flag:
                aql = ExprTemplates.not_text + aql

            if aqls:
                if expr["or_flag"]:
                    aql = ExprTemplates.or_text + aql
                else:
                    aql = ExprTemplates.and_text + aql

            aqls += aql

        self.LOG.info(f"AQL produced: {aqls}")
        value = {"aql": aqls, "sections": exprs}
        return value

    @property
    def _fields_map(self):
        if not hasattr(self, "_fields_map_data"):
            self._fields_map_data = self.apiobj.fields.get()
        return self._fields_map_data

    def _parse_section(self, name: str) -> dict:
        name = name.lower()

        if name in self.parsed:
            return self.parsed[name]

        if name not in self.unparsed:
            valid = "\n  - " + "\n  - ".join(list(self.unparsed))
            err = f"Section named {name!r} not found, valid sections: {valid}"
            raise NotFoundError(err)

        parser = SectionParser(wizard=self)
        parsed = parser(name=name, section=self.unparsed[name])
        self.parsed[name] = parsed
        return parsed

    def _parse_expression(
        self,
        value: List[str],
        reference_types: List[str],
        parent_name: Optional[str] = None,
    ) -> List[dict]:
        if isinstance(value, str):
            value = [x.strip() for x in value.split(",") if x.strip()]

        check_type(value=value, exp=list, exp_items=str)
        check_empty(value=value)

        parsed = []

        for item in value:
            item, or_flag = get_or_flag(item=item)

            if parent_name and item == parent_name:
                raise ApiError(f"Invalid reference to own section name: {item!r}")

            item_section = self._parse_section(name=item)
            item_type = item_section[Keys.section_type.key]

            if item_type not in reference_types:
                valid = "\n - " + "\n - ".join(reference_types)
                msg = (
                    f"Invalid reference to section {item!r} of type {item_type!r}, "
                    f"valid reference types:{valid}"
                )
                raise ApiError(msg)

            item_parsed = {"or_flag": or_flag, "name": item}
            parsed.append(item_parsed)

        return parsed

    @staticmethod
    def _get_section_type(name: str) -> Section:
        try:
            return getattr(Sections, name)
        except AttributeError:
            valid = ", ".join([x.name for x in Sections.get_fields()])
            raise ApiError(f"Invalid section type {name!r}, valid types: {valid}")
