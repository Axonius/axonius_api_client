# -*- coding: utf-8 -*-
"""Utilities and tools."""
import json
import logging
from typing import Any, ClassVar, Dict, Generator, List, Optional

from ..cert_human.paths import FileInfo, PathLike
from ..constants.api import AXID
from ..constants.logs import LOG_LEVEL_API
from ..exceptions import ToolsError
from ..logs import get_obj_log
from ..tools import listify


class ParseDicts:
    """Pass."""

    count: ClassVar[int] = None
    errors: ClassVar[List[str]] = None
    errors_items: ClassVar[Dict[str, List[int]]] = None
    yielded_one: ClassVar[bool] = False
    log: ClassVar[logging.Logger] = None

    def __init__(self, log_level: LOG_LEVEL_API):
        """Pass."""
        self.log: logging.Logger = get_obj_log(obj=self, level=log_level)

    def parse(self, **kwargs) -> List[Any]:
        """Pass."""
        return list(self._parse(**kwargs))

    def _parse(
        self,
        values: List[dict],
        keys: List[str],
        src: str = "",
        not_empty: bool = True,
        error_on_item: bool = True,
    ) -> Generator[Any, None, None]:
        """Pass."""
        self.count = 0
        self.errors = []
        self.errors_items = {}
        self.yielded_one = False

        err_pre = f"Errors occurred while checking supplied {self.src} as a list of dictionaries"

        keys = listify(keys)
        if not keys or not all([isinstance(x, str) and x.strip() for x in keys]):
            raise ToolsError(f"{err_pre}\nMust supply a list of non-empty strings as keys: {keys}")

        key_count = len(keys)

        for idx, item in enumerate(listify(values)):
            self.count += 1

            try:
                item = self._check_item(item=item, keys=keys)

                for idx, key in enumerate(keys):
                    if key in item:
                        value = item[key]
                        try:
                            yield self._check_value(value=value)
                        except Exception:
                            if idx + 1 == key_count:
                                raise

                self.yielded_one = True
            except Exception as exc:
                msg = str(exc)
                if msg not in self.errors_items:
                    self.errors_items[msg] = []
                self.errors_items[msg].append(idx)
                self.log.exception(f"At index {idx}: {msg}")

        if not_empty and not self.yielded_one:
            self.errors.append(f"Empty results after parsing {self.count} items")

        errors_items = [f"{k}: {v}" for k, v in self.errors_items.items()]
        errors = self.errors

        if errors_items or errors:
            err = [
                f"{err_pre} ({self.count} items parsed)",
            ]

            if errors_items:
                err += [
                    "Errors in item indexes:",
                    *errors_items,
                ]

            if errors:
                err += [
                    "Errors in parsing:",
                    *self.errors,
                ]

            err = "\n".join(err)

            self.log.error(err)
            if error_on_item or errors:
                raise ToolsError(err)

    def _check_item(self, item: dict, keys: List[str]) -> dict:
        """Pass."""
        if not isinstance(item, dict):
            raise TypeError(f"Invalid item, should be type {dict}, is instead type {type(item)}")

        if not any([k in item for k in keys]):
            raise ValueError("Does not have any of keys {keys}, only has keys {list(item)}")
        return item

    def _check_value(self, value: Any) -> Any:
        """Pass."""
        return value


class ParseAssetIds(ParseDicts):
    """Pass."""

    def parse(self, **kwargs) -> List[str]:
        """Pass."""
        ret = []
        for value in self._parse(**kwargs):
            if value not in ret:
                ret.append(value)
        return ret

    def _parse(
        self,
        values: List[dict],
        keys: List[str] = AXID,
        src: str = "",
        not_empty: bool = True,
        error_on_item: bool = True,
        do_strip: bool = True,
        strip: Optional[str] = "'\" ",
        check_alnum: bool = True,
        check_length: int = 32,
    ) -> Generator[Any, None, None]:
        """Pass."""
        self.do_strip = do_strip
        self.strip = strip
        self.check_alnum = check_alnum
        self.check_length = check_length
        return super()._parse(
            values=values, keys=keys, src=src, not_empty=not_empty, error_on_item=error_on_item
        )

    def _check_value(self, value: Any, idx: int) -> Any:
        """Pass."""
        if not isinstance(value, str):
            raise TypeError(f"Value is not type {str}, is instead type {type(value)}")

        if self.do_strip:
            value = value.strip(self.strip)

        if isinstance(self.check_length, int):
            vlen = len(value)
            if vlen != self.check_length:
                raise TypeError(f"Value is not {self.check_length} characters, is instead {vlen}")

        if self.check_alnum:
            if not value.isalnum():
                non_alpha_cnt = len(list(set([x for x in value if not x.isalnum()])))
                raise TypeError(f"Value has {non_alpha_cnt} non alphanumeric characters")
        return value


class ParseAssetIdsJson(ParseAssetIds):
    """Pass."""

    def parse(
        self,
        content: str,
        is_jsonl: bool = False,
        **kwargs,
    ) -> List[str]:
        """Pass."""
        self.is_jsonl = is_jsonl
        self.content = content

        if isinstance(content, str):
            content = content.strip()

            if self.is_jsonl:
                kwargs["values"] = content.splitlines()
            else:
                kwargs["values"] = json.load(content)
        else:
            raise TypeError(f"content must be type {str}, not {type(content)}")

        return super().parse(**kwargs)

    def _check_item(self, item: dict, keys: List[str]) -> dict:
        """Pass."""
        if self.is_jsonl:
            try:
                item = json.loads(item)
            except Exception as exc:
                raise ValueError(f"Invalid item, unable to parse JSON: {exc}")
        return super()._check_item(item=item, keys=keys)


class ParseAssetIdsJsonPath(ParseAssetIdsJson):
    """Pass."""

    """Needs JSON path as input.
    if is_jsonl, fh.readlines and json.loads and parse each item
    if not is_jsonl, fh.read and json.loads whole input and parse each item
    """

    def parse(
        self,
        path: PathLike,
        is_jsonl: bool = False,
        **kwargs,
    ) -> List[str]:
        """Pass."""
        self.is_jsonl = is_jsonl
        self.file_info = FileInfo(path=path, as_file=True)
        kwargs["values"] = self.path
        return super().parse(**kwargs)


class ParseAssetIdsCsv(ParseAssetIds):
    """Pass."""

    """Needs CSV string as input.
    csv.dictreader whole thing and pass to parent
    needs CSV specific keys
    """


class ParseAssetIdsCsvPath(ParseAssetIdsCsv):
    """Pass."""

    """Needs CSV path as input.
    fh.read() and csv.dictreader whole thing and pass to parent
    needs CSV specific keys
    """
