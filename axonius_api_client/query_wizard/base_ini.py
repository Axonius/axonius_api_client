#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import configparser
import pathlib
from typing import List, Optional, Union

from ..data_classes.wizard import Key, KeyNames, Sections
from ..tools import listify
from .base import QueryWizard


class QueryWizardIni(QueryWizard):
    SECTION_SKIPS_INI: List[str] = ["DEFAULT"]

    def from_file(self, path: Union[str, pathlib.Path]):
        self.parser = configparser.ConfigParser()
        self.parser.read(path)
        sections = self._get_sections_ini(parser=self.parser)
        return self.from_dict(sections=sections)

    def from_str(self, contents: str):
        self.parser = configparser.ConfigParser()
        self.parser.read_string(contents)
        sections = self._get_sections_ini(parser=self.parser)
        return self.from_dict(sections=sections)

    def _get_sections_ini(self, parser) -> dict:
        sections = {
            name.lower().strip(): {k: v for k, v in section.items()}
            for name, section in parser.items()
            if name not in self.SECTION_SKIPS_INI
        }
        self.LOG.debug(f"Parsed {len(sections)} sections from INI file")
        return sections

    @classmethod
    def doc_sections(cls):
        lines = []
        sections = Sections.get_fields()
        for section in sections:
            lines += [
                "#" * 60,
                f"# Section type: {section.name}",
                "#" * 60,
                cls.doc_section_type(name=section.name),
                "",
            ]

        return "\n".join(lines)

    @classmethod
    def doc_section_type(cls, name: str):
        lines = []
        section = cls._get_section_type(name=name)
        for key in section.get_fields():
            example_over = None
            key_name = key.key
            if key_name == KeyNames.section_type:
                example_over = section.__name__
            lines += [
                "",
                cls.doc_section_key(key=key.default, example_over=example_over),
                "",
            ]
        return "\n".join(lines)

    @staticmethod
    def doc_section_key(key: Key, example_over: Optional[str] = None) -> str:
        lines = [f"{key.key} = {example_over or key.example}"]
        fields = key.get_fields()

        skips = [
            # KeyNames.SECTION_NAME,
            "example",
            # KeyTypeNames.KEY.name,
        ]
        for field in fields:
            if field.name.startswith("_") or field.name in skips:
                continue

            human_name = field.name.replace("_", " ")
            value = getattr(key, field.name)

            if isinstance(value, (list, tuple)):
                lines.append(f"# {human_name:14}:")
                lines += [f"#    - {x}" for x in value]
            elif isinstance(value, dict):
                lines.append(f"# {human_name:14}:")
                for k, v in value.items():
                    v = ", ".join([str(x) for x in listify(v)])
                    lines.append(f"#    - {k}: {v}")
            else:
                lines.append(f"# {human_name:14}: {value}")

        return "\n".join(lines)
