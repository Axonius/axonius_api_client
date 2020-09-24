# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import codecs
import csv
import io
import pathlib
from typing import List, Optional, Union

from ..exceptions import WizardError
from ..tools import check_type, path_read
from .constants import Docs, Entry, EntrySq, Sources, Types
from .wizard import Wizard


def kv_dump(obj: dict) -> str:
    return "\n  " + "\n  ".join([f"{k}: {v}" for k, v in obj.items()])


class WizardCsv(Wizard):
    DOCS: str = Docs.CSV

    def parse(self, content: str, source: str = Sources.CSV_STR) -> List[dict]:
        source = source or Sources.CSV_STR
        return self._load_csv(content=content, source=source)

    def parse_path(
        self, path: Union[str, pathlib.Path], source: str = Sources.CSV_PATH
    ) -> List[dict]:
        path, content = path_read(path, encoding="utf-8")
        source = source.format(path=path)
        return self.parse(content=content, source=source)

    def _load_csv(self, content: str, source: str) -> List[dict]:
        check_type(value=content, exp=str, name="content")
        if content.startswith(codecs.BOM_UTF8.decode()):
            content = content[1:]

        content = content.strip()
        fh = io.StringIO(content)
        reader = csv.DictReader(fh)
        rows = [x for x in reader if x]
        columns = [x.strip().lower() for x in reader.fieldnames or []]

        found = ", ".join(columns or ["NONE!"])
        ctxt = f"Found columns: {found}, rows: {len(rows)}"
        self.LOG.debug(ctxt)

        if not rows:
            err = f"Error parsing from {source}\n\nNo rows found! {ctxt}"
            errs = [err, self.DOCS, err]
            raise WizardError("\n".join(errs))

        self._sqs = []
        self._sq = {}
        self._sq_entries = []
        self._sqs_done = []

        for idx, row in enumerate(rows):
            src = f"{source} row #{idx + 1}:{kv_dump(row)}"

            try:
                self._process_row(row=row, idx=idx, row_count=len(rows), src=src)
            except Exception as exc:
                err = f"Error parsing from {src}\n\n{exc}"
                errs = [err, self.DOCS, err]
                raise WizardError("\n".join(errs))

        return self._sqs

    def _process_row(self, row: dict, idx: int, row_count: int, src: str):
        entry = self._row_to_entry(row=row)

        if not entry:
            return

        self._check_entry_keys(entry=entry, keys=EntrySq.REQ)
        entry[Entry.SRC] = src
        etype = self._check_entry_type(entry=entry, types=Types.SQ)
        stype = Types.SAVED_QUERY

        if not idx:
            if etype == stype:
                self._new_sq(entry=entry)
                return

            raise WizardError(f"First entry must be type {stype!r}, not {etype!r}")

        if etype == stype:
            if self._sq_entries:
                self._process_sq(src=src)

            self._new_sq(entry=entry)
            return

        self._sq_entries.append(entry)

        if idx == row_count - 1:
            self._process_sq(src=src)
            return

    def _row_to_entry(self, row: dict) -> dict:
        entry = {}
        for k, v in row.items():
            k = str(k or "").lower().strip()

            if k == Entry.TYPE:
                if not v or not isinstance(v, str) or str(v).startswith("#"):
                    return {}

            if v is not None and str(v).strip():
                entry[k] = str(v)
        return entry

    def _process_sq(self, src: str):
        if self._sq_entries and self._sq not in self._sqs_done:
            cnt = len(self._sq_entries)
            self.LOG.debug(f"processing {cnt} entries in for SQ {kv_dump(self._sq)}")
            parsed = super().parse(entries=self._sq_entries, source=src)
            self._sq.update(parsed)
        self._sqs_done.append(self._sq)

    def _new_sq(self, entry: dict):
        self._sq = {}
        self._sq[EntrySq.NAME] = entry[Entry.VALUE]
        self._sq[EntrySq.FDEF] = False
        self._sq[EntrySq.FMAN] = self._process_fields(entry=entry)
        self._sq[EntrySq.TAGS] = self._process_tags(entry=entry)
        self._sq[EntrySq.DESC] = self._process_desc(entry=entry)
        self._sq_entries = []
        self._sqs.append(self._sq)
        self.LOG.debug(f"New {Types.SAVED_QUERY} found {kv_dump(self._sq)}")

    def _process_desc(self, entry: dict) -> Optional[str]:
        desc = entry.get(EntrySq.DESC) or ""
        desc = desc.strip()
        return desc or None

    def _process_tags(self, entry: dict) -> Optional[List[str]]:
        tags = entry.get(EntrySq.TAGS) or ""
        tags = [x.strip() for x in tags.split(",") if x.strip()]
        return tags or None

    def _process_fields(self, entry: dict) -> [List[str]]:
        fields = entry.get(EntrySq.FIELDS) or EntrySq.DEFAULT
        fields = fields if fields else ""
        fields = [x.strip().lower() for x in fields.split(",") if x.strip()]

        if EntrySq.DEFAULT in fields:
            lidx = fields.index(EntrySq.DEFAULT)
            ridx = lidx + 1
            fields[lidx:ridx] = self._apiobj.fields_default
            fields = [x for x in fields if x != EntrySq.DEFAULT]

        fields = self._apiobj.fields.validate(fields=fields, fields_default=False)
        return fields
