# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import csv

from ....tools import join_kv
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, INPUT_FILE, add_options
from .grp_common import EXPORT, handle_export

CONTINUE_ON_ERROR = click.option(
    "--continue-on-error/--no-continue-on-error",
    "-coe/-ncoe",
    "continue_on_error",
    help="Continue creating users if one has an error",
    default=False,
    is_flag=True,
    show_envvar=True,
    show_default=True,
    required=False,
)


OPTIONS = [*AUTH, INPUT_FILE, EXPORT, CONTINUE_ON_ERROR]
REQUIRED_COLUMNS = [
    "name",
    "role_name",
    "first_name",
    "last_name",
    "password",
    "email",
    "generate_password_link",
    "email_password_link",
]
REQUIRED_VALUES = ["name", "role_name"]
BOOL_COLUMNS = ["generate_password_link", "email_password_link"]

""" XXX
axonshell -nw system users add -n asdojfkasdfoasda -epl --email jim@axonius.com -r Viewer
add examples help
"""  # noqa


@click.command(name="add-from-csv", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, input_file, continue_on_error, **kwargs):
    """Add users from a CSV file."""
    reader = csv.DictReader(input_file)
    echo = ctx.obj.echo_warn if continue_on_error else ctx.obj.echo_error

    missing_columns = [x for x in REQUIRED_COLUMNS if x not in reader.fieldnames]
    if missing_columns:
        miss = ", ".join(missing_columns)
        ctx.obj.echo_error(f"CSV is missing required columns: {miss}")

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    users = []
    found_rows = False
    for idx, row in enumerate(reader):
        found_rows = True
        name = row.get("name")
        for bool_column in BOOL_COLUMNS:
            bool_value = str(row.get(bool_column, "")).lower().strip()
            row[bool_column] = bool_value in ["yes", "true", "y"]

        rowi = f"row {idx + 2}"
        rowj = "\n   " + "\n   ".join(join_kv(obj=row))
        fail = f"Failed to add user in {rowi}:{rowj}\n\n   ===>"

        missing_values = [x for x in REQUIRED_VALUES if not row.get(x)]
        if missing_values:
            miss = ", ".join(missing_values)
            echo(f"{fail} Missing required values for columns: {miss}\n")
            continue

        try:
            user = client.system.users.add(**row)
            users.append(user)
            ctx.obj.echo_ok(f"Successfully created user {name} in {rowi}\n")
        except Exception as exc:
            client.LOG.exception(fail)
            echo(f"{fail} {exc}\n")

    if not found_rows:
        ctx.obj.echo_error("CSV has no rows!")

    handle_export(ctx=ctx, data=users, export_format=export_format, **kwargs)
