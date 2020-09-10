# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
from typing import List, Union

from ..exceptions import WizardError
from ..tools import check_type
from .constants import AllEntryTypes, Consts, EntryKeys, EntryType
from .wizard_text import WizardTextBase


"""
--wiz simple "hostname contains blah" "or, not"
--wiz complex "installed_software" "or, not'
--wiz complex_sub 'version less_than 99'

[
    {
        'type': 'simple',
        'value': 'hostname contains blah',
        'flags': 'or, not, bracket_left, bracket_right',
    }
]
"""


# XXX NO SQ!!
# just skip over SQ entries
class WizardCli(WizardTextBase):
    NEEDS_SQ: bool = False

    def parse(self, content: List[str], source: str = Consts.CLI_SRC_STR) -> List[dict]:
        check_type(value=content, exp=str, name="content")
        self.LOG.info(f"Parsing {len(content)} lines from {source}")
        sq_entries = self._parse_lines(lines=content, source=source)
        return [self._parse_sq(sq_entry=x) for x in sq_entries]

    def _parse_sq(self, sq_entry: dict) -> dict:
        sq_obj = sq_entry[Consts.SQ]

        sq_obj.pop(Consts.SRC, "")
        sq_obj.pop(EntryKeys.TYPE.name)
        entries = sq_entry.pop(Consts.ENTRIES)

        if entries:
            parsed = super().parse(entries=entries)
            sq_obj[Consts.EXPRS] = parsed[Consts.EXPRS]
            sq_obj[Consts.QUERY] = parsed[Consts.QUERY]
        return sq_obj

    def _parse_lines(self, lines: List[str], source: str) -> List[dict]:
        sq_entries = {}
        sq = {}
        entries = []
        in_complex = {}

        for idx, line in enumerate(lines):
            src = f"{source} line #{idx + 1}: {line!r}"
            entry = self._line_to_entry(line=line, src=src)

            if not entry:
                continue

            sq, entries, in_complex = self._parse_line(
                entry=entry,
                sq=sq,
                entries=entries,
                in_complex=in_complex,
                src=src,
                line=line,
            )

            sq_name = sq[Consts.SQ_NAME]

            if sq_name not in sq_entries:
                sq_entries[sq_name] = {
                    Consts.SQ: sq,
                    Consts.ENTRIES: entries,
                    Consts.IN_COMPLEX: in_complex,
                }

        if not sq_entries:
            errs = [
                f"No entries parsed from {source}",
                "",
                Consts.STR_EXAMPLES,
                self.get_examples(include_help=True),
            ]
            raise WizardError("\n".join(errs))

        return list(sq_entries.values())

    @classmethod
    def get_examples(cls, include_help: bool = True) -> str:
        lines = [
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
