# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import re
import shlex
from typing import List, Union

from ..data_classes.wizard import (AllEntryTypes, EntryKeys, EntryType,
                                   TextEntryTypes)
from ..exceptions import WizardError
from ..tools import check_empty, check_type, path_read
from .wizard import Wizard, kv_dump


# WizardCli
# WizardCsv
class WizardText(Wizard):
    ITEM_SEP: str = ","
    VALUE_SEP: str = "="
    WORDCHARS: str = f"{VALUE_SEP}.: "

    def parse(self, content: str, source: str = "text string"):
        check_type(value=content, exp=str, name="content")

        lines: List[str] = content.splitlines()
        self.LOG.info(f"Parsing {len(lines)} lines from {source}")

        self.sq = {"sq": {}, "entries": []}
        self.sqs = []
        self.in_complex = {}

        for idx, line in enumerate(lines):
            src = f"{source} line #{idx + 1}: {line!r}"
            try:
                entry = self._split_line(line=line)
                self.LOG.debug(f"Split {src}\n  {kv_dump(entry)}")
            except Exception as exc:
                example = self.get_examples(include_help=False)
                raise WizardError(f"Error splitting {src}\n{exc}\n{example}")

            if not entry:
                continue

            self._parse_line(entry=entry, src=src)

        if not self.sqs:
            example = self.get_examples(include_help=False)
            raise WizardError(f"No entries parsed from {source}:\n{content}{example}")

        for sq_idx, sq in enumerate(self.sqs):
            sq_obj = sq["sq"]
            entries = sq["entries"]

            fields = sq_obj.pop(EntryKeys.SQ_FIELDS.name)
            fields_default = sq_obj[EntryKeys.SQ_FIELDS_DEFAULT.name]

            sq_obj["fields_manual"] = self.apiobj.fields.validate(
                fields=fields,
                fields_default=fields_default,
                fields_map=self._fields_map(),
            )
            sq_obj.update(super().parse(entries=entries))
        return self.sqs

    def parse_path(self, path):
        path, content = path_read(path)
        return self.parse(content=content, source=f"text file {path}")

    def _parse_line(self, entry: dict, src: str):
        entry_type = self._get_entry_type(entry=entry, entry_types=TextEntryTypes)
        self._parse_keys(entry=entry, entry_type=entry_type, src=src)

        entry["source"] = src

        if entry_type == AllEntryTypes.SAVED_QUERY:
            self.sq = {"sq": entry, "entries": []}
            self.sqs.append(self.sq)
            return

        self._check_sq(entry=entry)

        example = "\n\n" + self.get_example(entry_type=entry_type)
        err_pre = f"Error parsing {src}\n"

        if entry_type == AllEntryTypes.COMPLEX_SUB:
            if not self.in_complex:
                err = "Must define a type=complex before a type=complex_sub"
                raise WizardError(f"{err_pre}{err}{example}")

            self.in_complex["subs"].append(entry)
            return

        self.sq["entries"].append(entry)

        if entry_type == AllEntryTypes.SIMPLE:
            if self.in_complex and not self.in_complex["subs"]:
                csrc = self.in_complex["source"]
                err = (
                    f"Can not start a type=simple when no type=complex-sub under {csrc}"
                )
                raise WizardError(f"{err_pre}{err}{example}")

            self.in_complex = {}

        if entry_type == AllEntryTypes.COMPLEX:
            if self.in_complex and not self.in_complex["subs"]:
                csrc = self.in_complex["source"]
                err = (
                    f"Can not start a type=complex when no type=complex-sub under {csrc}"
                )
                raise WizardError(f"{err_pre}{err}{example}")

            entry["subs"] = []
            self.in_complex = entry

    def _split_line(self, line: str) -> dict:
        """Parse key-value pairs from a shell-like text line."""
        check_type(value=line, exp=str, name="line")
        line = line.strip()
        entry = {}

        if not line or line.startswith("#"):
            return entry

        lexer = shlex.shlex(line, posix=True)
        lexer.whitespace = self.ITEM_SEP
        lexer.wordchars += self.WORDCHARS

        for word in lexer:
            self._split_word(entry=entry, word=word)

        return entry

    def _split_word(self, entry: dict, word: str) -> dict:
        sep = self.VALUE_SEP
        if sep not in word:
            raise WizardError(
                "Missing double quotes around value???"
                f" No separator {sep!r} in word {word!r}"
            )

        word_key, word_value = word.split(self.VALUE_SEP, maxsplit=1)
        word_key = word_key.strip().lower()
        word_value = word_value.lstrip()

        if not word_key:
            raise WizardError(f"Empty key {word_key!r} in word {word!r}")

        if word_key in entry:
            raise WizardError(f"Duplicate key {word_key!r} found")

        entry[word_key] = word_value

    def _check_sq(self, entry: dict):
        if not self.sq["sq"]:
            src = entry["source"]
            raise WizardError(
                f"Must define type=saved_query as the first line, not {src}"
            )

    @classmethod
    def get_examples(cls, include_help: bool = True) -> str:
        lines = ["", "# EXAMPLES"]
        lines += [
            cls.get_example(x, include_help=include_help)
            for x in TextEntryTypes.get_values()
        ]
        return "\n".join(lines)

    @classmethod
    def get_example(
        cls, entry_type: Union[str, EntryType], include_help: bool = True
    ) -> str:
        examples = []
        helps = []

        for key in entry_type.keys:
            req = "REQUIRED" if key.required else "OPTIONAL"
            # ex_default = cls._value_unparse(key.default)
            example = key.example
            desc = key.description

            if key == EntryKeys.TYPE:
                example = entry_type.name
                h_default = f", DEFAULT: {key.default}"
            elif key.default:
                default = cls._value_unparse(key.default)
                h_default = f", DEFAULT: {default}"
            else:
                h_default = ""

            if key.choices:
                choices = ", CHOICES: " + ", ".join([x for x in key.choices if x])
            else:
                choices = ""

            examples.append(f"{key.name}{cls.VALUE_SEP}{example}")
            helps.append(f"# {key.name:<13}: [{req}] {desc}{h_default}{choices}")

        example = f"{cls.ITEM_SEP} ".join(examples)
        if include_help:
            example = ["# EXAMPLE", example, *helps, ""]
            example = "\n".join(example)
        return example

    @staticmethod
    def _value_unparse(value: Union[str, int, bool]) -> str:
        if value is None:
            value = ""

        if value is False:
            value = "n"

        if value is True:
            value = "y"

        if isinstance(value, list):
            value = ", ".join([str(x) for x in value])

        if isinstance(value, str) and re.search(r"[^a-zA-Z0-9_.: ]", value):
            value = f'"{value}"'

        if value == "":
            value = '""'
        return value

    @classmethod
    def _entry_unparse(cls, entry: dict) -> str:
        check_type(value=entry, exp=dict, name="entry")
        keys = EntryKeys.get_values()
        words = []
        for key in keys:
            if key.name not in entry:
                continue
            value = cls._value_unparse(value=entry[key.name])
            words.append(f"{key.name}{cls.VALUE_SEP}{value}")
        return f"{cls.ITEM_SEP} ".join(words)

    # XXX RE-DO ME
    @classmethod
    def unparse(cls, entries: List[dict]):
        check_type(value=entries, exp=list, name="entries", exp_items=dict)
        check_empty(value=entries, name="entries")
        return "\n".join([cls._entry_unparse(entry=entry) for entry in entries])
