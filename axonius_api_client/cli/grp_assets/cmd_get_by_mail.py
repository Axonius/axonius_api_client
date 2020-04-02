# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import click

from .. import cli_constants, options
from . import grp_common


@click.command(name="get-by-mail", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT
@options.OPT_EXPORT_OVERWRITE
@options.OPT_EXPORT_DELIM
@options.OPT_EXPORT_TABLE_FORMAT
@options.OPT_FIELDS
@options.OPT_FIELDS_REGEX
@options.OPT_FIELDS_DEFAULT
@options.OPT_MAX_ROWS
@options.OPT_PAGE_START
@options.OPT_PAGE_SIZE
@options.OPT_GET_BY_PRE_QUERY
@options.OPT_GET_BY_POST_QUERY
@options.OPT_GET_BY_VALUE_NOT
@options.OPT_GET_BY_VALUE_REGEX
@options.OPT_GET_BY_VALUES
@options.OPT_FIELD_NULLS
@options.OPT_FIELD_EXCLUDES
@click.pass_context
def cmd(ctx, **kwargs):
    """Get assets with matching email addresses."""
    grp_common.get_by_cmd(ctx=ctx, method="get_by_mail", **kwargs)
