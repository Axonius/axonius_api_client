# -*- coding: utf-8 -*-
"""Constants for wizards."""
import re
from typing import List, Optional, Union

from .api import GUI_PAGE_SIZES


class Templates:
    """Query builder templates."""

    LEFT: str = "({query}"
    """For building a query with a left parentheses"""

    RIGHT: str = "{query})"
    """For building a query with a right parentheses"""

    NOT: str = "not {query}"
    """For building a query with a NOT operator"""

    OR: str = "or {query}"
    """For building a query with an OR operator"""

    AND: str = "and {query}"
    """For building a query with an AND operator"""

    COMPLEX: str = '("{field}" == match([{sub_queries}]))'
    """For building a query for complex fields"""

    SUBS: str = " and "
    """Joiner for sub fields in a complex field"""


class Results:
    """Keys for results returned from wizards."""

    EXPRS: str = "expressions"
    """key containing the expressions that the GUI query wizard can understand"""

    QUERY: str = "query"
    """key containing the AQL produced by the parser"""


class Patterns:
    """Regular expression patterns for validation of values in entries."""

    FIELD_VALID: str = re.compile(
        r"""(?ix)            # case insensitive and verbose
([^a-z0-9:._\-]) # contains characters that are not one of: a-z 0-9 : . _ -
""",
    )
    """regex for validating that a field name is valid"""

    FIELD_FIRST_ALPHA: str = re.compile(
        r"""(?ix)        # case insensitive and verbose
(^[^a-zA-Z]) # starts with characters that are not one of: a-z
"""
    )
    """regex for validating that a field name begins with alpha characters"""

    OP_ALPHA: str = re.compile(
        r"""(?ix)        # case insensitive and verbose
([^a-z0-9_\-])  # contains characters that are not one of: a-z 0-9 _ -
"""
    )
    """regex for validating operators"""

    FLAGS: str = re.compile(
        r"""(?ix)                   # case insensitive and verbose
(?P<flags>[^a-z0-9]*)?  # capture optional flags at beginning
(?P<value>.*)           # capture the rest as the value
"""
    )
    """regex for validating flags"""

    FIELD: List[str] = [FIELD_VALID, FIELD_FIRST_ALPHA]
    """regex validators to use for fields"""

    OP: List[str] = [OP_ALPHA]
    """regex validators to use for operators"""


class Flags:
    """Flag values that can be used in values for entries."""

    NOT: str = "!"
    """Flag to NOT an entry"""

    AND: str = "&"
    """Flag to AND an entry"""

    OR: str = "|"
    """Flag to OR an entry"""

    LEFTB: str = "("
    """Flag to start a parenthesis"""

    RIGHTB: str = ")"
    """Flag to end a perenthesis, can also be at end of a value"""

    FLAGS: dict = {
        AND: "Use and instead of or (default)",
        OR: f"Use or instead of and (overrides {AND})",
        NOT: "Use not",
        LEFTB: "Open a parentheses",
        RIGHTB: "Close a parentheses (can also be at end of entry)",
    }
    """valid flags and their descriptions"""

    LFMT: str = "[" + " ".join(list(FLAGS)) + "]"
    """Doc string to show the flags that can be at the beginning of a value"""

    RFMT: str = f"[{RIGHTB}]"
    """Doc string to show the flags that can be at the end of a value"""

    FMT_TEXT: str = "\n# " + "\n# ".join([f"{k}  {v}" for k, v in FLAGS.items()])
    FMT_CSV: str = ", ".join([f"{k} {v}" for k, v in FLAGS.items()])


class Entry:
    """Entry keys and split values."""

    SRC: str = "source"
    """key of the str of where an entry came from"""

    WEIGHT: str = "bracket_weight"
    """key of the bracket weight for levels of filters within parenthesis"""

    FLAGS: str = "flags"
    """key of the flags were supplied in the value for an entry"""

    VALUE: str = "value"
    """key of the value for the entry"""

    TYPE: str = "type"
    """type of entry"""

    REQ: List[str] = [VALUE, TYPE]
    """Required keys for entries"""

    SPLIT: str = " "
    """String to split on for expressions"""

    CSPLIT: str = " // "
    """String to split on for complex expressions"""


class EntrySq:
    """Entry keys for saved query types."""

    NAME: str = "name"
    """key of name of SQ"""

    DESC: str = "description"
    """key of description of SQ"""

    TAGS: str = "tags"
    """key of tags of SQ"""

    FIELDS: str = "fields"
    """key of fields for SQ"""

    DEFAULT: str = "default"
    """if found in FIELDS column, insert asset API object default fields"""

    FDEF: str = "fields_default"
    FMAN: str = "fields_manual"

    PRIVATE: str = "private"
    ASSET_SCOPE: str = "asset_scope"
    ALWAYS_CACHED: str = "always_cached"
    PAGE_SIZE: str = "gui_page_size"

    REQ: List[str] = [*Entry.REQ]
    """Required keys for saved query types"""

    OPT_ENTRY: dict = {
        PRIVATE: False,
        ALWAYS_CACHED: False,
        ASSET_SCOPE: False,
        PAGE_SIZE: GUI_PAGE_SIZES[0],
    }
    OPT: dict = {
        DESC: "",
        TAGS: "",
        FIELDS: DEFAULT,
        **OPT_ENTRY,
    }
    """Optional keys and their defaults for saved query types"""
    BOOLS: List[str] = [PRIVATE, ASSET_SCOPE, ALWAYS_CACHED]
    INTS: List[str] = [PAGE_SIZE]


class Types:
    """Types of entries."""

    SIMPLE: str = "simple"
    """simple entry type, similar to 'Aggregated Data' GUI query wizard type"""

    COMPLEX: str = "complex"
    """complex entry type, similar to 'Complex Field' GUI query wizard type"""

    SAVED_QUERY: str = "saved_query"
    """saved query type, used in CSV wizard"""

    FILE: str = "file"
    """file type, used in CLI wizards"""

    LINES: str = "lines"
    """lines type, used in CLI wizards"""

    DICT: List[str] = [SIMPLE, COMPLEX]
    """valid types for the base Wizard class."""

    TEXT: List[str] = [*DICT]
    """valid types for the WizardText class."""

    SQ: List[str] = [*DICT, SAVED_QUERY]
    """valid types for the WizardCsv class."""

    CLI: List[str] = [*DICT, FILE, LINES]
    """valid types for the CLI."""


class Docs:
    """Documentation strings for wizards."""

    SUB_OPT: str = f"[{Entry.CSPLIT} ...]"
    OPVAL: str = "FIELD OPERATOR VALUE"

    FMT_SIMPLE: str = f"{Flags.LFMT} {OPVAL} {Flags.RFMT}"
    FMT_COMPLEX: str = f"{Flags.LFMT} COMPLEX-FIELD{Entry.CSPLIT}SUB-{OPVAL}{SUB_OPT} {Flags.RFMT}"
    DESC_SIMPLE: str = "Filter entry for simple fields"
    DESC_COMPLEX: str = "Filter entry for complex fields and their sub-fields"
    EX_SIMPLE1: str = f"{Flags.LEFTB} hostname contains test"
    EX_SIMPLE2: str = f"{Flags.NOT} hostname contains internal {Flags.RIGHTB}"
    EX_SIMPLE3: str = f"{Flags.LEFTB} os.type equals windows"
    EX_SIMPLE4: str = f"{Flags.OR} os.type equals os x {Flags.RIGHTB}"
    EX_COMPLEX1: str = (
        f"installed_software{Entry.CSPLIT}name contains chrome"
        f"{Entry.CSPLIT}version earlier_than 82"
    )

    EX_TEXT: str = f"""{Types.SIMPLE:<8} {EX_SIMPLE1}
{Types.SIMPLE:<8} {EX_SIMPLE2}
{Types.SIMPLE:<8} {EX_SIMPLE3}
{Types.SIMPLE:<8} {EX_SIMPLE4}
{Types.COMPLEX:<8} {EX_COMPLEX1}
"""

    EX_DICT: str = f"""[
  {{
    "{Entry.TYPE}": "{Types.SIMPLE}",
    "{Entry.VALUE}": "{EX_SIMPLE1}"
  }},
  {{
    "{Entry.TYPE}": "{Types.SIMPLE}",
    "{Entry.VALUE}": "{EX_SIMPLE2}"
  }},
  {{
    "{Entry.TYPE}": "{Types.SIMPLE}",
    "{Entry.VALUE}": "{EX_SIMPLE3}"
  }},
  {{
    "{Entry.TYPE}": "{Types.SIMPLE}",
    "{Entry.VALUE}": "{EX_SIMPLE4}"
  }},
  {{
    "{Entry.TYPE}": "{Types.COMPLEX}",
    "{Entry.VALUE}": "{EX_COMPLEX1}"
  }}
]
"""
    EX_FIELDS: str = "os.distribution,os.os_str,active_directory:ad_password_last_set"
    GUI_PAGE_SIZES_STR = " or ".join([str(x) for x in GUI_PAGE_SIZES]) + " (default 20 if empty)"
    OPT_BOOL = "Optional: True or False (default False if empty)"
    EX_CSV: str = f"""
{Entry.TYPE},{Entry.VALUE},{EntrySq.DESC},{EntrySq.TAGS},{EntrySq.FIELDS},{EntrySq.ASSET_SCOPE},{EntrySq.PRIVATE},{EntrySq.ALWAYS_CACHED},{EntrySq.PAGE_SIZE}
"# If {Entry.TYPE} column is empty or begins with # it is ignored",,,,
"# {Entry.TYPE} of {Types.SIMPLE} or {Types.COMPLEX} will belong to the {Types.SAVED_QUERY} they are under",,,,
"# Column descriptions for {Entry.TYPE} of {Types.SAVED_QUERY}","Name of Saved Query","Description of Saved Query","Tags to apply to Saved Query","Columns to display in Saved Query",{OPT_BOOL},{OPT_BOOL},{OPT_BOOL},"{GUI_PAGE_SIZES_STR}",
"# Column descriptions for {Entry.TYPE} of {Types.SIMPLE}","Format -- [] represents optional items: {FMT_SIMPLE}","Description: {DESC_SIMPLE}","Only uses columns {Entry.TYPE} and {Entry.VALUE}",
"# Column descriptions for {Entry.TYPE} of {Types.COMPLEX}","Format -- [] represents optional items: {FMT_COMPLEX}","Description: {DESC_COMPLEX}","Only uses columns {Entry.TYPE} and {Entry.VALUE}",
"# Value Flags for {Entry.TYPE} of {Types.SIMPLE} or {Types.COMPLEX}","{Flags.FMT_CSV}",,,
"{Types.SAVED_QUERY}","example 1","Filters, default fields, custom fields","example,tag1,tag2","{EX_FIELDS},{EntrySq.DEFAULT},os.build"
"{Types.SIMPLE}","{EX_SIMPLE1}",,,
"{Types.SIMPLE}","{EX_SIMPLE2}",,,
"{Types.SIMPLE}","{EX_SIMPLE3}",,,
"{Types.SIMPLE}","{EX_SIMPLE4}",,,
"{Types.SAVED_QUERY}","example 2","No filters, no default fields, custom fields","example,tag3,tag4","{EX_FIELDS}"
"{Types.SAVED_QUERY}","example 3","No filters, default fields, no custom fields","example,tag5,tag6",
"""  # noqa: E501

    TEXT: str = f"""
# Example:
{EX_TEXT}

# Format -- [] represents optional items:
{Types.SIMPLE:<8} {FMT_SIMPLE}
# Description: {DESC_SIMPLE}
{Types.COMPLEX:<8} {FMT_COMPLEX}
# Description: {DESC_COMPLEX}

# Flags:{Flags.FMT_TEXT}
"""
    DICT: str = f"""
# Example:
{EX_DICT}

# Format -- [] represents optional items:
# "{Entry.TYPE}": "{Types.SIMPLE}, "{Entry.VALUE}": "{FMT_SIMPLE}"
# Description: "{DESC_SIMPLE}"
# "{Entry.TYPE}": "{Types.COMPLEX}", "{Entry.VALUE}": "{FMT_COMPLEX}"
# Description: "{DESC_COMPLEX}"

# Flags:{Flags.FMT_TEXT}
"""
    CSV: str = f"{EX_CSV}"


class Sources:
    """Defaults for wizard source argument."""

    CSV_STR: str = "csv text string"
    CSV_PATH: str = "csv file {path}"
    TEXT_STR: str = "text string"
    TEXT_PATH: str = "text file {path}"
    LOD: str = "list of dictionaries"
    JSON_STR: str = "json string"
    JSON_PATH: str = "json file {path}"


class Fields:
    """Keys and arguments for field schemas."""

    NAME: str = "name"
    EXPR_TYPE: str = "expr_field_type"
    ANAME: str = "adapter_name"
    SUBS: str = "sub_fields"
    IS_ALL: str = "is_all"
    IS_DETAILS: str = "is_details"
    IS_COMPLEX: str = "is_complex"


class Expr:
    """Keys for GUI expressions."""

    BRACKET_LEFT: str = "leftBracket"
    BRACKET_RIGHT: str = "rightBracket"
    BRACKET_WEIGHT: str = "bracketWeight"
    CHILDREN: str = "children"
    CONDITION: str = "condition"
    CONTEXT: str = "context"
    EXPR: str = "expression"
    FIELD: str = "field"
    FIELD_TYPE: str = "fieldType"
    FILTER: str = "filter"
    FILTER_ADAPTERS: str = "filteredAdapters"
    IDX: str = "i"
    NOT: str = "not"
    OP_COMP: str = "compOp"
    OP_LOGIC: str = "logicOp"
    VALUE: str = "value"
    CONTEXT_OBJ: str = "OBJ"

    OP_AND: str = "and"
    OP_OR: str = "or"
    OP_IDX0: str = ""

    @classmethod
    def get_query(cls, exprs: List[dict]) -> str:
        """Get the query for a list of GUI expressions.

        Args:
            exprs: list of expressions to build query from
        """
        return " ".join([x[cls.FILTER] for x in exprs])

    @classmethod
    def get_subs_query(cls, sub_exprs: List[dict]) -> str:
        """Get the complex query for a list of GUI child expressions.

        Args:
            sub_exprs: list of children of a complex expression to build query from
        """
        return Templates.SUBS.join([x[cls.CONDITION] for x in sub_exprs])

    @classmethod
    def build(
        cls,
        entry: dict,
        query: str,
        field: dict,
        idx: int,
        op_comp: str,
        field_name_override: Optional[str] = None,
        value: Optional[Union[int, str, bool]] = None,
        is_complex: bool = False,
        children: Optional[List[dict]] = None,
    ) -> dict:
        """Build an expression for the GUI to understand the query.

        Args:
            entry: entry to build expression from
            query: AQL string
            field: schema of field
            idx: index of this expression
            field_name_override: value to use as name of field in expr instead of 'name' key from
                field dict
            value: raw expression value
            op_comp: comparison operator
            is_complex: build an expression for a complex filter
            children: children of a complex filter
        """
        flags = entry.get(Entry.FLAGS, []) or []
        weight = entry.get(Entry.WEIGHT, 0)

        is_right = Flags.RIGHTB in flags
        is_left = Flags.LEFTB in flags
        is_not = Flags.NOT in flags
        is_or = Flags.OR in flags

        if is_not:
            query = Templates.NOT.format(query=query)

        if is_right:
            query = Templates.RIGHT.format(query=query)

        if is_left:
            query = Templates.LEFT.format(query=query)

        if idx:
            if is_or:
                query = Templates.OR.format(query=query)
                op_logic = cls.OP_OR
            else:
                query = Templates.AND.format(query=query)
                op_logic = cls.OP_AND
        else:
            op_logic = cls.OP_IDX0

        field_name = (
            field_name_override if isinstance(field_name_override, str) else field[Fields.NAME]
        )

        expression = {}
        expression[cls.BRACKET_WEIGHT] = weight
        expression[cls.CHILDREN] = children or [cls.build_child()]
        expression[cls.OP_COMP] = op_comp
        expression[cls.FIELD] = field_name
        expression[cls.FIELD_TYPE] = field[Fields.EXPR_TYPE]
        expression[cls.FILTER] = query
        expression[cls.FILTER_ADAPTERS] = None
        expression[cls.BRACKET_LEFT] = is_left
        expression[cls.OP_LOGIC] = op_logic
        expression[cls.NOT] = is_not
        expression[cls.BRACKET_RIGHT] = is_right
        expression[cls.VALUE] = value
        if idx:
            expression[cls.IDX] = idx

        if is_complex:
            expression[cls.CONTEXT] = cls.CONTEXT_OBJ

        return expression

    @classmethod
    def build_child(
        cls,
        query: str = "",
        op_comp: str = "",
        field: str = "",
        value: Optional[Union[int, str, bool]] = None,
        idx: int = 0,
    ) -> dict:
        """Build a child expression to be used in an expression.

        Args:
            query: AQL of this child expression
            op_comp: comparison operator
            field: name of field for this child
            value: raw expression value
            idx: index of this expression
        """
        expression = {}
        expression[cls.CONDITION] = query
        expression[cls.EXPR] = {}
        expression[cls.EXPR][cls.OP_COMP] = op_comp
        expression[cls.EXPR][cls.FIELD] = field
        expression[cls.EXPR][cls.FILTER_ADAPTERS] = None
        expression[cls.EXPR][cls.VALUE] = value
        expression[cls.IDX] = idx
        return expression
