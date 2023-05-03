# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...constants.fields import AXID
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

OPTS_GRABBER = [
    click.option(
        "--path",
        "-p",
        "path",
        help="path to file to grab Asset IDs from",
        required=True,
        show_envvar=True,
    ),
    click.option(
        "--grab-key",
        "-gk",
        "keys",
        help=(
            "Additional keys/columns to look for Asset IDs (multiple, csv-able) "
            f"[always checks keys: {AXID.keys}]"
        ),
        required=False,
        multiple=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--do-raise-grab/--no-raise-grab",
        "-drg/-nrg",
        "do_raise_grab",
        default=False,
        help="Raise an error if grabber fails to find an Asset ID in any item",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--do-echo-grab/--no-echo-grab",
        "-deg/-neg",
        "do_echo_grab",
        default=True,
        help="Echo Asset ID grabber output to console",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--check-stdin/--no-check-stdin",
        "-cs/-ncs",
        "check_stdin",
        default=True,
        help="Check that STDIN is a TTY when prompting",
        show_envvar=True,
        show_default=True,
    ),
]

OPTS_RUNNER = [
    click.option(
        "--eset",
        "-e",
        "eset",
        help="Name or UUID of Enforcement Set",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--verified/--no-verified",
        "-ve/-nve",
        "verified",
        default=False,
        help="$ids already verified, just run $eset against $ids",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--verify_count/--no-verify_count",
        "-vc/-nvc",
        "verify_count",
        default=True,
        help=(
            'Build a query like ("internal_axon_id" in [$ids_csv]) and verify that the count of '
            "query equals the count of Asset IDs grabbed from $path"
        ),
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--prompt/--no-prompt",
        "-ve/-nve",
        "prompt",
        default=True,
        help="Prompt user for verification when verifying count",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--do-echo/--no-echo",
        "-de/-ne",
        "do_echo",
        default=True,
        help="Echo $eset verifier & runner output to console",
        show_envvar=True,
        show_default=True,
    ),
]

OPTIONS = [
    *AUTH,
    *OPTS_GRABBER,
    *OPTS_RUNNER,
]

EPI_JSON: str = """
\b
# Notes:
# 1) --path must be a JSON file containing a list of dictionaries

\b
# Example:
# 1) Get assets in JSON format:
axonshell devices get --export-format json --export-file data.json --export-overwrite --wiz simple 'os.type equals windows'
# 2) Run an enforcement set against the asset IDs in the JSON file:
# 2a) prompting to verify the count:
axonshell devices run-enforcement-from-json --path data.json --eset test
# 2b) With no prompting (will error out if the count mismatches):
axonshell devices run-enforcement-from-json --path data.json --eset test --no-prompt
# 2c) With no verification because we know the asset IDs are valid for this instance:
axonshell devices run-enforcement-from-json --path data.json --eset test --verified
"""  # noqa

EPI_JSONL: str = """
\b
# Notes:
# 1) --path must be a JSONL file with one dictionary per line

\b
# Example:
# 1) Get assets in JSONL format:
axonshell devices get --export-format json --json-flat --export-file data.jsonl --export-overwrite --wiz simple 'os.type equals windows'
# 2) Run an enforcement set against the asset IDs in the JSON file:
# 2a) prompting to verify the count:
axonshell devices run-enforcement-from-jsonl --path data.jsonl --eset test
# 2b) With no prompting (will error out if the count mismatches):
axonshell devices run-enforcement-from-jsonl --path data.jsonl --eset test --no-prompt
# 2c) With no verification because we know the asset IDs are valid for this instance:
axonshell devices run-enforcement-from-jsonl --path data.jsonl --eset test --verified
"""  # noqa


EPI_CSV: str = """
\b
# Notes:
# 1) --path must be a CSV file with headers
# 2) --path can also be a CSV file exported from the GUI.

\b
# Example:
# 1) Get assets in CSV format:
axonshell devices get --export-format csv --export-file data.csv --export-overwrite --wiz simple 'os.type equals windows'
# 2) Run an enforcement set against the asset IDs in the CSV file:
# 2a) prompting to verify the count:
axonshell devices run-enforcement-from-csv --path data.csv --eset test
# 2b) With no prompting (will error out if the count mismatches):
axonshell devices run-enforcement-from-csv --path data.csv --eset test --no-prompt
# 2c) With no verification because we know the asset IDs are valid for this instance:
axonshell devices run-enforcement-from-csv --path data.csv --eset test --verified
"""  # noqa

EPI_TEXT: str = """
\b
# Notes:
# 1) --path must be a text file with valid asset IDs
# 2) All lines will have any non alpha-numeric characters removed from them and
#   if a 32 character alpha numeric string is found it is considered an Asset ID.

\b
# Example:
# 1) Get assets in JSON format then use jq to extract the IDs to a text file:
axonshell devices get --export-format json --export-file data.json --export-overwrite --wiz simple 'os.type equals windows'
jq '.[].internal_axon_id' data.json > data.txt
# 2) Run an enforcement set against the asset IDs in the text file:
# 2a) prompting to verify the count:
axonshell devices run-enforcement-from-text --path data.txt --eset test
# 2b) With no prompting (will error out if the count mismatches):
axonshell devices run-enforcement-from-text --path data.txt --eset test --no-prompt
# 2c) With no verification because we know the asset IDs are valid for this instance:
axonshell devices run-enforcement-from-text --path data.txt --eset test --verified
"""  # noqa


@click.command(name="run-enforcement-from-json", context_settings=CONTEXT_SETTINGS, epilog=EPI_JSON)
@add_options(OPTIONS)
@click.pass_context
def from_json(ctx, url, key, secret, **kwargs):
    """Grab Asset IDs from a JSON file and run an Enforcement Set against them."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.run_enforcement_from_json_path(**kwargs)
    click.secho(f"{data}")
    ctx.exit(0)


@click.command(
    name="run-enforcement-from-jsonl", context_settings=CONTEXT_SETTINGS, epilog=EPI_JSONL
)
@add_options(OPTIONS)
@click.pass_context
def from_jsonl(ctx, url, key, secret, **kwargs):
    """Grab Asset IDs from a JSONL file and run an Enforcement Set against them."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.run_enforcement_from_jsonl_path(**kwargs)
    click.secho(f"{data}")
    ctx.exit(0)


@click.command(name="run-enforcement-from-csv", context_settings=CONTEXT_SETTINGS, epilog=EPI_CSV)
@add_options(OPTIONS)
@click.pass_context
def from_csv(ctx, url, key, secret, **kwargs):
    """Grab Asset IDs from a CSV file and run an Enforcement Set against them."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.run_enforcement_from_csv_path(**kwargs)
    click.secho(f"{data}")
    ctx.exit(0)


@click.command(name="run-enforcement-from-text", context_settings=CONTEXT_SETTINGS, epilog=EPI_TEXT)
@add_options(OPTIONS)
@click.pass_context
def from_text(ctx, url, key, secret, **kwargs):
    """Grab Asset IDs from any old text file and run an Enforcement Set against them."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.run_enforcement_from_text_path(**kwargs)
    click.secho(f"{data}")
    ctx.exit(0)


CMDS = [from_json, from_jsonl, from_csv, from_text]
