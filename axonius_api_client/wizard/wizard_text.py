# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import shlex
from typing import List, Tuple, Union

from ..exceptions import WizardError
from ..tools import check_type, path_read
from .constants import (AllEntryTypes, Consts, EntryKeys, EntryType,
                        TextEntryTypes)
from .wizard import Wizard


class WizardTextBase(Wizard):
    NEEDS_SQ: bool = True

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

    def _line_to_entry(self, line: str, src: str) -> dict:
        """Parse key-value pairs from a shell-like text line."""
        check_type(value=line, exp=str, name="line")
        self.LOG.debug(f"in line: {src}")

        line = line.strip()
        entry = {}
        err_pre = f"Error splitting {src}:\n"

        if not line or line.startswith("#"):
            self.LOG.debug("empty line or begins with comment, skip rest of line")
            return entry

        lexer = shlex.shlex(line, posix=True)
        lexer.whitespace = Consts.ITEM_SEP
        lexer.wordchars += Consts.WORDCHARS

        for idx, word in enumerate(lexer):
            print(idx, word)
            wtxt = f"in word #{idx + 1}: {word!r}"

            # if word.startswith("#") or not word.strip():
            #     self.LOG.debug(
            #         f"empty word or begins with comment {wtxt}, stop parsing line"
            #     )
            #     break

            # if Consts.VALUE_SEP not in word:
            #     errs = [
            #         f"{err_pre}No separator {Consts.VALUE_SEP!r} {wtxt}",
            #         "Tip: Missing double quotes around value???",
            #         Consts.STR_EXAMPLES,
            #         self.get_examples(include_help=True),
            #     ]
            #     raise WizardError("\n\n".join(errs))

            word_key, word_value = word.split(Consts.VALUE_SEP, maxsplit=1)
            word_key = word_key.strip().lower()
            word_value = word_value.lstrip()

            if not word_key:
                errs = [
                    f"{err_pre}Empty key {word_key!r} {wtxt}",
                    Consts.STR_EXAMPLES,
                    self.get_examples(include_help=True),
                ]
                raise WizardError("\n\n".join(errs))

            if word_key in entry:
                errs = [
                    f"{err_pre}Duplicate key {word_key!r} found {wtxt}",
                    Consts.STR_EXAMPLES,
                    self.get_examples(include_help=True),
                ]
                raise WizardError("\n\n".join(errs))

            entry[word_key] = word_value

        self.LOG.debug(f"Split line into entry: {entry}")
        return entry

    # XXX i don't like this
    def _parse_line(
        self,
        entry: dict,
        sq: dict,
        entries: List[dict],
        in_complex: dict,
        src: str,
        line: str,
    ) -> Tuple[dict, List[dict], dict]:
        entry_type = self._get_entry_type(entry=entry, entry_types=TextEntryTypes)

        ftype = f"{EntryKeys.TYPE.name}={entry_type.name}"
        fsq = f"{EntryKeys.TYPE.name}={AllEntryTypes.COMPLEX_SUB.name}"
        fcomplex = f"{EntryKeys.TYPE.name}={AllEntryTypes.COMPLEX.name}"
        fsub = f"{EntryKeys.TYPE.name}={AllEntryTypes.COMPLEX_SUB.name}"
        err_pre = f"Error parsing line:\n{src}\n"
        csrc = in_complex.get(Consts.SRC, "")
        when_no = f"when no {fsub} lines under {csrc}"

        entry = self._parse_keys(entry=entry, entry_type=entry_type, src=src)
        entry[Consts.SRC] = src

        ex_sq = self.get_example(
            entry_type=AllEntryTypes.SAVED_QUERY, include_help=False
        )
        ex_this = self.get_example(entry_type=entry_type, include_help=False)
        ex_complex = self.get_example(
            entry_type=AllEntryTypes.COMPLEX, include_help=False
        )
        ex_sub = self.get_example(
            entry_type=AllEntryTypes.COMPLEX_SUB, include_help=False
        )

        if entry_type == AllEntryTypes.SAVED_QUERY:
            flags = entry.pop(EntryKeys.FLAGS.name, [])
            fields_default = Consts.NO_FDEFAULT not in flags
            fields = entry.pop(EntryKeys.SQ_FIELDS.name, [])

            if fields:
                entry[Consts.FMANUAL] = self.apiobj.fields.validate(
                    fields=fields, fields_default=fields_default,
                )
            else:
                fields_default = True

            entry[Consts.FDEFAULT] = fields_default
            entry[Consts.SQ_NAME] = entry.pop(EntryKeys.VALUE.name)

            sq = entry
            entries = []
            in_complex = {}
            return sq, entries, in_complex

        if not sq and self.NEEDS_SQ:
            errs = [
                f"{err_pre}Must define {fsq} as the first line, not {ftype}",
                "",
                Consts.STR_EXAMPLE,
                "\n".join([ex_sq, ex_this]),
            ]
            raise WizardError("\n".join(errs))

        if not sq:
            sq = {}
            entries = []
            in_complex = {}
            return sq, entries, in_complex

        if entry_type == AllEntryTypes.COMPLEX_SUB:
            if not in_complex:
                errs = [
                    f"{err_pre}Must define a {fcomplex} line before a {ftype} line",
                    "",
                    Consts.STR_EXAMPLE,
                    "\n".join([ex_sq, ex_complex, ex_this]),
                ]
                raise WizardError("\n".join(errs))

            in_complex[Consts.SUBS].append(entry)
            return sq, entries, in_complex

        if entry_type == AllEntryTypes.COMPLEX:
            if in_complex and not in_complex[Consts.SUBS]:
                errs = [
                    f"{err_pre}Can not start a {ftype} line {when_no}",
                    "",
                    Consts.STR_EXAMPLE,
                    "\n".join([ex_sq, ex_complex, ex_this]),
                ]
                raise WizardError("\n".join(errs))

            entry[Consts.SUBS] = []
            in_complex = entry
            entries.append(entry)
            return sq, entries, in_complex

        if in_complex and not in_complex[Consts.SUBS]:
            errs = [
                f"{err_pre}Can not start a {ftype} line {when_no}",
                "",
                Consts.STR_EXAMPLE,
                "\n".join([ex_sq, ex_complex, ex_sub, ex_this]),
            ]
            raise WizardError("\n".join(errs))

        in_complex = {}
        entries.append(entry)
        return sq, entries, in_complex


class WizardText(WizardTextBase):
    def parse(self, content: str, source: str = Consts.TXT_SRC_STR) -> List[dict]:
        check_type(value=content, exp=str, name="content")
        lines: List[str] = content.splitlines()
        self.LOG.info(f"Parsing {len(lines)} lines from {source}")
        sq_entries = self._parse_lines(lines=lines, source=source)
        return [self._parse_sq(sq_entry=x) for x in sq_entries]

    def parse_path(self, path) -> List[dict]:
        path, content = path_read(path)
        return self.parse(content=content, source=Consts.TXT_SRC_PATH.format(path=path))

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
