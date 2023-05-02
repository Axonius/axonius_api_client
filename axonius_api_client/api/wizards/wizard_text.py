# -*- coding: utf-8 -*-
"""Parser for AQL queries and GUI expressions from text files."""
import pathlib
from typing import List, Union

from ...constants.wizards import Docs, Entry, Sources, Types
from ...exceptions import WizardError
from ...tools import check_type, path_read
from .wizard import Wizard


class WizardText(Wizard):
    """Wizard for text files.

    Examples:
        Create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
        ``apiobj`` is either ``client.devices`` or ``client.users``

        >>> apiobj = client.devices  # or client.users

        Define a text string to parse

        >>> content = '''
        ... simple hostname contains test
        ... simple os.type equals windows
        ... complex installed_software // name contains chrome // version earlier_than 82
        ... '''

        Parse the text string into a query and GUI expressions

        >>> parsed = apiobj.wizard_text.parse(content=content)

        Or parse a text file directly

        >>> parsed = apiobj.wizard_csv.parse(path="~/test.txt")
        >>> list(parsed)
        ['expressions', 'query']

        Get the query produced by the wizard

        >>> query = parsed["query"]
        >>> query[:80]
        '(specific_data.data.hostname == regex("test", "i")) and (specific_data.data.os.t'

        Get the GUI expressions produced by the wizard

        >>> expressions = parsed["expressions"]
        >>> expressions[0]['filter']
        '(specific_data.data.hostname == regex("test", "i"))'
        >>> expressions[1]['filter'][:80]
        'and (specific_data.data.os.type == "Windows")'

        Use the query to get assets

        >>> assets = apiobj.get(query=query)
        >>> len(assets)
        2

        Use the query to get a count of assets

        >>> count = apiobj.count(query=query)
        >>> count
        2

        Use the query and expressions to create a saved query that the GUI understands

        >>> sq = apiobj.saved_query.add(name="test", query=query, expressions=expressions)
        >>> sq['name']
        'test'
        >>> sq['view']['query']['filter'][:80]
        '(specific_data.data.hostname == regex("test", "i")) and (specific_data.data.os.t'

    """

    DOCS: str = Docs.TEXT

    def parse(self, content: Union[str, List[str]], source: str = Sources.TEXT_STR) -> dict:
        """Parse a CSV string into a query and GUI expressions.

        Args:
            content: text string
            source: where content came from
        """
        entries = self._lines_to_entries(content=content, source=source)
        return super().parse(entries=entries, source=source)

    def parse_path(self, path: Union[str, pathlib.Path], source: str = Sources.TEXT_PATH) -> dict:
        """Parse a text file into a query and GUI expressions.

        Args:
            path: text file
            source: where csv file came from
        """
        path, content = path_read(path)
        source = source.format(path=path)
        return self.parse(content=content, source=source)

    def _lines_to_entries(self, content: Union[str, List[str]], source: str) -> List[dict]:
        """Parse the lines from a text file into entries.

        Args:
            content: text string
            source: where content came from
        """
        lines = content.splitlines() if isinstance(content, str) else content
        check_type(value=lines, exp=list, name="content", exp_items=str)

        # lines: List[str] = content.splitlines()
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
