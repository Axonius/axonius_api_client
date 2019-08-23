# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import click

from . import context

# from .. import tools


# jdump = context.jdump
# jpretty = context.jpretty
# crjoin = context.crjoin
# is_type = tools.is_type


@click.command("get", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--query",
    help="Query built from Query Wizard to filter objects (empty returns all).",
    metavar="QUERY",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--field",
    help="Field (column) to include in the format of adapter:field.",
    callback=context.cb_fields,
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--default-fields/--no-default-fields",
    default=True,
    help="Include default fields for this object type.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--all-generic/--no-all-generic",
    default=False,
    help="Ignore --field and --default-fields and include ALL generic fields.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@context.pass_context
@click.pass_context
def cmd(
    clickctx,
    ctx,
    url,
    key,
    secret,
    export_format,
    export_file,
    export_path,
    export_overwrite,
    query,
    field,
    default_fields,
    all_generic,
):
    """Get all objects matching a query."""
    client = ctx.start_client(url=url, key=key, secret=secret)

    api = getattr(client, clickctx.parent.command.name)

    kwargs = {"query": query}

    if all_generic:
        # kwargs["default_fields"] = False
        kwargs["general"] = ["all"]
    else:
        kwargs["default_fields"] = default_fields
        kwargs.update(field)

    try:
        raw_data = api.get(**kwargs)
    except Exception as exc:
        if ctx.wraperror:
            ctx.echo_error(format(exc))
        raise

    formatters = {"json": ctx.to_json, "csv": ctx.to_csv}

    # d = to_csv(ctx=ctx, raw_data=raw_data)
    # rows = d["rows"]

    ctx.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
    )

    # shellvars = {}
    # shellvars.update(globals())
    # shellvars.update(locals())
    # context.spawn_shell(shellvars=shellvars)
    return ctx


# def jpre(*args):
#     """Pass."""
#     return ".".join([format(x) for x in args if format(x)])


# def complex_flat(item, pre=""):
#     """Pass."""
#     new_item = {}

#     if not is_type.dict(item):
#         print("ITEM NOT DICT {!r}: {}".format(pre, jpretty(item)))
#         return new_item

#     # remove = []

#     for k in list(item):
#         k_pre = jpre(pre, k)
#         # print("in item {!r}".format(k))

#         if is_type.simple(item[k]):
#             v = item.pop(k)
#             # print("is_simple {!r} {!r}".format(k_pre, item[k]))
#             new_item[k_pre] = crjoin(v)
#             continue

#         if is_type.list_of_simple(item[k]):
#             v = item.pop(k)
#             print("is_list_of_simple {!r} {!r}".format(k_pre, v))
#             new_item[k_pre] = crjoin(v)
#             continue

#         if is_type.dict(item[k]):
#             print("is_dict {!r} {!r}".format(k_pre, item[k]))
#             new_item[k_pre] = complex_flat(item[k], pre=k_pre)
#             if not item[k]:
#                 item.pop(k)
#             continue

#         if is_type.list_of_dict(item[k]):
#             # print("is_list_of_dict {!r} {!r}".format(k, item[k]))
#             for idx, sub_item in enumerate(item[k]):
#                 sub_item_pre = jpre(k_pre, idx)
#                 new_sub_item = complex_flat(sub_item, pre=sub_item_pre)
#                 new_item.update(new_sub_item)
#                 # jdump(sub_item)
#                 # basics = handle_dict_basics(sub_item, pre=sub_item_pre)
#                 # new_item.update(basics)

#                 # for sub_k, sub_v in sub_item.items():
#                 #     sub_k_pre = jpre(sub_item_pre, sub_k)
#                 #     # sub_basics = handle_dict_basics(sub_v, pre=sub_k_pre)
#                 #     sub_lod = complex_flat(sub_v, pre=sub_k_pre)
#                 #     # jdump(sub_lod)
#                 #     # new_item.update(sub_basics)
#                 #     new_item.update(sub_lod)
#                 #     # jdump({"sub_k_pre": sub_k_pre, "sub_v": sub_v})
#             # item[k] = [x for x in v if x in [{}, []]]
#             continue

#         print("is_nothing {!r} {!r}".format(k_pre, item[k]))
#         # if tools.is_list_of_list_of_simple(item[k]):
#         #     print("ITEM IS LOLS: {!r} {}".format(k_pre, jpretty(item[k])))
#         # for idx, sub_item in enumerate(v):
#         #     if tools.is_list_of_simple(sub_item, or_simple=True, or_none=True):
#         #         remove.append(k)

#         # item[k] = [x for x in v if x in [{}, []]]

#     # for k in list(item):
#     #     if item[k] in [[], {}] or k in remove:
#     #         item.pop(k)

#     return new_item


# def to_csv(ctx, raw_data):
#     """Pass."""
#     rows = []
#     headers = []

#     for raw_row in raw_data:
#         # basics = handle_dict_basics(raw_row)
#         # found_headers = list(basics) + list(lod)
#         # row = {}
#         # row.update(basics)

#         row = complex_flat(raw_row)
#         headers += [x for x in row if x not in headers]
#         rows.append(row)

#     return {"rows": rows, "headers": headers}
