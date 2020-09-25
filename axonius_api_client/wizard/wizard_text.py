# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import pathlib
from typing import List, Union

from ..exceptions import WizardError
from ..tools import check_type, path_read
from .constants import Docs, Entry, Sources, Types
from .wizard import Wizard


class WizardText(Wizard):
    DOCS: str = Docs.TEXT

    def parse(self, content: str, source: str = Sources.TEXT_STR) -> List[dict]:
        entries = self._lines_to_entries(content=content, source=source)
        return super().parse(entries=entries, source=source)

    def parse_path(
        self, path: Union[str, pathlib.Path], source: str = Sources.TEXT_PATH
    ) -> List[dict]:
        path, content = path_read(path)
        source = source.format(path=path)
        return self.parse(content=content, source=source)

    def _lines_to_entries(self, content: str, source: str) -> List[dict]:
        check_type(value=content, exp=str, name="content")
        lines: List[str] = content.splitlines()
        self.LOG.info(f"Parsing {len(lines)} lines from {source}")

        entries = []
        for idx, line in enumerate(lines):
            if not line.strip() or line.strip().startswith("#"):
                self.LOG.debug(f"Skipping empty/comment line {idx}")
                continue

            src = f"{source} line #{idx + 1}: {line}"

            try:
                entries.append(self._line_to_entry(line=line, src=src))
            except Exception as exc:
                err = f"Error parsing from {src}\n{exc}"
                errs = [err, self.DOCS, err]
                raise WizardError("\n".join(errs))

        return entries

    def _line_to_entry(self, line: str, src: str) -> dict:
        """Parse key-value pairs from a shell-like text line."""
        line = line.strip()
        items = line.split(" ", maxsplit=1)

        etype = items.pop(0).strip().lower()

        if not items:
            raise WizardError(f"Must supply a filter after type {etype!r}")

        etype = self._check_entry_type(etype=etype, types=Types.DICT)
        value = items.pop().lstrip()

        entry = {}
        entry[Entry.TYPE] = etype
        entry[Entry.VALUE] = value
        entry[Entry.SRC] = src
        entry[Entry.FLAGS] = []

        self.LOG.debug(f"Split line {line!r} into entry: {entry}")
        return entry
