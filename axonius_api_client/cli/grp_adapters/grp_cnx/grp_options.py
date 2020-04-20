# # -*- coding: utf-8 -*-
# """Command line interface for Axonius API Client."""
# from ...context import click
# from ...options import AUTH, NODE_CNX, SPLIT_CONFIG_OPT  # , CONTENTS,

# EXPORT = click.option(
#     "--export-format",
#     "-xf",
#     "export_format",
#     type=click.Choice(
#         ["json-full", "json-config", "json", "table", "table-schemas", "str", "str-args"]
#     ),
#     help="Format of to export data in",
#     default="json-config",
#     show_envvar=True,
#     show_default=True,
# )

# PROMPT_OPT = click.option(
#     "--prompt-optional / --no-prompt-optional",
#     "-po / -npo",
#     "prompt_optional",
#     help="Prompt for optional items that are not supplied.",
#     is_flag=True,
#     default=True,
#     show_envvar=True,
#     show_default=True,
# )
# PROMPT_DEF = click.option(
#     "--prompt-default / --no-prompt-default",
#     "-pd / -npd",
#     "prompt_default",
#     help="Prompt for items that have a default.",
#     is_flag=True,
#     default=True,
#     show_envvar=True,
#     show_default=True,
# )

# ADD = [
#     *AUTH,
#     EXPORT,
#     *NODE_CNX,
#     PROMPT_OPT,
#     PROMPT_DEF,
#     SPLIT_CONFIG_OPT,
# ]


# GET = [
#     *AUTH,
#     EXPORT,
#     *NODE_CNX,
# ]


# GET = [
#     *AUTH,
#     EXPORT,
#     *NODE_CNX,
# ]

# GET_BY_ID = [
#     *GET,
#     click.option(
#         "--id",
#         "-i",
#         "cnx_id",
#         help="ID of connection",
#         required=True,
#         show_envvar=True,
#         show_default=True,
#     ),
# ]
