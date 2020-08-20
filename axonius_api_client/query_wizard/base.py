#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import logging

from ..api.assets.asset_mixin import AssetMixin
from ..constants import LOG_LEVEL_WIZARD
from ..data_classes.wizard import Section, Sections
from ..exceptions import ApiError, NotFoundError
from ..logs import get_obj_log
from ..tools import check_empty, check_type
from .section_parser import SectionParser


class QueryWizard:
    def __init__(
        self, apiobj: AssetMixin, sections: dict, **kwargs,
    ):
        log_level: str = kwargs.get("log_level", LOG_LEVEL_WIZARD)
        source: str = kwargs.get("source", "dict")
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)

        check_type(value=sections, name="sections", exp=dict)
        sections = {
            k.lower().strip(): v for k, v in sections.items() if k.lower().strip()
        }
        check_empty(value=sections, name="sections")

        self.apiobj: AssetMixin = apiobj
        self.parsed: dict = {}
        self.unparsed: dict = sections

        self.LOG.debug(f"Loaded {len(self.unparsed)} sections from {source}")

    def parse(self, name: str, parent: str = "", idx: int = 0) -> dict:
        name = name.lower()

        if name in self.parsed:
            return self.parsed[name]

        if name not in self.unparsed:
            valid = "\n  - " + "\n  - ".join(list(self.unparsed))
            err = f"Section named {name!r} not found, valid sections: {valid}"
            raise NotFoundError(err)

        unparsed = self.unparsed[name]
        parser = SectionParser(wizard=self)
        parsed = parser(name=name, section=unparsed, parent=parent, idx=idx)
        self.parsed[name] = parsed
        return parsed

    def parse_all(self) -> dict:
        for name in self.unparsed:
            self.parse(name=name)
        return self.parsed

    @staticmethod
    def _get_section_type(name: str) -> Section:
        try:
            return getattr(Sections, name)
        except AttributeError:
            valid = ", ".join([x.name for x in Sections.get_fields()])
            raise ApiError(f"Invalid section type {name!r}, valid types: {valid}")

    @property
    def _fields_map(self):
        if not hasattr(self, "_fields_map_data"):
            self._fields_map_data = self.apiobj.fields.get()
        return self._fields_map_data
