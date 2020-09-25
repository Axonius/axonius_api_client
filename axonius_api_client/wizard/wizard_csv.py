# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import codecs
import csv
import io
import pathlib
from typing import List, Optional, Union

from ..exceptions import WizardError
from ..tools import check_type, listify, path_read
from .constants import Docs, Entry, EntrySq, Sources, Types
from .wizard import Wizard


def kv_dump(obj: dict) -> str:
    return "\n  " + "\n  ".join([f"{k}: {v}" for k, v in obj.items()])


class WizardCsv(Wizard):
    DOCS: str = Docs.CSV

    def parse(self, content: str, source: str = Sources.CSV_STR) -> List[dict]:
        source = source or Sources.CSV_STR
        entries = self._load_csv(content=content, source=source)
        sqs = self._process_sqs(entries=entries)
        return sqs

    def parse_path(
        self, path: Union[str, pathlib.Path], source: str = Sources.CSV_PATH
    ) -> List[dict]:
        path, content = path_read(path, encoding="utf-8")
        source = source.format(path=path)
        return self.parse(content=content, source=source)

    def _load_csv(self, content: str, source: str) -> List[dict]:
        check_type(value=content, exp=str, name="content")
        content = content.strip()
        if content.startswith(codecs.BOM_UTF8.decode()):
            content = content[1:]
        content = content.strip()
        fh = io.StringIO(content)
        reader = csv.DictReader(fh)
        rows = list(reader)
        columns = listify(reader.fieldnames)
        entries = self._process_csv(rows=rows, columns=columns, source=source)
        return entries

    def _process_csv(self, rows: List[dict], columns: List[str], source: str) -> List[dict]:
        found = [x.strip().lower() for x in columns if x.strip()]
        found_txt = ", ".join(found or ["NONE!"])

        ctxt = f"Found columns: {found_txt}, rows: {len(rows)}"
        self.LOG.debug(ctxt)

        missing = [x for x in EntrySq.REQ if x not in found]
        if missing:
            errs = [
                f"Error parsing from {source}",
                f"Missing required columns: {EntrySq.REQ}",
                f"Missing columns: {missing}",
                f"Found columns: {found_txt}",
            ]
            err = "\n".join(errs)
            raise WizardError("\n".join([err, self.DOCS, err]))

        entries = self._rows_to_entries(rows=rows, source=source)
        if not entries:
            err = f"Error parsing from {source}\n\nNo rows found! {ctxt}"
            raise WizardError("\n".join([err, self.DOCS, err]))
        return entries

    def _rows_to_entries(self, rows: List[dict], source: str) -> List[dict]:
        entries = []
        for idx, row in enumerate(rows):
            src = f"{source} row #{idx + 1}:{kv_dump(row)}"
            try:
                entries.append(self._row_to_entry(row=row, src=src))
            except Exception as exc:
                err = f"Error parsing row to entry from {src}\n\n{exc}"
                raise WizardError("\n".join([err, self.DOCS, err]))
        return [x for x in entries if x]

    def _row_to_entry(self, row: dict, src: str) -> dict:
        oetype = row.get(Entry.TYPE, "")
        etype = str(oetype or "").strip().lower()
        value = row.get(Entry.VALUE, "") or ""

        if not etype or etype.startswith("#"):
            self.LOG.debug(f"Skipping row due to empty type {oetype!r}: {row}")
            return {}

        etype = self._check_entry_type(etype=etype, types=Types.SQ)

        if not isinstance(value, str) or not value.strip():
            raise WizardError(f"Empty value for column {Entry.VALUE!r}: {value!r}")

        entry = {}
        entry[Entry.TYPE] = etype
        entry[Entry.VALUE] = value.lstrip()
        entry[Entry.SRC] = src
        if entry[Entry.TYPE] == Types.SAVED_QUERY:
            entry.update({k: str(row.get(k, v) or v) for k, v in EntrySq.OPT.items()})
        return entry

    def _process_sqs(self, entries: List[dict]) -> List[dict]:
        self._sqs = sqs = []
        self._sq = {}
        self._sq_entries = []
        self._sqs_done = []

        for idx, entry in enumerate(entries):
            is_last = idx + 1 == len(entries)
            try:
                self._process_sq(entry=entry, is_last=is_last)
            except Exception as exc:
                src = entry.get(Entry.SRC, f"entry #{idx + 1}")
                err = f"Error parsing entry from {src}\n\n{exc}"
                raise WizardError("\n".join([err, self.DOCS, err]))

        return sqs

    def _process_sq(self, entry: dict, is_last: bool) -> int:
        if entry[Entry.TYPE] == Types.SAVED_QUERY:
            if self._sq_entries:
                self._process_sq_entries()
                self._new_sq(entry=entry)
                return 0

            self._new_sq(entry=entry)
            return 1
        else:
            self._sq_entries.append(entry)

        if not self._sq:
            raise WizardError(
                f"First row must be type {Types.SAVED_QUERY!r}, not {entry[Entry.TYPE]!r}"
            )

        if is_last:
            self._process_sq_entries()
            return 2

        return 3

    def _process_sq_entries(self):
        if self._sq_entries and self._sq and self._sq not in self._sqs_done:
            cnt = len(self._sq_entries)
            self.LOG.debug(f"processing {cnt} entries in for SQ {kv_dump(self._sq)}")
            parsed = super().parse(entries=self._sq_entries)
            self._sq.update(parsed)
        self._sqs_done.append(self._sq)

    def _new_sq(self, entry: dict):
        self._sq = {}
        self._sq[EntrySq.NAME] = entry[Entry.VALUE]
        self._sq[EntrySq.FDEF] = False
        self._sq[EntrySq.FMAN] = self._process_fields(entry=entry)
        self._sq[EntrySq.TAGS] = self._process_tags(entry=entry)
        self._sq[EntrySq.DESC] = self._process_desc(entry=entry)
        self.LOG.debug(f"New {Types.SAVED_QUERY} found {kv_dump(self._sq)}")

        self._sq_entries = []
        self._sqs.append(self._sq)

    def _process_desc(self, entry: dict) -> Optional[str]:
        desc = str(entry.get(EntrySq.DESC) or "")
        return desc.strip() or None

    def _process_tags(self, entry: dict) -> Optional[List[str]]:
        tags = str(entry.get(EntrySq.TAGS) or "")
        tags = [x.strip() for x in tags.split(",") if x.strip()]
        return tags or None

    def _process_fields(self, entry: dict) -> [List[str]]:
        fields = str(entry.get(EntrySq.FIELDS) or EntrySq.DEFAULT)
        fields = [x.strip().lower() for x in fields.split(",") if x.strip()]

        if EntrySq.DEFAULT in fields:
            lidx = fields.index(EntrySq.DEFAULT)
            ridx = lidx + 1
            fields[lidx:ridx] = self._apiobj.fields_default
            fields = [x for x in fields if x != EntrySq.DEFAULT]

        if fields != [EntrySq.DEFAULT]:
            fields = self._apiobj.fields.validate(fields=fields, fields_default=False)
        return fields

    def _init(self):
        self._sqs: List[dict] = []
        self._sq: dict = {}
        self._sq_entries: List[dict] = []
        self._sqs_done: List[dict] = []
