# -*- coding: utf-8 -*-
"""Parser for AQL queries and GUI expressions from CSV files."""
import csv
import io
import pathlib
from typing import List, Optional, Union

from ...constants.wizards import Docs, Entry, EntrySq, Sources, Types
from ...exceptions import WizardError
from ...tools import (
    bom_strip,
    check_gui_page_size,
    check_type,
    coerce_bool,
    kv_dump,
    listify,
    path_read,
)
from .wizard import Wizard


class WizardCsv(Wizard):
    """Parser for AQL queries and GUI expressions from CSV files.

    Notes:
        This wizard can create as many saved queries as you like. The first row of the CSV
        must always have a type value of "saved_query". All rows under that row will be added to
        that saved query until another row with a type value of "saved_query" is found.
        Repeat this pattern as you see fit.

        The description, tags, and fields columns are only used for types of "saved_query"

    Examples:
        Create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
        ``apiobj`` is either ``client.devices`` or ``client.users``

        >>> apiobj = client.devices  # or client.users

        Define a CSV string to parse

        >>> content = '''
        ... type,value,description,tags,fields
        ... saved_query,name of sq,description  of sq,"tag1,tag2, tag4","os.type,default, aws:aws_device_type"
        ... simple,hostname contains test,,,
        ... simple,os.type equals windows,,,
        ... saved_query,name of second sq,description  of sq,"tag1,tag2, tag4",
        ... simple,hostname contains test,,,
        ... complex,installed_software // name contains chrome // version earlier_than 82,,,
        ... simple,os.type equals windows,,,
        ... '''

        Parse the CSV string into a query and GUI expressions

        >>> parsed = apiobj.wizard_csv.parse(content=content)
        >>> for sq in parsed:
        ...   sq['name']
        ...   sq['query'][:80]
        ...   len(sq['expressions'])
        ...
        'name of sq'
        '(specific_data.data.hostname == regex("test", "i")) and (specific_data.data.os.t'
        2
        'name of second sq'
        '(specific_data.data.hostname == regex("test", "i")) and (specific_data.data.inst'
        3

        Or parse a CSV file directly

        >>> parsed = apiobj.wizard_csv.parse(path="~/test.csv")

        Use the result to create saved queries that the GUI understands

        >>> sqs = [apiobj.saved_query.add(**sq) for sq in parsed]
        >>> for sq in sqs:
        ...    sq['name']
        ...    sq['uuid']
        ...    sq['view']['query']['filter'][:80]
        ...
        'name of sq'
        '5f79e90be4557d5cbab26344'
        '(specific_data.data.hostname == regex("test", "i")) and (specific_data.data.os.t'
        'name of second sq'
        '5f79e90be4557d5cbab26359'
        '(specific_data.data.hostname == regex("test", "i")) and (specific_data.data.inst'

    """  # noqa: E501

    DOCS: str = Docs.CSV

    def parse(self, content: str, source: str = Sources.CSV_STR) -> List[dict]:
        """Parse a CSV string into a set of saved queries.

        Args:
            content: CSV string
            source: where content came from
        """
        source = source or Sources.CSV_STR
        entries = self._load_csv(content=content, source=source)
        sqs = self._process_sqs(entries=entries)
        return sqs

    def parse_path(
        self, path: Union[str, pathlib.Path], source: str = Sources.CSV_PATH
    ) -> List[dict]:
        """Parse a CSV file into a set of saved queries.

        Args:
            path: CSV file
            source: where csv file came from
        """
        path, content = path_read(path, encoding="utf-8")
        source = source.format(path=path)
        return self.parse(content=content, source=source)

    def _load_csv(self, content: str, source: str) -> List[dict]:
        """Load a CSV string and parse the rows into entries.

        Args:
            content: CSV string
            source: where content came from
        """
        check_type(value=content, exp=str, name="content")
        content = bom_strip(content=content)
        fh = io.StringIO(content)
        reader = csv.DictReader(fh)
        rows = list(reader)
        columns = listify(reader.fieldnames)
        entries = self._process_csv(rows=rows, columns=columns, source=source)
        return entries

    def _process_csv(self, rows: List[dict], columns: List[str], source: str) -> List[dict]:
        """Process and validate the rows and columns from a CSV into entries.

        Args:
            rows: rows from the CSV
            columns: columns from the CSV
            source: where content came from
        """
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
        """Process and validate the rows from a CSV into entries.

        Args:
            rows: rows from the CSV
            source: where content came from
        """
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
        """Proccess and validate a row from a CSV into an entry.

        Args:
            row: row from the CSV
            src: identifier of where the row came from
        """
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
            for key, default in EntrySq.OPT.items():
                if key in row:
                    value = row[key]
                    if value in [None, ""]:
                        value = default
                else:
                    value = default
                entry[key] = value
        return entry

    def _process_sqs(self, entries: List[dict]) -> List[dict]:
        """Process the saved queries defined in the CSV.

        Args:
            entries: the entries produced by parsing the rows
        """
        self.SQS = sqs = []
        self.SQ = {}
        self.SQ_ENTRIES = []
        self.SQS_DONE = []

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
        """Process a saved query.

        Args:
            entry: entry being processed by :meth:`_process_sqs`
            is_last: entry is the last entry being processed by :meth:`_process_sqs`
        """
        if entry[Entry.TYPE] == Types.SAVED_QUERY:
            if self.SQ_ENTRIES:
                self._process_sq_entries()
                self._new_sq(entry=entry)
                return 0

            self._new_sq(entry=entry)
            return 1
        else:
            self.SQ_ENTRIES.append(entry)

        if not self.SQ:
            raise WizardError(
                f"First row must be type {Types.SAVED_QUERY!r}, not {entry[Entry.TYPE]!r}"
            )

        if is_last:
            self._process_sq_entries()
            return 2

        return 3

    def _process_sq_entries(self):
        """Process the entries for the current saved query."""
        if self.SQ_ENTRIES and self.SQ and self.SQ not in self.SQS_DONE:
            cnt = len(self.SQ_ENTRIES)
            self.LOG.debug(f"processing {cnt} entries in for SQ {kv_dump(self.SQ)}")
            parsed = super().parse(entries=self.SQ_ENTRIES)
            self.SQ.update(parsed)
        self.SQS_DONE.append(self.SQ)

    # NEXT: need to add support for path && folder_id
    def _new_sq(self, entry: dict):
        """Create a new current saved query.

        Args:
            entry: entry being processed by :meth:`_process_sqs`
        """
        self.SQ = {}
        self.SQ[EntrySq.NAME] = entry[Entry.VALUE]
        self.SQ[EntrySq.FDEF] = False
        self.SQ[EntrySq.FMAN] = self._process_fields(entry=entry)
        self.SQ[EntrySq.TAGS] = self._process_tags(entry=entry)
        self.SQ[EntrySq.DESC] = self._process_desc(entry=entry)
        self.SQ[EntrySq.PRIVATE] = coerce_bool(
            entry.get(EntrySq.PRIVATE, EntrySq.OPT[EntrySq.PRIVATE])
        )
        self.SQ[EntrySq.ASSET_SCOPE] = coerce_bool(
            entry.get(EntrySq.ASSET_SCOPE, EntrySq.OPT[EntrySq.ASSET_SCOPE])
        )
        self.SQ[EntrySq.ALWAYS_CACHED] = coerce_bool(
            entry.get(EntrySq.ALWAYS_CACHED, EntrySq.OPT[EntrySq.ALWAYS_CACHED])
        )
        self.SQ[EntrySq.PAGE_SIZE] = check_gui_page_size(
            entry.get(EntrySq.PAGE_SIZE, EntrySq.OPT[EntrySq.PAGE_SIZE])
        )
        self.LOG.debug(f"New {Types.SAVED_QUERY} found {kv_dump(self.SQ)}")

        self.SQ_ENTRIES = []
        self.SQS.append(self.SQ)

    def _process_desc(self, entry: dict) -> Optional[str]:
        """Process the description key of an entry.

        Args:
            entry: entry being processed by :meth:`_process_sqs`
        """
        desc = str(entry.get(EntrySq.DESC) or "")
        return desc.strip() or None

    def _process_tags(self, entry: dict) -> Optional[List[str]]:
        """Process the tags key of an entry.

        Args:
            entry: entry being processed by :meth:`_process_sqs`
        """
        tags = str(entry.get(EntrySq.TAGS) or "")
        tags = [x.strip() for x in tags.split(",") if x.strip()]
        return tags or None

    def _process_fields(self, entry: dict) -> [List[str]]:
        """Process the fields key of an entry.

        Args:
            entry: entry being processed by :meth:`_process_sqs`
        """
        fields = str(entry.get(EntrySq.FIELDS) or EntrySq.DEFAULT)
        fields = [x.strip().lower() for x in fields.split(",") if x.strip()]

        if EntrySq.DEFAULT in fields:
            lidx = fields.index(EntrySq.DEFAULT)
            ridx = lidx + 1
            fields[lidx:ridx] = self.APIOBJ.fields_default
            fields = [x for x in fields if x != EntrySq.DEFAULT]

        if fields not in [[EntrySq.DEFAULT], self.APIOBJ.fields_default]:
            fields = self.APIOBJ.fields.validate(fields=fields, fields_default=False)
        return fields

    def _init(self):
        """Post init setup."""
        self.SQS: List[dict] = []
        """Saved queries produced by this wizard"""

        self.SQ: dict = {}
        """Current saved query being processed"""

        self.SQ_ENTRIES: List[dict] = []
        """Entries belonging to current saved query being processed"""

        self.SQS_DONE: List[dict] = []
        """Saved queries that have been processed"""
