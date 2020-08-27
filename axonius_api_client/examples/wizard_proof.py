#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import os

import axonius_api_client as axonapi  # noqa:F401
from axonius_api_client.connect import Connect
from axonius_api_client.constants import load_dotenv

# from axonius_api_client.data_classes import wizard
from axonius_api_client.query_wizard import Wizard, WizardText
from axonius_api_client.tools import json_reload

# from shlex import shlex
# from typing import List


def jdump(obj, **kwargs):
    """JSON dump utility."""
    print(json_reload(obj, **kwargs))


if __name__ == "__main__":
    load_dotenv()

    AX_URL = os.environ["AX_URL"]
    AX_KEY = os.environ["AX_KEY"]
    AX_SECRET = os.environ["AX_SECRET"]

    ctx = Connect(
        url=AX_URL,
        key=AX_KEY,
        secret=AX_SECRET,
        certwarn=False,
        log_console=True,
        # log_level_console="info",
    )

    # ctx.start()

    devices = ctx.devices
    # users = ctx.users
    j = jdump
    # ini_dir = get_path(__file__).parent
    # ini_file = "wizard_proof.ini"
    # ini_path = ini_dir / ini_file
    # wizard = QueryWizardIni.from_file(apiobj=devices, path=ini_path)
    # final = wizard.parse("combo1")
    # print(final["value"]["aql"])

'''
# OPERATOR = "operator"
# ADAPTER = "adapter"
# FIELD = "field"
# VALUE = "value"
# LOGICAL = "logical"
TYPE = "type"
SUBS = "subs"
IDX = "source_line_idx"
LINE = "source_line"
SOURCE = "source"
# DEFAULT_OP_NO_VALUE = "exists"
# DEFAULT_OP_VALUE = "equals"
# DEFAULT_LOGICAL = "and"
# LOGICALS = ["and", "or", "and_not", "or_not"]
# DEFAULT_ADAPTER = "agg"


class ExprStrTypes:
    simple: str = "simple"
    start_complex: str = "complex"
    stop_complex: str = ""
    start_bracket: str = "bracket"
    stop_bracket: str = ""


class ExprParse:
    ITEM_SEP: str = ","
    VALUE_SEP: str = "="
    TYPES = ["simple", "start_complex", "stop_complex", "start_bracket", "stop_bracket"]
    DEFAULT_TYPE = "simple"

    def __init__(self, **kwargs):
        pass

    def from_text(self, text: str, source: str = "text"):
        self._text: str = text
        self._source: str = source
        self._lines: List[str] = text.splitlines()
        self.exprs: List[dict] = []
        self._bracket_idx: int = None
        self._bracket_obj: dict = None
        self._complex_idx: int = None
        self._complex_obj: dict = None

        for idx, line in enumerate(self._lines):
            expr = {}
            expr[LINE] = line
            expr[IDX] = idx

            try:
                self._parse(expr=expr)
            except Exception as exc:
                msg = [
                    f"Error while parsing expression from {source}",
                    f"Line number: {idx + 1}",
                    f"Line text: {line}",
                    f"Error: {exc}",
                ]
                raise Exception("\n".join(msg))

        return self.exprs

    def _parse(self, expr: dict) -> dict:
        """Parse key-value pairs from a shell-like text."""
        text = expr[LINE].lstrip()
        has_content = False

        if not text or text.startswith("#"):
            return

        if self.VALUE_SEP not in text:
            raise Exception(f"Missing separator {self.VALUE_SEP!r}")

        lexer = shlex(text, posix=True)
        lexer.whitespace = self.ITEM_SEP
        lexer.wordchars += self.VALUE_SEP

        for word in lexer:
            value = word.split(self.VALUE_SEP, maxsplit=1)
            key = value.pop(0).strip().lower()

            if not all([key, value]):
                continue

            has_content = True
            expr[key] = value.pop()

        if has_content:
            if TYPE not in expr:
                expr_type = self.DEFAULT_TYPE
            else:
                expr_type = expr[TYPE]

            expr_method = getattr(self, f"_handle_{expr_type}", None)

            if not expr_method:
                valid = "\n - " + "\n - ".join(self.TYPES)
                raise Exception(f"Invalid type {expr_type!r}, valid types:{valid}")

            expr_method(expr=expr)
        return expr

    def _handle_simple(self, expr: dict):
        if self._complex_obj:
            self._complex_obj[SUBS].append(expr)
        elif self._bracket_obj:
            expr[TYPE] = "simple"
            self._bracket_obj[SUBS].append(expr)
        else:
            self.exprs.append(expr)

    def _handle_start_complex(self, expr: dict):
        err = "Can not start a new complex section"
        if self._complex_obj:
            idx = self._complex_idx + 1
            raise Exception(f"{err}, complex section started on line {idx}")

        expr[SUBS] = []
        expr[TYPE] = "complex"
        self._complex_idx = expr[IDX]
        self._complex_obj = expr

        if isinstance(self._bracket_idx, int):
            self._bracket_obj[SUBS].append(expr)
        else:
            self.exprs.append(expr)

    def _handle_stop_complex(self, expr: dict):
        err = "Can not stop a complex section"
        if not self._complex_obj:
            raise Exception(f"{err}, not in a complex section")

        self._complex_obj = None
        self._complex_idx = None

    def _handle_start_bracket(self, expr: dict):
        err = "Can not start new bracket section"
        if self._bracket_obj:
            idx = self._bracket_idx + 1
            raise Exception(f"{err}, bracket section started on line {idx}")

        if self._complex_obj:
            idx = self._complex_idx + 1
            raise Exception(f"{err}, complex section started on line {idx}")

        expr[TYPE] = "bracket"
        expr[SUBS] = []
        self._bracket_idx = expr[IDX]
        self._bracket_obj = expr
        self.exprs.append(expr)

    def _handle_stop_bracket(self, expr: dict):
        err = "Can not stop a bracket section"
        if not self._bracket_obj:
            raise Exception(f"{err}, not in a bracket section")

        self._bracket_obj = None
        self._bracket_idx = None


TEXT = """
type=stop_comxplex
type=start_complex, logical=and, field=installed_software
    field=name, operator=equals, value="Google Chrome"
    field=version, operator=less_than, value=99
type=stop_complex
# test1
type=start_bracket
    logical=and_not, field=last_seen, operator=last_hours, value=24
    type=simple, logical=and, field=os_type, operator=equals, value=Windows
    # test2
    type=start_complex, logical=and, field=installed_software
        field=name, operator=in, value="Google Chrome, xyz"
        field=version, operator=less_than, value=99
    type=stop_complex
type=stop_bracket
"""
# TEXT = """
# field=last_seen
# """

parser = ExprParse()
exprs = parser.from_text(text=TEXT)
j(exprs)
'''
TEXT = """
type = START_COMPLEX, logical = and, field=installed_software
    field=name, operator=equals, value="Google Chrome"
    field=version, operator=less_than, value=99
type=stop_complex
# test1
type=start_bracket
    logical=and_not, field=last_seen, operator=last_hours, value=24
    logical=and, field=os_type, operator=equals, value=Windows
    # test2
    type=start_complex, logical=and, field=installed_software
        field=name, operator=in, value="Google Chrome, xyz"
        field=version, operator=less_than, value=99
    type=stop_complex
type=stop_bracket
"""
text_wizard = WizardText()
exprs = text_wizard.from_path(path="/tmp/blah.txt")
wizard = Wizard(apiobj=devices)
exprs = wizard.parse(exprs=exprs, source=text_wizard.source)
