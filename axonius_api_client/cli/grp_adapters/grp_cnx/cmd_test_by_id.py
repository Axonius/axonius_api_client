# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....exceptions import CnxTestError
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_EXPORT, OPT_ID_CNX, OPTS_NODE

OPTIONS = [
    *AUTH,
    *OPTS_NODE,
    OPT_ID_CNX,
    OPT_EXPORT,
]


@click.command(name="test-by-id", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, adapter_name, adapter_node, tunnel, export_format, cnx_id):
    """Test reachability for an existing connection by ID."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    had_error = False
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        cnx = client.adapters.cnx.get_by_id(
            adapter_name=adapter_name,
            adapter_node=adapter_node,
            tunnel=tunnel,
            cnx_id=cnx_id,
        )

        try:
            data = client.adapters.cnx.test_cnx(cnx_test=cnx)
            ctx.obj.echo_ok(msg="Connection tested with no errors")
        except CnxTestError as exc:
            had_error = True
            ctx.obj.echo_error(msg=f"Connection tested with error: {exc}", abort=False)
            data = exc.cnx
            if not ctx.obj.wraperror:  # pragma: no cover
                raise

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(100 if had_error else 0)
