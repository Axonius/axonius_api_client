# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...api.json_api.enforcements import ActionCategory, EnforcementDefaults, EnforcementSchedule
from ...api.json_api.saved_queries import QueryTypes
from ...parsers.tables import tablize
from ...tools import json_dump
from ..context import click

OPT_RECURRENCE_DAILY = click.option(
    "--recurrence",
    "-r",
    "recurrence",
    help="Set schedule to run every N days (N = int 1-~), ex: '7'",
    required=True,
    show_envvar=True,
    show_default=True,
)
OPT_RECURRENCE_HOURLY = click.option(
    "--recurrence",
    "-r",
    "recurrence",
    help="Set schedule to run every N hours (N = int 1-24), ex: '4'",
    required=True,
    show_envvar=True,
    show_default=True,
)
OPT_RECURRENCE_WEEKLY = click.option(
    "--recurrence",
    "-r",
    "recurrence",
    help="Set schedule to run on N days of week (N = int 0-6 or day of week), ex: '0,wednesday'",
    required=True,
    show_envvar=True,
    show_default=True,
)
OPT_RECURRENCE_MONTHLY = click.option(
    "--recurrence",
    "-r",
    "recurrence",
    help="Set schedule to run on N days of month (N = int 1-29), ex: '1,4,29'",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_UPDATE_BOOL = click.option(
    "--enable/--disable",
    "-e/-d",
    "update",
    required=True,
    help="Enable/disable option",
    show_envvar=True,
    show_default=True,
)
OPT_USE_CONDITIONS = click.option(
    "--use-conditions/--no-use-conditions",
    "-uc/-nuc",
    "use_conditions",
    default=False,
    help="Use conditions configured on enforcement set to determine execution",
    show_envvar=True,
    show_default=True,
)
OPT_ERROR = click.option(
    "--error/--no-error",
    "-err/-nerr",
    "error",
    default=True,
    help="Throw error if an enforcement set has no trigger",
    show_envvar=True,
    show_default=True,
)


OPT_UPDATE_INT = click.option(
    "--int",
    "-i",
    "update",
    required=True,
    help="Integer to assign to option ('none' for None)",
    show_envvar=True,
    show_default=True,
)


OPT_SET_VALUE_OPT = click.option(
    "--value",
    "-v",
    "value",
    help="Name or UUID of Enforcement Set",
    required=False,
    show_envvar=True,
    show_default=True,
)
OPT_SET_VALUE_REQ = click.option(
    "--value",
    "-v",
    "value",
    help="Name or UUID of Enforcement Set",
    required=True,
    show_envvar=True,
    show_default=True,
)
OPT_SET_VALUES_REQ = click.option(
    "--value",
    "-v",
    "values",
    help="Name or UUID of Enforcement Set (multiple)",
    required=True,
    multiple=True,
    show_envvar=True,
    show_default=True,
)

OPT_ACTION_VALUE_OPT = click.option(
    "--value",
    "-v",
    "value",
    help="Name or UUID of Action Type",
    required=False,
    show_envvar=True,
    show_default=True,
)


OPT_NEW_NAME = click.option(
    "--name",
    "-n",
    "name",
    help="New Name to assign",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_COPY_TRIGGERS = click.option(
    "--copy-triggers/--no-copy-triggers",
    "-ct/-nct",
    "copy_triggers",
    default=True,
    help="Include triggers in copy",
    show_envvar=True,
    show_default=True,
)

OPT_ACTION_CATEGORY = click.option(
    "--category",
    "-cat",
    "category",
    help="Action Category",
    type=click.Choice(ActionCategory.keys()),
    required=True,
    show_envvar=True,
    show_default=True,
)
OPT_ACTION_NAME = click.option(
    "--name",
    "-an",
    "name",
    help="Name of the Action",
    required=True,
    show_envvar=True,
    show_default=True,
)
OPTS_SCHEDULE_TIME = [
    click.option(
        "--schedule-hour",
        "-sh",
        "hour",
        help="Hour to use for schedule",
        default=EnforcementDefaults.schedule_hour,
        type=click.INT,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--schedule-minute",
        "-sm",
        "minute",
        help="Minute to use for schedule",
        default=EnforcementDefaults.schedule_minute,
        type=click.INT,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
]
OPTS_ACTION_ADD = [
    OPT_ACTION_NAME,
    click.option(
        "--type",
        "-at",
        "action_type",
        help="Type of Action",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--config",
        "-ac",
        "config",
        help="JSON file with the configuration for the Action",
        required=True,
        default="-",
        type=click.File(mode="r"),
        show_envvar=True,
        show_default=True,
    ),
]
OPTS_UPDATE_QUERY = [
    click.option(
        "--query-name",
        "-qn",
        "query_name",
        help="Name of Saved Query to use for trigger",
        default=EnforcementDefaults.query_name,
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--query-type",
        "-qt",
        "query_type",
        help="Type of Saved Query to use for trigger",
        type=click.Choice(QueryTypes.keys()),
        default=EnforcementDefaults.query_type,
        required=True,
        show_envvar=True,
        show_default=True,
    ),
]
OPTS_CREATE = [
    OPT_NEW_NAME,
    click.option(
        "--description",
        "-desc",
        "description",
        help="Description for Set",
        default="",
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--main-action-name",
        "-man",
        "main_action_name",
        help="Name of the Main Action",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--main-action-type",
        "-mat",
        "main_action_type",
        help="Type of action for the Main Action",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--main-action-config",
        "-mac",
        "main_action_config",
        help="JSON file with the configuration for the Main Action",
        required=True,
        default="-",
        type=click.File(mode="r"),
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--query-name",
        "-qn",
        "query_name",
        help="Name of Saved Query to use for trigger",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--query-type",
        "-qt",
        "query_type",
        help="Type of Saved Query to use for trigger",
        type=click.Choice(QueryTypes.keys()),
        default=EnforcementDefaults.query_type,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--schedule-type",
        "-st",
        "schedule_type",
        help="Type of Schedule to use for trigger",
        default=EnforcementDefaults.schedule_type,
        type=click.Choice(EnforcementSchedule.keys()),
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--schedule-hour",
        "-sh",
        "schedule_hour",
        help="Hour to use for schedule",
        default=EnforcementDefaults.schedule_hour,
        type=click.INT,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--schedule-minute",
        "-sm",
        "schedule_minute",
        help="Minute to use for schedule",
        default=EnforcementDefaults.schedule_minute,
        type=click.INT,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--schedule-recurrence",
        "-sr",
        "schedule_recurrence",
        help=(
            "Recurrence of schedule type: hourly (int 1-24), daily (int 1-~), "
            "weekly (CSV of days as int 0-6 or day names), monthly (CSV of days as int 1-29)"
        ),
        default=EnforcementDefaults.schedule_recurrence,
        required=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--only-new-assets/--no-only-new-assets",
        "-ona/-nona",
        "only_new_assets",
        default=EnforcementDefaults.only_new_assets,
        help="Configure trigger to only run against new assets",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--on-count-increased/--no-on-count-increased",
        "-oci/-noci",
        "on_count_increased",
        default=EnforcementDefaults.on_count_increased,
        help="Configure trigger to only run when Saved Query asset count increases",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--on-count-decreased/--no-on-count-decreased",
        "-ocd/-nocd",
        "on_count_decreased",
        default=EnforcementDefaults.on_count_decreased,
        help="Configure trigger to only run when Saved Query asset count decreases",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--on-count-above",
        "-oca",
        "on_count_above",
        default=EnforcementDefaults.on_count_above,
        help="Configure trigger to only run when Saved Query asset count is above this number",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--on-count-below",
        "-ocb",
        "on_count_below",
        default=EnforcementDefaults.on_count_below,
        help="Configure trigger to only run when Saved Query asset count is below this number",
        show_envvar=True,
        show_default=True,
    ),
]


def export_set_json(data, **kwargs):
    """Pass."""
    return json_dump(data)


def export_set_table(data, **kwargs):
    """Pass."""
    items = [x.to_tablize() for x in data] if isinstance(data, list) else [data.to_tablize()]
    return tablize(items)


def export_set_str(data, **kwargs):
    """Pass."""
    items = [str(x) for x in data] if isinstance(data, list) else [str(data)]
    return "\n\n".join(items)


EXPORT_FORMATS: dict = {
    "table": export_set_table,
    "json": export_set_json,
    "str": export_set_str,
}

OPT_EXPORT_FORMAT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(list(EXPORT_FORMATS)),
    help="Format of to export data in",
    default=list(EXPORT_FORMATS)[0],
    show_envvar=True,
    show_default=True,
)
