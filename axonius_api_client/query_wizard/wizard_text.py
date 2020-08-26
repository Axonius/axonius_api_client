# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import logging
import shlex
from typing import List

from ..constants import LOG_LEVEL_WIZARD
from ..data_classes.wizard import ExprKeys, TextTypes
from ..exceptions import WizardError
from ..logs import get_obj_log
from ..tools import path_read

SRC: str = "text string"


class WizardText:
    ITEM_SEP: str = ","
    VALUE_SEP: str = "="
    WORDCHARS: str = f"{VALUE_SEP}: "
    DEFAULT_TYPE = TextTypes.simple

    def __init__(self, **kwargs):
        log_level: str = kwargs.get("log_level", LOG_LEVEL_WIZARD)
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)

    def from_text(self, content: str, source: str = SRC):
        self.idx_bracket: int = None
        self.idx_complex: int = None
        self.expr_bracket: dict = None
        self.expr_complex: dict = None

        self.source = source
        self.content: str = content
        self.lines: List[str] = content.splitlines()
        self.exprs: List[dict] = []

        line_cnt = len(self.lines)
        self.LOG.debug(f"Parsing {line_cnt} lines from {source}")

        for idx, line in enumerate(self.lines):
            self.line = line
            self.idx = idx
            self.expr: dict = {}

            try:
                self._parse()
            except Exception as exc:
                current = f"Current line #{idx + 1}: {line}"
                raise WizardError(
                    f"Error while parsing expression from {source}: {exc}:\n{current}"
                )

        return self.exprs

    def from_path(self, path):
        path, content = path_read(obj=path)
        return self.from_text(content=content, source=f"{path}")

    def _parse(self):
        """Parse key-value pairs from a shell-like text."""
        line = self.line
        idx = self.idx
        line = line.lstrip()

        if not line or line.startswith("#"):
            self.LOG.debug(f"Skipping line #{idx + 1}: empty/comment line")
            return

        if self.VALUE_SEP not in line:
            raise WizardError(f"Missing separator {self.VALUE_SEP!r}")

        lexer = shlex.shlex(line, posix=True)
        lexer.whitespace = self.ITEM_SEP
        lexer.wordchars += self.WORDCHARS

        for word in lexer:
            value = word.split(self.VALUE_SEP, maxsplit=1)
            key = value.pop(0).strip().lower()

            if not all([key, value]):
                self.LOG.debug(f"No key/value pair in word {word!r}")
                continue

            self.expr[key] = value.pop()

        self.LOG.debug(f"Split line #{idx + 1} into expr: {self.expr}")

        if self.expr:
            self._handle()

        self.LOG.debug(f"Parsed line #{idx + 1} into expr: {self.expr}")

        self.expr[ExprKeys.SRC] = {ExprKeys.SRC_LINE: line, ExprKeys.SRC_IDX: idx}

    def _handle(self):
        expr_type = self.expr.pop(ExprKeys.TYPE, self.DEFAULT_TYPE).strip().lower()
        expr_types = TextTypes.get_names()
        if expr_type not in expr_types:
            valid = TextTypes.get_names(join="\n - ")
            raise WizardError(f"Invalid type {expr_type!r}, valids:{valid}")

        getattr(self, f"_handle_{expr_type}")()

    def _handle_simple(self):
        if self.expr_complex:
            self.expr_complex[ExprKeys.SUBS].append(self.expr)
        elif self.expr_bracket:
            self.expr[ExprKeys.TYPE] = TextTypes.simple
            self.expr_bracket[ExprKeys.SUBS].append(self.expr)
        else:
            self.expr[ExprKeys.TYPE] = TextTypes.simple
            self.exprs.append(self.expr)

    def _handle_start_complex(self):
        err = "Can not start a complex section"
        if self.expr_complex:
            idx = self.idx_complex + 1
            raise WizardError(f"{err} while in a complex section started on line #{idx}")

        self.expr[ExprKeys.SUBS] = []
        self.expr[ExprKeys.TYPE] = TextTypes.start_complex
        self.idx_complex = self.idx
        self.expr_complex = self.expr

        if isinstance(self.idx_bracket, int):
            self.expr_bracket[ExprKeys.SUBS].append(self.expr)
        else:
            self.exprs.append(self.expr)

    def _handle_stop_complex(self):
        err = "Can not stop a complex section"
        if not self.expr_complex:
            raise WizardError(f"{err} when a complex section has not been started")

        self.expr_complex = None
        self.idx_complex = None

    def _handle_start_bracket(self):
        err = "Can not start a bracket section"
        if self.expr_bracket:
            idx = self.idx_bracket + 1
            raise WizardError(f"{err} while in a bracket section started on line #{idx}")

        if self.expr_complex:
            idx = self.idx_complex + 1
            raise WizardError(f"{err} while in a complex section started on line #{idx}")

        self.expr[ExprKeys.TYPE] = TextTypes.start_bracket
        self.expr[ExprKeys.SUBS] = []
        self.idx_bracket = self.idx
        self.expr_bracket = self.expr
        self.exprs.append(self.expr)

    def _handle_stop_bracket(self):
        err = "Can not stop a bracket section"
        if not self.expr_bracket:
            raise WizardError(f"{err} when a bracket section has not been started")

        self.expr_bracket = None
        self.idx_bracket = None
