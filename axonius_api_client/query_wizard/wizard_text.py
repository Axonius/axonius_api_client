# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import re
import shlex
from typing import List, Union

from ..data_classes.wizard import EntryKeys, EntryType, EntryTypes
from ..exceptions import WizardError
from ..tools import check_empty, check_type, path_read
from .wizard import Wizard, kv_dump


# WizardCli
# WizardCsv
class WizardText(Wizard):
    ITEM_SEP: str = ","
    VALUE_SEP: str = "="
    WORDCHARS: str = f"{VALUE_SEP}.: "

    def parse(
        self, content: str, source: str = "text string", sq_required: bool = False
    ):
        check_type(value=content, exp=str, name="content")
        self._pre_parse()

        lines: List[str] = content.splitlines()
        self.LOG.info(f"Parsing {len(lines)} lines from {source}")

        entries = []

        for idx, line in enumerate(lines):
            src = f"from {source} line #{idx + 1}: {line!r}"
            try:
                entry = self._parse_line(line=line)
                self.LOG.debug(f"Split line into entry {src}\n{kv_dump(entry)}")
            except Exception as exc:
                raise WizardError(f"Error splitting line into entry {src}\n{exc}")

            if entry:
                entry["_source"] = src
                entries.append(entry)

        for idx, entry in enumerate(entries):
            src = entry.pop("_source")
            try:
                self._parse_entry(entry=entry, sq_required=sq_required)
            except Exception as exc:
                raise WizardError(f"Error parsing entry #{idx + 1} {src}\n{exc}")

        return self._sqs_serialize

    def parse_path(self, path):
        path, content = path_read(path)
        return self.parse(content=content, source=f"text file {path}")

    @classmethod
    def unparse(cls, entries: List[dict]):
        check_type(value=entries, exp=list, name="entries", exp_items=dict)
        check_empty(value=entries, name="entries")
        return "\n".join([cls._entry_unparse(entry=entry) for entry in entries])

    @classmethod
    def get_examples(cls, include_help: bool = True) -> str:
        lines = ["", "# EXAMPLES"]
        lines += [
            cls.get_example(x, include_help=include_help)
            for x in EntryTypes.get_values()
        ]
        return "\n".join(lines)

    @classmethod
    def get_example(
        cls, entry_type: Union[str, EntryType], include_help: bool = True
    ) -> str:
        entry_type = cls.get_entry_type(entry_type)

        examples = []
        helps = []

        for key in entry_type.keys:
            req = "REQUIRED" if key.required else "OPTIONAL"
            ex_default = cls._value_unparse(key.default)

            if key == EntryKeys.TYPE:
                ex_default = entry_type.name
                h_default = f", default: {key.default}"
            elif key.default:
                h_default = f", default: {ex_default}"
            else:
                h_default = ""

            if isinstance(key.description, dict):
                description = key.description[entry_type.name]
            else:
                description = key.description

            if key.choices:
                choices = ", valid choices: " + ", ".join([x for x in key.choices if x])
            else:
                choices = ""

            examples.append(f"{key.name}{cls.VALUE_SEP}{ex_default}")
            helps.append(f"# {key.name}: [{req}] {description}{h_default}{choices}")

        example = f"{cls.ITEM_SEP} ".join(examples)
        if include_help:
            example = [
                f"# --> {entry_type.name} example",
                example,
                "",
                f"# --> {entry_type.name} help",
                *helps,
                "",
            ]
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

    def _parse_line(self, line: str) -> dict:
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
            self._parse_word(entry=entry, word=word)

        return entry

    def _parse_word(self, entry: dict, word: str) -> dict:
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
