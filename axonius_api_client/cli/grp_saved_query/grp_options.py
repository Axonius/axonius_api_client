# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...constants import GUI_PAGE_SIZES
from ..context import SplitEquals, click
from ..options import (
    AUTH,
    FIELDS_SELECT,
    QUERY,
    SQ_NAME,
    get_option_fields_default,
    int_callback,
)

TAGS = click.option(
    "--tag",
    "-t",
    "tags",
    help="Tags of saved queries",
    required=True,
    multiple=True,
    show_envvar=True,
    show_default=True,
)

ADD = [
    *AUTH,
    *QUERY,
    *FIELDS_SELECT,
    get_option_fields_default(default=False),
    click.option(
        "--tag",
        "-t",
        "tags",
        help="Tags to set for saved query",
        multiple=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--sort-field",
        "-sf",
        "sort_field",
        help="Column to sort data on.",
        metavar="ADAPTER:FIELD",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--sort-ascending",
        "-sd",
        "sort_descending",
        default=True,
        help="Sort --sort-field ascending.",
        is_flag=True,
        show_envvar=True,
    ),
    click.option(
        "--column-filter",
        "-cf",
        "column_filters",
        help="Columns to filter in the format of adapter:field=value.",
        metavar="ADAPTER:FIELD=value",
        type=SplitEquals(),
        multiple=True,
        show_envvar=True,
    ),
    click.option(
        "--gui-page-size",
        "-gps",
        default=format(GUI_PAGE_SIZES[0]),
        help="Number of rows to show per page in GUI.",
        type=click.Choice([format(x) for x in GUI_PAGE_SIZES]),
        callback=int_callback,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--description",
        "-d",
        "description",
        help="Description to set on saved query",
        show_envvar=True,
        show_default=True,
        default=None,
    ),
    SQ_NAME,
]

DELETE_BY_NAME = [
    *AUTH,
    SQ_NAME,
]

DELETE_BY_TAGS = [
    *AUTH,
    TAGS,
]

GET = [
    *AUTH,
    click.option(
        "--schema-type",
        "-st",
        "schema_type",
        type=click.Choice(["full", "basic"]),
        help="Control how much schema information to return",
        default="basic",
        show_envvar=True,
        show_default=True,
    ),
]

GET_BY_NAME = [
    *GET,
    SQ_NAME,
]

GET_BY_TAGS = [*GET, TAGS]

GET_TAGS = AUTH
