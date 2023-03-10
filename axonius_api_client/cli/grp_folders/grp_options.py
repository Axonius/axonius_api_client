# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...constants.api import FolderDefaults
from ..context import click
from ..options import TABLE_FMT
from .grp_common import SEARCH_EXPORT_DEFAULT, SEARCH_EXPORTS

OPT_FOLDER = click.option(
    "--folder",
    "-f",
    "folder",
    help="Path of folder",
    required=False,
    show_envvar=True,
    show_default=True,
)

OPT_FOLDER_GET_TREE = click.option(
    "--folder",
    "-f",
    "folder",
    help="Path of folder to print tree of, defaults to /",
    required=False,
    show_envvar=True,
    show_default=True,
)

OPT_FOLDER_UPDATE = click.option(
    "--folder",
    "-f",
    "folder",
    help="Path of folder to update",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_FOLDER_FIND = click.option(
    "--folder",
    "-f",
    "folder",
    help="Path of folder to find",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_FOLDER_CREATE = click.option(
    "--folder",
    "-f",
    "folder",
    help="Path of folder to create",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_FOLDER_DELETE = click.option(
    "--folder",
    "-f",
    "folder",
    help="Path of folder to delete",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_FOLDER_RENAME = click.option(
    "--folder",
    "-f",
    "folder",
    help="Path of folder to rename",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_FOLDER_MOVE = click.option(
    "--folder",
    "-f",
    "folder",
    help="Path of folder to move",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_FOLDER_SEARCH = click.option(
    "--folder",
    "-f",
    "folder",
    help="Path of folder to search for objects",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_SEARCHES = click.option(
    "--search",
    "-S",
    "searches",
    help="Objects to search for (use --pattern-prefix for regex) (multiple)",
    required=True,
    multiple=True,
    show_envvar=True,
    show_default=True,
)

OPT_PATTERN_PREFIX = click.option(
    "--pattern-prefix",
    "-pp",
    "pattern_prefix",
    default=FolderDefaults.pattern_prefix,
    help="Treat any searches that start with this prefix as a regex",
    show_envvar=True,
    show_default=True,
)

OPT_IGNORE_CASE = click.option(
    "--ignore-case/--no-ignore-case",
    "-ic/-nic",
    "ignore_case",
    default=FolderDefaults.ignore_case,
    help="Ignore case when building patterns.",
    show_envvar=True,
    show_default=True,
)

OPT_ERROR_UNMATCHED = click.option(
    "--error-unmatched/--no-error-unmatched",
    "-eu/-neu",
    "error_unmatched",
    default=FolderDefaults.error_unmatched,
    help="Throw a fit if any searches supplied have no matches.",
    show_envvar=True,
    show_default=True,
)

OPT_ERROR_NO_MATCHES = click.option(
    "--error-no-matches/--no-error-no-matches",
    "-enm/-nenm",
    "error_no_matches",
    default=FolderDefaults.error_no_matches,
    help="Throw a fit if no searches match any objects.",
    show_envvar=True,
    show_default=True,
)

OPT_ERROR_NO_OBJECTS = click.option(
    "--error-no-objects/--no-error-no-objects",
    "-eno/-neno",
    "error_no_objects",
    default=FolderDefaults.error_no_objects,
    help="Throw a fit if no objects exist in --folder.",
    show_envvar=True,
    show_default=True,
)
OPT_RECURSIVE = click.option(
    "--recursive/--no-recursive",
    "-r/-nr",
    "recursive",
    default=FolderDefaults.recursive,
    help="Search for objects recursively under --folder instead of only in --folder.",
    show_envvar=True,
    show_default=True,
)

OPT_ALL_OBJECTS = click.option(
    "--all-objects/--no-all-objects",
    "-all/-nall",
    "all_objects",
    default=FolderDefaults.all_objects,
    help="Search for objects in the entire system instead of only in --folder.",
    show_envvar=True,
    show_default=True,
)

OPT_ECHO = click.option(
    "--echo/--no-echo",
    "-e/-ne",
    "echo",
    default=FolderDefaults.echo_action,
    help="Echo folder workflow messages to console.",
    show_envvar=True,
    show_default=True,
)

OPT_EXPORT_FORMAT_SEARCH = click.option(
    "--export-format",
    "-xt",
    "export_format",
    default=SEARCH_EXPORT_DEFAULT,
    help="Format to output objects in",
    type=click.Choice(list(SEARCH_EXPORTS)),
    show_envvar=True,
    show_default=True,
)
OPT_EXPORT_FILE = click.option(
    "--export-file",
    "-xf",
    "export_file",
    default="",
    help="File to send results to",
    show_envvar=True,
    show_default=True,
    metavar="PATH",
)

OPT_EXPORT_OVERWRITE = click.option(
    "--export-overwrite/--no-export-overwrite",
    "-xo/-nxo",
    "export_overwrite",
    default=False,
    help="If --export-file supplied and it exists, overwrite it",
    show_envvar=True,
    show_default=True,
)

OPT_INCLUDE_DETAILS = click.option(
    "--include-details/--no-include-details",
    "-id/-nid",
    "include_details",
    default=FolderDefaults.include_details,
    help="Show detailed folder/object information in output",
    show_envvar=True,
    show_default=True,
)

OPT_INCLUDE_OBJECTS = click.option(
    "--include-objects/--no-include-objects",
    "-io/-nio",
    "include_objects",
    default=FolderDefaults.include_objects,
    help="Include objects in output",
    show_envvar=True,
    show_default=True,
)

OPT_MAXIMUM_DEPTH = click.option(
    "--maximum-depth",
    "-m",
    "maximum_depth",
    type=click.INT,
    help="Stop printing folders & objects past this depth",
    show_envvar=True,
    show_default=True,
)

OPT_TARGET_SEARCH = click.option(
    "--target",
    "-t",
    "target",
    help="Optional folder to copy objects to, defaults to same folder",
    required=False,
    show_envvar=True,
    show_default=True,
)

OPT_TARGET_MOVE = click.option(
    "--target",
    "-t",
    "target",
    help="Path to move folder to",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_TARGET_RENAME = click.option(
    "--target",
    "-t",
    "target",
    help="New folder name",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_COPY_PREFIX = click.option(
    "--copy-prefix",
    "-cp",
    "copy_prefix",
    default=FolderDefaults.copy_prefix,
    help="Value to prepend to each copied objects name",
    show_envvar=True,
    show_default=True,
)

OPT_CREATE_FOLDER_REQ = click.option(
    "--create/--no-create",
    "-c/-nc",
    "create",
    default=FolderDefaults.create_action,
    help="If --folder does not exist, create it",
    show_envvar=True,
    show_default=True,
)

OPT_CREATE_TARGET_OPT = click.option(
    "--create/--no-create",
    "-c/-nc",
    "create",
    default=FolderDefaults.create_action,
    help="If --target is supplied and does not exist, create it",
    show_envvar=True,
    show_default=True,
)

OPT_CREATE_TARGET_REQ = click.option(
    "--create/--no-create",
    "-c/-n",
    "create",
    default=FolderDefaults.create_action,
    help="If --target does not exist, create it",
    show_envvar=True,
    show_default=True,
)

OPT_CONFIRM = click.option(
    "--confirm/--no-confirm",
    "-c/-nc",
    "confirm",
    default=FolderDefaults.confirm,
    help="Throw a fit if neither confirm nor prompt is True",
    show_envvar=True,
    show_default=True,
)

OPT_PROMPT = click.option(
    "--prompt/--no-prompt",
    "-p/-np",
    "prompt",
    default=FolderDefaults.prompt_shell,
    help="If confirm is not True and prompt is True, prompt user to delete each object",
    show_envvar=True,
    show_default=True,
)

OPT_PROMPT_DEFAULT = click.option(
    "--prompt-default/--no-prompt-default",
    "-pd/-npd",
    "prompt_default",
    default=FolderDefaults.prompt_default,
    help="if prompt is True, default choice to offer in prompt",
    show_envvar=True,
    show_default=True,
)

OPT_DELETE_SUBFOLDERS = click.option(
    "--delete-subfolders/--no-delete-subfolders",
    "-ds/-nds",
    "delete_subfolders",
    default=FolderDefaults.delete_subfolders,
    help="Throw a fit if subfolders exist and this is not True",
    show_envvar=True,
    show_default=True,
)

OPT_DELETE_OBJECTS = click.option(
    "--delete-objects/--no-delete-objects",
    "-do/-ndo",
    "delete_objects",
    default=FolderDefaults.delete_subfolders,
    help="Throw a fit if objects exist recursively and this is not True",
    show_envvar=True,
    show_default=True,
)

OPTS_TREE_CONTROLS = [OPT_INCLUDE_DETAILS, OPT_INCLUDE_OBJECTS, OPT_MAXIMUM_DEPTH]
OPTS_CONFIRM = [OPT_PROMPT_DEFAULT, OPT_PROMPT, OPT_CONFIRM]

# X search_objects
OPTS_SEARCH = [
    TABLE_FMT,
    OPT_INCLUDE_DETAILS,
    OPT_EXPORT_FORMAT_SEARCH,
    OPT_EXPORT_FILE,
    OPT_EXPORT_OVERWRITE,
    OPT_ECHO,
    OPT_PATTERN_PREFIX,
    OPT_IGNORE_CASE,
    OPT_ERROR_UNMATCHED,
    OPT_ERROR_NO_MATCHES,
    OPT_ERROR_NO_OBJECTS,
    OPT_ALL_OBJECTS,
    OPT_RECURSIVE,
    OPT_SEARCHES,
    OPT_FOLDER_SEARCH,
]

# X search_objects_copy
OPTS_SEARCH_COPY = [OPT_COPY_PREFIX, OPT_CREATE_TARGET_OPT, *OPTS_SEARCH, OPT_TARGET_SEARCH]

# X search_objects_move
OPTS_SEARCH_MOVE = [OPT_CREATE_TARGET_REQ, *OPTS_SEARCH, OPT_TARGET_MOVE]

# X search_objects_delete
OPTS_SEARCH_DELETE = [*OPTS_SEARCH, *OPTS_CONFIRM]

# X get-tree
OPTS_GET_TREE = [*OPTS_TREE_CONTROLS, OPT_FOLDER_GET_TREE]

# X find
OPTS_FIND = [OPT_ECHO, OPT_CREATE_FOLDER_REQ, *OPTS_TREE_CONTROLS, OPT_FOLDER_FIND]

# X create
OPTS_CREATE = [OPT_ECHO, OPT_FOLDER_CREATE]

# X rename
OPTS_RENAME = [OPT_ECHO, OPT_FOLDER_RENAME, OPT_TARGET_RENAME]

# X move
OPTS_MOVE = [OPT_ECHO, OPT_CREATE_TARGET_REQ, OPT_FOLDER_MOVE, OPT_TARGET_MOVE]

# X delete
OPTS_DELETE = [
    OPT_ECHO,
    *OPTS_CONFIRM,
    OPT_DELETE_SUBFOLDERS,
    OPT_DELETE_OBJECTS,
    OPT_FOLDER_DELETE,
]

# object.update-folder
OPTS_UPDATE_FOLDER = [
    OPT_ECHO,
    OPT_CREATE_FOLDER_REQ,
    OPT_FOLDER_UPDATE,
]

# object.copy/add/create/etc
OPTS_OBJECT_CREATE = [
    OPT_ECHO,
    OPT_CREATE_FOLDER_REQ,
    OPT_FOLDER,
]
