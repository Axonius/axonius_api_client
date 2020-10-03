# -*- coding: utf-8 -*-
"""Wizard for text files."""
import pathlib
from typing import List, Union

from ...constants.wizards import Docs, Entry, Sources, Types
from ...exceptions import WizardError
from ...tools import check_type, path_read
from .wizard import Wizard


class WizardText(Wizard):
    """Wizard for text files.

    Examples:
        First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

        >>> # Define a text string to parse
        >>> content = '''
        ... simple hostname contains test
        ... simple os.type equals windows
        ... complex installed_software // name contains chrome // version earlier_than 82
        ... '''
        >>>
        >>> # Parse the text string into a query and GUI expressions
        >>> parsed = client.devices.wizard_text.parse(content=content)
        >>>
        >>> # Or parse a text file directly
        >>> parsed = client.devices.wizard_csv.parse(path="~/test.txt")
        >>>
        >>> # get the query produced by the wizard
        >>> query = parsed["query"]
        >>> print(query)
        >>>
        >>> # get the GUI expressions produced by the wizard
        >>> expressions = parsed["expressions"]
        >>> print(expressions)
        >>>
        >>> # use the query to get assets
        >>> assets = client.devices.get(query=query)
        >>>
        >>> # use the query to get a count of assets
        >>> count = client.devices.count(query=query)
        >>>
        >>> # use the query and expressions to create a saved query that the GUI understands
        >>> sq = client.devices.saved_query.add(name="test", query=query, expressions=expressions)

    """  # noqa: E501

    DOCS: str = Docs.TEXT

    def parse(self, content: str, source: str = Sources.TEXT_STR) -> List[dict]:
        """Parse a CSV string into a query and GUI expressions.

        Args:
            content: text string
            source: where content came from
        """
        entries = self._lines_to_entries(content=content, source=source)
        return super().parse(entries=entries, source=source)

    def parse_path(
        self, path: Union[str, pathlib.Path], source: str = Sources.TEXT_PATH
    ) -> List[dict]:
        """Parse a text file into a query and GUI expressions.

        Args:
            path: text file
            source: where csv file came from
        """
        path, content = path_read(path)
        source = source.format(path=path)
        return self.parse(content=content, source=source)

    def _lines_to_entries(self, content: str, source: str) -> List[dict]:
        """Parse the lines from a text file into entries.

        Args:
            content: text string
            source: where content came from
        """
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
        """Parse a line into an entry.

        Args:
            line: current line being processed by :meth:`_lines_to_entries`
            src: identifier of where the line came from
        """
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
