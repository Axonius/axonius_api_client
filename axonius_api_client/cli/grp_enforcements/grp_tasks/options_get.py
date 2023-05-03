# -*- coding: utf-8 -*-
"""Common options for the "enforcements tasks" group of commands."""
import click

from ....api.json_api.count_operator import OperatorTypes
from ....api.json_api.paging_state import PagingState
from ....constants.api import RE_PREFIX
from ....constants.general import SPLITTER
from .export_get import DEFAULT_EXPORT_FORMAT, EXPORT_FORMATS

from ...options import AUTH, OPT_EXPORT_FILE, OPT_EXPORT_OVERWRITE

OPT_EXPORT_FORMAT = click.option(
    "--export-format",
    "-xt",
    "export_format",
    type=click.Choice(list(EXPORT_FORMATS)),
    help="Format to write data as to STDOUT or --export-file.",
    default=DEFAULT_EXPORT_FORMAT,
    show_envvar=True,
    show_default=True,
)


_RE = "(use re_prefix for pattern matching) (multiple)"
_DASH = "(prefix with '-' for descending) "
OPT_DATE_FROM = click.option(
    "--date-from",
    "-df",
    "date_from",
    help="Only get tasks with creation date >= this date",
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_DATE_FROM_ADD = click.option(
    "--date-from-add",
    "-dfa",
    "date_from_add",
    help="seconds to add to date_from (or now if date_from not provided)",
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_DATE_FROM_SUBTRACT = click.option(
    "--date-from-subtract",
    "-dfs",
    "date_from_subtract",
    help="seconds to subtract from date_from (or now if date_from not provided)",
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_DATE_TO = click.option(
    "--date-to",
    "-dt",
    "date_to",
    help="Only get tasks with creation date <= this date",
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_DATE_TO_ADD = click.option(
    "--date-to-add",
    "-dta",
    "date_to_add",
    help="seconds to add to date_to (or now if date_to not provided)",
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_DATE_TO_SUBTRACT = click.option(
    "--date-to-subtract",
    "-dts",
    "date_to_subtract",
    help="seconds to subtract from date_to (or now if date_to not provided)",
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_DURATION_SECONDS = click.option(
    "--duration-seconds",
    "-ds",
    "duration_seconds",
    help="Only get tasks where run duration matches duration_operator",
    type=click.INT,
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_DURATION_OPERATOR = click.option(
    "--duration-operator",
    "-do",
    "duration_operator",
    help="Operator to evaluate the duration_seconds value against task run durations",
    type=click.Choice([x.name for x in OperatorTypes]),
    default=OperatorTypes.less.name,
    show_envvar=True,
    show_default=True,
)
OPT_TASK_ID = click.option(
    "--task-id",
    "-id",
    "task_id",
    help="Only get tasks associated with this 'pretty id'",
    type=click.INT,
    default=None,
    show_envvar=True,
    show_default=True,
)

OPT_ACTION_TYPES = click.option(
    "--action-types",
    "-at",
    "action_types",
    help=f"Only get tasks that were ran by types of actions {_RE}",
    multiple=True,
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_ACTION_TYPES_ERROR = click.option(
    "--action-types-error/--no-action-types-error",
    "-ate/-nate",
    "action_types_error",
    help="Error if any action_types provided are not valid",
    default=True,
    show_envvar=True,
    show_default=True,
)
OPT_ACTION_TYPES_MINIMUM = click.option(
    "--action-types-minimum",
    "-atm",
    "action_types_minimum",
    help="Error if matches for action_types are < this number",
    type=click.INT,
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_DISCOVERY_UUIDS = click.option(
    "--discovery-uuids",
    "-du",
    "discovery_uuids",
    help=f"Only get tasks that were ran by discovery UUIDs {_RE}",
    multiple=True,
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_DISCOVERY_UUIDS_ERROR = click.option(
    "--discovery-uuids-error/--no-discovery-uuids-error",
    "-due/-ndue",
    "discovery_uuids_error",
    help="Error if any discovery_uuids provided are not valid",
    default=True,
    show_envvar=True,
    show_default=True,
)
OPT_DISCOVERY_UUIDS_MINIMUM = click.option(
    "--discovery-uuids-minimum",
    "-dum",
    "discovery_uuids_minimum",
    help="Error if matches for discovery_uuids are < this number",
    type=click.INT,
    default=None,
    show_envvar=True,
    show_default=True,
)

OPT_ENFORCEMENT_NAMES = click.option(
    "--enforcement-names",
    "-en",
    "enforcement_names",
    help=f"Only get tasks that were ran by enforcement names {_RE}",
    multiple=True,
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_ENFORCEMENT_NAMES_ERROR = click.option(
    "--enforcement-names-error/--no-enforcement-names-error",
    "-ene/-nene",
    "enforcement_names_error",
    help="Error if any enforcement_names provided are not valid",
    default=True,
    show_envvar=True,
    show_default=True,
)
OPT_ENFORCEMENT_NAMES_MINIMUM = click.option(
    "--enforcement-names-minimum",
    "-enm",
    "enforcement_names_minimum",
    help="Error if matches for enforcement_names are < this number",
    type=click.INT,
    default=None,
    show_envvar=True,
    show_default=True,
)

OPT_STATUSES = click.option(
    "--statuses",
    "-st",
    "statuses",
    help=f"Only get tasks that have the provided statuses {_RE}",
    multiple=True,
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_STATUSES_ERROR = click.option(
    "--statuses-error/--no-statuses-error",
    "-ste/-note",
    "statuses_error",
    help="Error if any statuses provided are not valid",
    default=True,
    show_envvar=True,
    show_default=True,
)
OPT_STATUSES_MINIMUM = click.option(
    "--statuses-minimum",
    "-stm",
    "statuses_minimum",
    help="Error if matches for statuses are < this number",
    type=click.INT,
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_STATUSES_RESULT = click.option(
    "--statuses-result",
    "-sr",
    "statuses_result",
    help=f"Only get tasks that have the provided result statuses {_RE}",
    multiple=True,
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_STATUSES_RESULT_ERROR = click.option(
    "--statuses-result-error/--no-statuses-result-error",
    "-sre/-nsre",
    "statuses_result_error",
    help="Error if any result statuses provided are not valid",
    default=True,
    show_envvar=True,
    show_default=True,
)
OPT_STATUSES_RESULT_MINIMUM = click.option(
    "--statuses-result-minimum",
    "-srm",
    "statuses_result_minimum",
    help="Error if matches for result statuses are < this number",
    type=click.INT,
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_SORT = click.option(
    "--sort",
    "-so",
    "sort",
    help=f"Ask REST API to sort tasks on this attribute {_DASH}",
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_ROW_START = click.option(
    "--row-start",
    "-rt",
    "row_start",
    help="Row to start on",
    type=click.INT,
    default=PagingState.row_start,
    show_envvar=True,
    show_default=True,
)
OPT_ROW_STOP = click.option(
    "--row-stop",
    "-rs",
    "row_stop",
    help="Row to stop on",
    type=click.INT,
    default=PagingState.row_stop,
    show_envvar=True,
    show_default=True,
)
OPT_PAGE_SIZE = click.option(
    "--page-size",
    "-ps",
    "page_size",
    help="Number of rows to get per page",
    type=click.INT,
    default=PagingState.page_size,
    show_envvar=True,
    show_default=True,
)
OPT_RE_PREFIX = click.option(
    "--re-prefix",
    "-re",
    "re_prefix",
    help=(
        "Any strings provided to action_type, discovery_uuids, enforcement_names,"
        "statuses, or statuses_result that start with this value will be treated as a regex pattern"
    ),
    default=RE_PREFIX,
    show_envvar=True,
    show_default=True,
)
OPT_SPLIT = click.option(
    "--split/--no-split",
    "-sp/-nsp",
    "split",
    help="Split strings provided to filters using split_sep",
    default=True,
    show_envvar=True,
    show_default=True,
)
OPT_SPLIT_SEP = click.option(
    "--split-sep",
    "-ss",
    "split_sep",
    help="Split strings provided to filters using this separator",
    default=SPLITTER,
    show_envvar=True,
    show_default=True,
)
OPT_STRIP = click.option(
    "--strip/--no-strip",
    "-st/-nst",
    "strip",
    help="Strip strings provided to filters",
    default=True,
    show_envvar=True,
    show_default=True,
)
OPT_ECHO = click.option(
    "--echo/--no-echo",
    "-e/-ne",
    "echo",
    help="Echo fetch messages to console.",
    default=True,
    show_envvar=True,
    show_default=True,
)
OPT_EXPLODE = click.option(
    "--explode/--no-explode",
    "-ex/-nex",
    "explode",
    help=(
        "Explode each result for each task into individual rows "
        "(defaults per --export-format json:False, jsonl:False, csv:True)"
    ),
    default=None,
    show_envvar=True,
    show_default=True,
)
OPT_SCHEMAS = click.option(
    "--schemas/--no-schemas",
    "-sc/-nsc",
    "schemas",
    help=(
        "Include schema definitions for each task and result attribute "
        "(defaults per --export-format json:False, jsonl:False, csv:True)"
    ),
    default=None,
    show_envvar=True,
    show_default=True,
)
OPTS_FILTERS = [
    OPT_ACTION_TYPES,
    OPT_ACTION_TYPES_ERROR,
    OPT_ACTION_TYPES_MINIMUM,
    OPT_DATE_FROM,
    OPT_DATE_FROM_ADD,
    OPT_DATE_FROM_SUBTRACT,
    OPT_DATE_TO,
    OPT_DATE_TO_ADD,
    OPT_DATE_TO_SUBTRACT,
    OPT_DISCOVERY_UUIDS,
    OPT_DISCOVERY_UUIDS_ERROR,
    OPT_DISCOVERY_UUIDS_MINIMUM,
    OPT_DURATION_OPERATOR,
    OPT_DURATION_SECONDS,
    OPT_ENFORCEMENT_NAMES,
    OPT_ENFORCEMENT_NAMES_ERROR,
    OPT_ENFORCEMENT_NAMES_MINIMUM,
    OPT_RE_PREFIX,
    OPT_SPLIT,
    OPT_SPLIT_SEP,
    OPT_STRIP,
    OPT_SORT,
    OPT_STATUSES,
    OPT_STATUSES_ERROR,
    OPT_STATUSES_MINIMUM,
    OPT_STATUSES_RESULT,
    OPT_STATUSES_RESULT_ERROR,
    OPT_STATUSES_RESULT_MINIMUM,
    OPT_TASK_ID,
]

OPTS_EXPORT = [
    OPT_PAGE_SIZE,
    OPT_ROW_START,
    OPT_ROW_STOP,
    OPT_EXPLODE,
    OPT_SCHEMAS,
    OPT_EXPORT_FORMAT,
    OPT_EXPORT_FILE,
    OPT_EXPORT_OVERWRITE,
    OPT_ECHO,
]

OPTIONS = [*AUTH, *OPTS_FILTERS, *OPTS_EXPORT]
