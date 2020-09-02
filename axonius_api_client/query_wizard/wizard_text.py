# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import logging
import shlex
from typing import List, Union

from ..constants import LOG_LEVEL_WIZARD
from ..data_classes.wizard import ExprKeys, TextTypes
from ..exceptions import WizardError
from ..logs import get_obj_log
from ..tools import check_empty, check_type, join_kv, path_read


def kv_dump(obj):
    return "\n  ".join(join_kv(obj))


class WizardText:
    ITEM_SEP: str = ","
    VALUE_SEP: str = "="
    WORDCHARS: str = f"{VALUE_SEP}: "
    DEFAULT_TYPE: str = TextTypes.simple.name_text

    def __init__(
        self, log_exprs: bool = False, log_level: Union[str, int] = LOG_LEVEL_WIZARD
    ):
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        self._expr_bracket: dict = {}
        self._expr_complex: dict = {}
        self.exprs: List[dict] = []
        self._log_exprs: bool = log_exprs
        self._expr_log = self.LOG.debug if log_exprs else lambda x: x

    def from_text(self, content: str, source: str = "text string"):
        check_type(value=content, exp=str, name="content")
        check_empty(value=content, name="content")
        self._expr_bracket: dict = {}
        self._expr_complex: dict = {}
        self.exprs: List[dict] = []

        lines: List[str] = content.splitlines()

        self.LOG.info(f"Parsing {len(lines)} lines from {source}")

        for idx, line in enumerate(lines):
            line_num = idx + 1
            src = f"from {source} line #{line_num}: {line!r}"
            try:
                expr = self._parse_line(line=line)
                self._expr_log(f"Split line into expr {src}\n{kv_dump(expr)}")

                if not expr:
                    continue

                expr[ExprKeys.IDX] = idx
                expr[ExprKeys.SRC] = src
                self._parse_expr(expr=expr)
                self._expr_log(f"Parsed expr {src}\n{kv_dump(expr)}")

            except Exception as exc:
                raise WizardError(f"Error parsing {src}\n{exc}")

        if not self.exprs:
            raise WizardError(
                f"No expressions parsed from {source} with content:\n{content}"
            )
        self.LOG.info(f"Parsed {len(self.exprs)} expressions from {source}")

        return self.exprs

    def from_path(self, path):
        path, content = path_read(obj=path)
        return self.from_text(content=content, source=f"text file {path}")

    def _parse_line(self, line: str) -> dict:
        """Parse key-value pairs from a shell-like text."""
        line = line.strip()
        expr = {}

        if not line or line.startswith("#"):
            self.LOG.debug("Skipping empty or comment line")
            return expr

        if self.VALUE_SEP not in line:
            raise WizardError(f"Missing separator {self.VALUE_SEP!r}")

        lexer = shlex.shlex(line, posix=True)
        lexer.whitespace = self.ITEM_SEP
        lexer.wordchars += self.WORDCHARS

        for word in lexer:
            value = word.split(self.VALUE_SEP, maxsplit=1)
            key = value.pop(0).strip().lower()

            value = value.pop().lstrip()

            if not value.strip():
                self.LOG.debug(f"Empty value {value!r} in word {word!r}")
                continue

            if not key:
                self.LOG.debug(f"Empty key {key!r} in word {word!r}")
                continue

            expr[key] = value

        return expr

    def _parse_expr(self, expr: dict):
        expr_type = expr.pop(ExprKeys.TYPE, self.DEFAULT_TYPE).strip().lower()
        expr_types = [x.name_text for x in TextTypes.get_values()]
        if expr_type not in expr_types:
            valid = "\n - " + "\n - ".join(expr_types)
            raise WizardError(f"Invalid type {expr_type!r}, valids:{valid}")

        getattr(self, f"_handle_{expr_type}")(expr=expr)

    def _handle_simple(self, expr: dict):
        self._check_req(expr=expr, req=ExprKeys.FIELD)
        if self._expr_complex:
            self._expr_complex[ExprKeys.SUBS].append(expr)
        else:
            if self._expr_bracket:
                expr[ExprKeys.TYPE] = TextTypes.simple.name_expr
                self._expr_bracket[ExprKeys.SUBS].append(expr)
            else:
                expr[ExprKeys.TYPE] = TextTypes.simple.name_expr
                self.exprs.append(expr)

    def _handle_start_complex(self, expr: dict):
        self._check_start(
            expr=expr,
            attr="_expr_complex",
            type1=TextTypes.start_complex.name_expr,
            type2=TextTypes.start_complex.name_expr,
        )
        self._check_req(expr=expr, req=ExprKeys.FIELD)

        expr[ExprKeys.SUBS] = []
        expr[ExprKeys.TYPE] = TextTypes.start_complex.name_expr
        self._expr_complex = expr

        if self._expr_bracket:
            self._expr_bracket[ExprKeys.SUBS].append(expr)
        else:
            self.exprs.append(expr)

    def _handle_start_bracket(self, expr: dict):
        self._check_start(
            expr=expr,
            attr="_expr_bracket",
            type1=TextTypes.start_bracket.name_expr,
            type2=TextTypes.start_bracket.name_expr,
        )
        self._check_start(
            expr=expr,
            attr="_expr_complex",
            type1=TextTypes.start_bracket.name_expr,
            type2=TextTypes.start_complex.name_expr,
        )
        expr[ExprKeys.TYPE] = TextTypes.start_bracket.name_expr
        expr[ExprKeys.SUBS] = []
        self._expr_bracket = expr
        self.exprs.append(expr)

    def _handle_stop_complex(self, expr: dict):
        self._check_stop(
            expr=expr, attr="_expr_complex", type1=TextTypes.start_complex.name_expr
        )

    def _handle_stop_bracket(self, expr: dict):
        self._check_stop(
            expr=expr, attr="_expr_bracket", type1=TextTypes.start_bracket.name_expr
        )

    def _check_start(self, expr: dict, attr: str, type1: str, type2: str):
        attr_value = getattr(self, attr, {})
        if attr_value:
            type1 = f"{type1} section"
            type2 = f"{type2} section"
            idx = attr_value[ExprKeys.IDX] + 1
            raise WizardError(
                f"Can not start a {type1} when in a {type2} started on line #{idx}"
            )

    def _check_stop(self, expr: dict, attr: str, type1: str):
        attr_value = getattr(self, attr, {})
        if not attr_value:
            type1 = f"{type1} section"
            raise WizardError(
                f"Can not stop a {type1} when a {type1} has not been started"
            )
        setattr(self, attr, {})

    def _check_req(self, expr: dict, req: str):
        if not expr.get(req):
            raise WizardError(f"Missing required key {req!r}")
