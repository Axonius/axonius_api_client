# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from axonius_api_client.constants.fields import AXID

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


@click.command(
    name="run-enforcement-from-json",
    context_settings=CONTEXT_SETTINGS,
    epilog="--path must be a JSON file containing a list of dictionaries",
)
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
    name="run-enforcement-from-jsonl",
    context_settings=CONTEXT_SETTINGS,
    epilog="--path must be a JSONL file with one dictionary per line",
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


@click.command(
    name="run-enforcement-from-csv",
    context_settings=CONTEXT_SETTINGS,
    epilog="--path must be a CSV file with headers",
)
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


@click.command(
    name="run-enforcement-from-text",
    context_settings=CONTEXT_SETTINGS,
    epilog="--path must be a text file with valid asset IDs",
)
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
