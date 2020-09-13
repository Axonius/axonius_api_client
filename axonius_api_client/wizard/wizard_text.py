# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import pathlib
import shlex
from typing import List, Optional, Union

from ..exceptions import WizardError
from ..tools import check_type, path_read
from .constants import Docs, Entry, Sources, Types
from .wizard import Wizard


class WizardText(Wizard):
    DOCS: str = Docs.TEXT

    def parse(self, content: str, source: Optional[str] = None) -> List[dict]:
        source = source or Sources.TEXT_STR
        self._parsed = entries = self._lines_to_entries(content=content, source=source)
        return super().parse(entries=entries, source=source)

    def parse_path(
        self, path: Union[str, pathlib.Path], source: Optional[str] = None
    ) -> List[dict]:
        source = source or Sources.TEXT_PATH.format(path=path)
        path, content = path_read(path)
        return self.parse(content=content, source=source)

    def _lines_to_entries(
        self, content: str, source: Optional[str] = None
    ) -> List[dict]:
        check_type(value=content, exp=str, name="content")
        lines: List[str] = content.splitlines()
        self.LOG.info(f"Parsing {len(lines)} lines from {source}")

        entries = []
        for idx, line in enumerate(lines):
            src = f"{source} line #{idx + 1}: {line!r}"

            if not line.strip() or line.strip().startswith("#"):
                self.LOG.debug(f"Skipping empty/comment line {idx}")
                continue

            try:
                entry = self._line_to_entry(line=line, src=src)
            except Exception as exc:
                err = f"Error parsing from {src}:\n{exc}"
                errs = [err, self.DOCS, err]
                raise WizardError("\n".join(errs))

            entries.append(entry)
        return entries

    def _line_to_entry(self, line: str, src: str) -> dict:
        """Parse key-value pairs from a shell-like text line."""
        line = line.strip()
        entry = {}

        lexer = shlex.shlex(line, posix=True)
        lexer.whitespace = " "

        words = list(lexer)

        for idx, word in enumerate(words):
            if idx:
                if Entry.VALUE in entry:
                    found = [f"item #{i + 1}: {w}" for i, w in enumerate(words)]
                    found = "\n  " + "\n  ".join(found)
                    raise WizardError(
                        f"Must be only 2 quoted items in line, found:{found}"
                    )

                entry[Entry.VALUE] = word
            else:
                word = word.strip().lower()

                if word not in Types.TEXT:
                    valid = ", ".join(Types.TEXT)
                    raise WizardError(
                        f"Unknown type supplied {word!r}, valid types: {valid}"
                    )

                entry[Entry.TYPE] = word

        self.LOG.debug(f"Split line '{line}' into entry: {entry}")
        entry[Entry.SRC] = src
        entry[Entry.FLAGS] = []
        return entry
