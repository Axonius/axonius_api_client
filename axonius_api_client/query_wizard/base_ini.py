#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import configparser
import pathlib
from typing import List, Union

from ..data_classes.wizard import Key, Sections
from ..tools import listify
from .base import QueryWizard


class QueryWizardIni(QueryWizard):
    SECTION_SKIPS_INI: List[str] = ["DEFAULT"]

    @classmethod
    def from_file(cls, path: Union[str, pathlib.Path], **kwargs):
        parser = configparser.ConfigParser()
        parser.read(path)
        kwargs["sections"] = cls._get_sections(parser=parser)
        kwargs["source"] = f"INI file at: {path}"
        return cls(**kwargs)

    @classmethod
    def from_str(cls, contents: str, **kwargs):
        parser = configparser.ConfigParser()
        parser.read_string(contents)
        kwargs["sections"] = cls._get_sections(parser=parser)
        kwargs["source"] = "INI string"
        return cls(**kwargs)

    @classmethod
    def _get_sections(cls, parser: configparser.ConfigParser) -> dict:
        sections = {
            name.lower().strip(): {k: v for k, v in section.items()}
            for name, section in parser.items()
            if name not in cls.SECTION_SKIPS_INI
        }
        return sections

    # XXX MAKE PRIVATE
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
            lines += [
                "",
                cls.doc_section_key(key=key.default),
                "",
            ]
        return "\n".join(lines)

    @staticmethod
    def doc_section_key(key: Key) -> str:
        # lines = [f"{key.key} = {example_over or key.example}"]
        lines = []
        fields = key.get_fields()

        for field in fields:
            if field.name.startswith("_"):
                continue

            human_name = field.name.replace("_", " ")
            pre = f"# {human_name:14}:"
            value = getattr(key, field.name)

            if field.name == "example":
                lines.append(f"{pre} {key.key} = {value}")
            elif isinstance(value, (list, tuple)):
                lines.append(pre)
                lines += [f"#    - {x}" for x in value]
            elif isinstance(value, dict):
                lines.append(f"# {human_name:14}:")
                for k, v in value.items():
                    v = ", ".join([str(x) for x in listify(v)])
                    lines.append(f"#    - {k}: {v}")
            else:
                lines.append(f"{pre} {value}")

        return "\n".join(lines)
