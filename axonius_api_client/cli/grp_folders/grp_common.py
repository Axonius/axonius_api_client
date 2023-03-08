# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...constants.api import TABLE_FORMAT, FolderDefaults
from ...parsers.tables import tablize
from ...tools import json_dump, listify, path_write


def search_export_str(data, **kwargs):
    """Pass."""
    return f"\n{'-' * 60}\n".join(str(x) for x in listify(data))


def search_export_json(data, **kwargs):
    """Pass."""
    return json_dump(listify(data))


def search_export_jsonl(data, **kwargs):
    """Pass."""
    return "\n".join([json_dump(x, indent=None) for x in listify(data)])


def search_export_table(data, table_format=TABLE_FORMAT, **kwargs):
    """Pass."""
    return tablize(value=[x.to_tablize() for x in listify(data)], fmt=table_format)


def search_export_folder(data, include_details=FolderDefaults.include_details, **kwargs):
    """Pass."""
    return "\n".join([x.get_tree_entry(include_details=include_details) for x in listify(data)])


SEARCH_EXPORTS = {
    "folder": search_export_folder,
    "table": search_export_table,
    "json": search_export_json,
    "jsonl": search_export_jsonl,
    "str": search_export_str,
}
SEARCH_EXPORT_DEFAULT = "table"


def handle_export_search(
    apiobj,
    folder,
    objs,
    export_format=SEARCH_EXPORT_DEFAULT,
    export_file="",
    export_overwrite=False,
    echo=True,
    **kwargs,
):
    """Pass."""
    output = SEARCH_EXPORTS[export_format](data=objs, **kwargs)
    desc = f"{len(objs)} search results"
    size = len(output)
    msgs = [
        f"Exporting {desc}",
        f"Folder: {folder}",
        f"--export-file: {export_file!r}",
        f"--export-format: {export_format!r}",
        f"Output bytes: {size}",
    ]
    folder.spew(msgs, echo=echo)

    if export_file:
        path, _ = path_write(obj=export_file, data=output, overwrite=export_overwrite)
        folder.spew(f"Finished writing {desc} to --export-path: {str(path)}", echo=echo)
    else:
        click.secho(output)
        folder.spew(f"Finished writing {desc} to STDOUT", echo=echo)
    folder.spew(f"Search Path: {folder.path}", echo=echo)
