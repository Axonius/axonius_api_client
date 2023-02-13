# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import echo_error, echo_ok
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, DEFAULT_PATH, add_options
from .grp_common import OPT_CHARTS, OPT_SEP, OPT_SPACES

OPT_ERROR = click.option(
    "--error/--no-error",
    "-e/-ne",
    "error",
    default=False,
    help="Raise an error if any CSV export fails",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
OPT_PATH = click.option(
    "--path",
    "-p",
    "path",
    default=DEFAULT_PATH,
    help="Path to write CSV export files to (default==CWD)",
    type=click.Path(exists=False, resolve_path=True),
    show_envvar=True,
    show_default=True,
)


OPTIONS = [
    *AUTH,
    OPT_SEP,
    OPT_ERROR,
    OPT_SPACES,
    OPT_CHARTS,
    OPT_PATH,
]


@click.command(name="export-charts-to-csv", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Export Multiple Charts to CSV."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = client.dashboard_spaces

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        results = apiobj.export_charts_to_csv_path(**kwargs)
        for result in results:
            chart, data, path = result
            if "export_chart_csv_error" in data.splitlines()[0]:
                echo_method = echo_error
                msg = "errors"
            else:
                echo_method = echo_ok
                msg = "no errors"
            echo_method(f"{path.name} written with {msg}", abort=False)
