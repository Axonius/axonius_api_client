# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import dataclasses
from typing import Any, Callable, List, Optional

from ....api import json_api
from ....api.assets.asset_mixin import AssetMixin
from ....tools import json_reload, listify
from ...context import CONTEXT_SETTINGS, click
from ...options import ABORT, AUTH, INPUT_FILE, add_options
from .grp_common import EXPORT_FORMATS, OPT_OVERWRITE, OPTS_EXPORT

OPTIONS = [
    *AUTH,
    *OPTS_EXPORT,
    ABORT,
    OPT_OVERWRITE,
    INPUT_FILE,
]


@click.command(name="add-from-json", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, input_file, overwrite, export_format, table_format, abort):
    """Add saved queries from a JSON file."""
    rows = listify(ctx.obj.read_stream_json(stream=input_file, expect=(list, dict)))

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)
    handle_updates(
        rows=rows,
        input_file=input_file,
        ctx=ctx,
        apiobj=apiobj,
        abort=abort,
        overwrite=overwrite,
        export_format=export_format,
        table_format=table_format,
        parse_method=json_api.saved_queries.SavedQueryCreate.new_from_kwargs,
    )


def handle_updates(
    rows, input_file, ctx, apiobj, abort, overwrite, export_format, table_format, parse_method
):
    """Pass."""
    failure = []
    success = []

    for idx, row in enumerate(rows):
        state = State(
            idx=idx,
            row=row,
            total=len(rows),
            input_file=input_file,
            ctx=ctx,
            apiobj=apiobj,
            abort=abort,
            overwrite=overwrite,
            parse_method=parse_method,
        )
        target = failure if state.error else success
        target.append(state)

    if failure:
        txt = "\n" + "\n".join([f"{x}: {x.error}" for x in failure])
        ctx.obj.echo_warn(f"Rows with errors:{txt}")

    if not success:
        ctx.obj.echo_warn("No changes made!")
    else:
        txt = "\n" + "\n".join([f"{x}: {x.result}" for x in success])
        ctx.obj.echo_ok(f"Exporting successfully modified Saved Queries:{txt}")
        click.secho(
            EXPORT_FORMATS[export_format](data=[x.obj for x in success], table_format=table_format)
        )

    ctx.exit(100 if failure or not success else 0)


@dataclasses.dataclass
class State:
    """Pass."""

    idx: int
    row: Any
    total: int
    input_file: str
    ctx: click.Context
    apiobj: AssetMixin
    abort: bool
    overwrite: bool
    parse_method: Callable

    msgs: List[str] = dataclasses.field(default_factory=list)
    error: str = ""
    exc: Optional[Exception] = None
    obj_parsed: Optional[json_api.saved_queries.SavedQueryCreate] = None
    obj: Optional[json_api.saved_queries.SavedQuery] = None
    result: str = ""

    @property
    def name(self) -> Optional[str]:
        """Pass."""
        return self.row.get("name") if isinstance(self.row, dict) else None

    def __str__(self) -> str:
        """Pass."""
        return f"supplied row #{self.idx + 1}/{self.total} name={self.name!r}"

    @property
    def file_name(self) -> str:
        """Pass."""
        return getattr(self.input_file, "name", self.input_file)

    def failure(self, msg: str, exc: Optional[Exception] = None, obj: Optional[Any] = None):
        """Pass."""
        self.exc = exc
        self.error = msg
        self.result = "FAILURE"
        self.msgs.append(msg)

        if not self.ctx.obj.wraperror and exc:  # pragma: no cover
            raise

        msgs = [f"While working on {self}: {msg}"]
        msgs += self.objinfo(obj=obj)
        msgs += self.objinfo(obj=exc, src="Exception")
        self.ctx.obj.echo_error(msg="\n  ".join(msgs), abort=self.abort)

    def objinfo(self, obj: Any, src: str = "Object") -> List[str]:
        """Pass."""
        return (
            [f"{src} type: {type(obj)}", f"{src} details:", *f"{obj}".splitlines()] if obj else []
        )

    def debug(self, msg: str):
        """Pass."""
        self.msgs.append(msg)
        msg = f"{self}: {msg}"
        self.ctx.obj.echo_debug(msg=msg)

    def success(self, msg: str, result: str):
        """Pass."""
        self.result = result.upper()
        self.msgs.append(msg)

        msgs = [f"Finished working on {self}: {msg}"]
        msgs += self.objinfo(obj=self.obj)
        self.ctx.obj.echo_ok(msg="\n  ".join(msgs))

    def __post_init__(self):
        """Pass."""
        msgs = [
            f"Start parsing supplied row from {self.file_name}",
            "Supplied row:",
            json_reload(self.row),
        ]
        self.debug("\n".join(msgs))

        try:
            self.obj_parsed = self.parse_method(**self.row)
        except Exception as exc:
            self.failure(msg="Initial parsing of supplied row failed", obj=self.row, exc=exc)
            return

        self.debug("Initial parsing of supplied row successful")

        existing = self.existing_by_name.get(self.obj_parsed.name)
        msg_exist = f"Saved Query exists={bool(existing)} and overwrite={self.overwrite}"

        if existing:
            if not self.overwrite:
                self.failure(msg=f"{msg_exist}, can not update", obj=existing)
                return

            self.debug(f"{msg_exist}, will update")
            try:
                self.obj = self.apiobj.saved_query._update_from_dataclass(
                    obj=self.obj_parsed, uuid=existing.uuid
                )
            except Exception as exc:
                self.failure(msg="Update failed", exc=exc, obj=self.obj_parsed)
                return

            self.success(msg="Update succeeded", result="updated")
            return
        else:
            self.debug(f"{msg_exist}, will create")

        try:
            self.obj = self.apiobj.saved_query._add_from_dataclass(obj=self.obj_parsed)
        except Exception as exc:
            self.failure(msg="Create failed", exc=exc, obj=self.obj_parsed)
            return

        self.success(msg="Create succeeded", result="created")
        return

    @property
    def existing_by_name(self) -> dict:
        """Pass."""
        with self.ctx.obj.exc_wrap(wraperror=self.ctx.obj.wraperror, abort=True):
            return {x.name: x for x in self.apiobj.saved_query.get(as_dataclass=True)}
