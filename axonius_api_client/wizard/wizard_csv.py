# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import codecs
import csv
import io
from typing import List, Union

from ..exceptions import WizardError
from ..tools import check_type, path_read
from .constants import AllEntryTypes, Consts, EntryKeys, EntryType
from .wizard_text import WizardTextBase


# WizardCli
# get_example_header()
class WizardCsv(WizardTextBase):
    NEEDS_SQ: bool = True
    BOM = codecs.BOM_UTF8.decode()

    def parse(self, content: str, source: str = Consts.CSV_SRC_STR) -> List[dict]:
        try:
            lines = self._load_csv(content=content, source=source)
        except Exception as exc:
            errs = [f"Error reading from {source}:", f"{exc}"]
            raise WizardError("\n".join(errs))
        sq_entries = self._parse_lines(lines=lines, source=source)
        return [self._parse_sq(sq_entry=x) for x in sq_entries]

    def parse_path(self, path) -> List[dict]:
        path, content = path_read(path, encoding="utf-8")
        return self.parse(content=content, source=Consts.CSV_SRC_PATH.format(path=path))

    def _line_to_entry(self, line: dict, src: str) -> dict:
        """Parse key-value pairs from a shell-like text line."""
        return {k.strip().lower(): v.lstrip() for k, v in line.items()}

    def _load_csv(self, content: str, source: str) -> List[dict]:
        check_type(value=content, exp=str, name="content")
        if content.startswith(self.BOM):
            content = content[1:]

        content = content.strip()

        fh = io.StringIO(content)

        # XXX catch general errors here
        reader = csv.DictReader(fh)
        lines = [x for x in reader]
        # XXX catch general errors here

        columns = [x.strip().lower() for x in reader.fieldnames]

        entry_keys = EntryKeys.get_values()
        required = [x for x in entry_keys if x.required]
        optional = [x for x in entry_keys if not x.required]
        req_miss = [x.name for x in required if x.name not in columns]
        opt_miss = [x.name for x in optional if x.name not in columns]

        found = ", ".join(columns)
        self.LOG.debug(f"Found columns: {found}")

        if opt_miss:
            opt_txt = ", ".join(opt_miss)
            self.LOG.info(f"Missing columns that are optional: {opt_txt}")

        if req_miss:
            req_txt = ", ".join(req_miss)
            raise WizardError(f"Missing columns that are required: {req_txt}")

        return lines

    @classmethod
    def get_examples(cls, include_help: bool = True) -> str:
        lines = [
            cls.get_example(
                entry_type=AllEntryTypes.SAVED_QUERY, include_help=include_help
            ),
            cls.get_example(entry_type=AllEntryTypes.SIMPLE, include_help=include_help),
            cls.get_example(entry_type=AllEntryTypes.COMPLEX, include_help=include_help),
            cls.get_example(
                entry_type=AllEntryTypes.COMPLEX_SUB, include_help=include_help
            ),
        ]
        join = "\n\n" if include_help else "\n"
        return join.join(lines)

    @classmethod
    def get_example(
        cls, entry_type: Union[str, EntryType], include_help: bool = True
    ) -> str:
        examples = []
        helps = []

        for key in entry_type.keys:
            required = EntryType.key_dict(value=key.required, entry_type=entry_type)
            example = EntryType.key_dict(value=key.example, entry_type=entry_type)
            desc = EntryType.key_dict(value=key.description, entry_type=entry_type)
            choices = EntryType.key_dict(value=key.choices, entry_type=entry_type)
            default = EntryType.key_dict(value=key.default, entry_type=entry_type)
            name = EntryType.key_dict(value=key.name, entry_type=entry_type)

            req_txt = Consts.REQ if required else Consts.OPT
            choice_txt = ""
            help_txt = ""
            desc_txt = f", {Consts.DESC}: {desc}"

            if isinstance(desc, dict):
                desc = "".join([f"\n#  - {k}: {v}" for k, v in desc.items()])
                desc_txt = f", {Consts.DESC}: {desc}"

            if default is not None:
                help_txt = f', {Consts.DEFAULT}: "{default}"'

            if choices:
                choice_txt = ", ".join([x for x in choices if x])
                choice_txt = f", {Consts.CHOICES}: {choice_txt}"

            examples.append(f'{name}{Consts.VALUE_SEP}"{example}"')
            helps.append(f"# {name:<14}: [{req_txt}] {help_txt}{choice_txt}{desc_txt}")

        example = f"{Consts.ITEM_SEP} ".join(examples)
        if include_help:
            example = [
                example,
                *helps,
            ]
            example = "\n".join(example)
        return example
