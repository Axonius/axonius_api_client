# -*- coding: utf-8 -*-
"""Tools for working with SSL certificate files."""
import logging
import pathlib
from typing import Any, List, Optional, Tuple, TypeVar, Union

from .tools import check_type, str_to_bytes, type_str

LOG: logging.Logger = logging.getLogger(__name__)
PathLike: TypeVar = TypeVar("PathLike", pathlib.Path, str, bytes)


class PathError(ValueError):
    """Pass."""

    pass


class PathNotFoundError(PathError):
    """Pass."""

    pass


def read_bytes(path: PathLike, exts: Optional[List[str]] = None) -> Tuple[pathlib.Path, bytes]:
    """Read data from a file as bytes.

    Args:
        path (PathLike): str or pathlib.Path object to file to read data from

    Returns:
        Tuple[pathlib.Path, bytes]: resolved path from value, data from path as bytes
    """
    path = pathify(path=path, as_file=True)
    exts = exts or []
    if exts and path.suffix not in exts:
        raise PathError(
            f"Supplied path '{path}' with extension {path.suffix!r} is not one of {exts}"
        )

    data = path.read_bytes()
    return path, data


def find_file_exts(
    path: PathLike, exts: List[str], error: bool = True
) -> Tuple[pathlib.Path, List[pathlib.Path]]:
    """Pass."""
    path = pathify(path=path, as_dir=error)
    files = [x for x in path.glob("*") if x.suffix in exts] if path.is_dir() else []

    if not files and error:
        raise PathNotFoundError(f"Supplied path '{path}' has no files with extensions {exts}")

    return path, files


# XXX NOT USED YET
def write_bytes(
    path: PathLike, content: Union[str, bytes], strict: bool = True, **kwargs
) -> pathlib.Path:
    """Write data to a file."""
    content = str_to_bytes(value=content, strict=strict)
    path = create_file(path=path, **kwargs)
    path.write_bytes(data=content)
    return path


def is_existing_file(path: Any) -> bool:
    """Check if the supplied value refers to an existing file."""
    return (isinstance(path, pathlib.Path) and path.is_file()) or (
        isinstance(path, str) and len(path.splitlines()) == 1 and pathify(path=path).is_file()
    )


def octify(
    value: Optional[Union[int, str, bytes]],
    allow_empty: bool = False,
    fallback: Optional[Any] = None,
    oct_len: int = 5,
    error: bool = True,
) -> Optional[int]:
    """Coerce str or bytes into base 8 octal int."""
    str_ex = "like '0700' or '0o700'"
    int_ex = "like 448"
    err = f"Value must be str/bytes {str_ex} or base 8 int {int_ex}, not {type_str(value)}"

    if not value and allow_empty:
        return fallback

    try:
        check_type(value=value, exp=(int, str, bytes))

        if isinstance(value, (str, bytes)) and value:
            try:
                value = int(value, 8)
            except Exception as exc:
                raise ValueError(f"{err}\nError during 'int({value!r}, 8)':\n{exc}")

        oval = oct(value)
        ovlen = len(oval)
        if oct_len and ovlen != oct_len:
            raise ValueError(
                f"{err}\nOctal result {oval!r} must be {oct_len} characters, not {ovlen}"
            )
    except Exception:
        LOG.exception(f"Error while converting value {value!r} to octal")
        if error:
            raise

        return fallback


def pathify(
    path: PathLike,
    resolve: bool = True,
    expanduser: bool = True,
    as_file: bool = False,
    as_dir: bool = False,
) -> pathlib.Path:
    """Convert a str into a fully resolved & expanded Path object."""
    check_type(value=path, exp=(str, bytes, pathlib.Path))
    resolved = pathlib.Path(path) if isinstance(path, (str, bytes)) else path
    vstr = f"(supplied {type_str(path)})"

    if expanduser:
        resolved = resolved.expanduser()

    if resolve:
        resolved = resolved.resolve()

    if as_file and not resolved.is_file():
        raise PathNotFoundError(f"Resolved path {str(resolved)!r} does not exist as a file {vstr}")

    if as_dir and not resolved.is_dir():
        raise PathNotFoundError(
            f"Resolved path {str(resolved)!r} does not exist as a directory {vstr}"
        )

    return resolved


def create_file(
    path: PathLike,
    overwrite: bool = False,
    make_parent: bool = True,
    make_file: bool = True,
    perm_file: Optional[Union[int, str, bytes]] = "0600",
    perm_parent: Optional[Union[int, str, bytes]] = "0700",
    error: bool = True,
) -> pathlib.Path:
    """Create a file at a path.

    Args:
        path (PathLike): str of path or pathlib.Path object to file to create
        overwrite (bool, optional): error if the file exists already
        make_parent (bool, optional): make the parent directory of value if it does not exist
        make_file (bool, optional): create an empty file if it does not exist
        perm_file (Optional[Union[int, str, bytes]], optional): permissions to set on file
            when creating
        perm_parent (Optional[Union[int, str, bytes]], optional): permissions to set on
            parent directory when creating
        error (bool, optional): raise errors, otherwise just return the resolved path

    Raises:
        PathError: if value exists as file and overwrite is False
        PathNotFoundError: if parent directory of value does not exist and make_parent is False

    Returns:
        pathlib.Path: the resolved path of value
    """
    path = pathify(path=path)
    parent = path.parent
    perm_file = octify(value=perm_file, allow_empty=True)
    perm_parent = octify(value=perm_parent, allow_empty=True)

    try:
        if path.is_file() and overwrite is False:
            raise PathError(f"File '{path}' already exists and overwrite is False")

        if not parent.is_dir():
            raise PathNotFoundError(
                f"Parent directory '{parent}' does not exist and make_parent is False"
            )

            if make_parent:
                parent.mkdir(mode=perm_parent, parents=True, exist_ok=True)
            else:
                return path

        if make_file:
            path.touch()

            if isinstance(perm_parent, int) and perm_parent:
                parent.chmod(mode=perm_parent)

            if isinstance(perm_file, int) and perm_file:
                path.chmod(mode=perm_file)
    except Exception as exc:
        LOG.exception(f"Error while trying to create path {path}: {exc}")
        if error:
            raise

    return path
