# -*- coding: utf-8 -*-
"""Utilities and tools."""
import dataclasses
import logging
import pathlib
import types
import typing as t
import warnings

from ..constants.fields import AXID
from ..constants.ctypes import PathLike
from ..data import BaseData
from ..exceptions import GrabberError, GrabberWarning
from ..logs import get_echoer, get_obj_log
from ..tools import (
    add_source,
    csv_able,
    csv_load,
    json_load,
    jsonl_load,
    listify,
    text_load,
    tlens,
    pathify,
)


class Mixins:
    """Pass."""

    _exc_cls: t.ClassVar[Exception] = GrabberError
    _warn_cls: t.ClassVar[Warning] = GrabberWarning

    def spew(
        self,
        msgs: t.Optional[t.List[str]] = None,
        top: bool = False,
        exc: t.Optional[t.Union[bool, Exception]] = None,
        warn: bool = False,
        **kwargs,
    ):
        """Log an entry to logger and console."""
        do_echo: bool = kwargs.get("do_echo", self.do_echo)
        exc_obj: t.Optional[Exception] = None
        msgs: str = "\n".join(self.infos(msgs=msgs, top=top))

        if exc:
            kwargs.setdefault("level", "error")
        elif warn:
            kwargs.setdefault("level", "warning")
        elif self._initialized:
            kwargs.setdefault("level", "info")
        else:
            kwargs.setdefault("level", "debug")

        level = kwargs["level"]

        if exc is True:
            exc = self._exc_cls

        if exc and callable(exc) and issubclass(exc, Exception):
            exc_obj = exc(msgs)
            exc_obj.self = self

        if isinstance(exc_obj, Exception):
            raise exc_obj

        if warn:
            if not do_echo:
                warnings.warn(msgs, self._warn_cls)
                return
        echoer: t.Callable = get_echoer(level=level)
        echoer(msg=msgs, log_level=level, log=self.log, do_echo=do_echo, abort=False)

    def __str__(self) -> str:
        """Dunder."""
        items = "\n  " + ",\n  ".join(self._tstr_items) + ",\n"
        return f"{self.__class__.__name__}({items})"

    def infos(self, msgs: t.Optional[t.List[str]] = None, top: bool = True) -> t.List[str]:
        """Get info on self."""
        ret = []
        if top:
            ret += [f"{self}"]
        ret += listify(msgs)
        return ret


@dataclasses.dataclass
class Hunter(BaseData, Mixins):
    """Pass."""

    value: t.Union[dict, str]
    idx: int
    keys: t.List[str]
    count_supplied: int
    do_echo: bool = True

    log: t.ClassVar[logging.Logger] = None
    found: t.ClassVar[bool] = False
    found_key: t.ClassVar[t.Optional[str]] = None
    error: t.ClassVar[t.Optional[str]] = None
    axid: t.ClassVar[t.Optional[str]] = None
    msgs: t.ClassVar[t.List[str]] = None
    had_error: t.ClassVar[bool] = None
    _initialized: t.ClassVar[bool] = True
    _tbadtype: t.ClassVar[str] = "is not a dict or str, is instead"
    _trules: t.ClassVar[str] = AXID.rules_short
    _ttxt_y: t.ClassVar[str] = "found Asset ID in text line"
    _ttxt_n: t.ClassVar[str] = f"text line does not contain a {_trules}"
    _tdict_n_keys: t.ClassVar[str] = f"but none of the keys values are a {_trules}"
    _tdict_n: t.ClassVar[str] = "but it has none of the keys we looked for"
    _tdict_y_bad_pre: t.ClassVar[str] = "found matching key"
    _tdict_y_bad_post: t.ClassVar[str] = f"but value is not a {_trules}"
    _tdict_y: t.ClassVar[str] = "found item in key"

    @property
    def num(self) -> int:
        """Pass."""
        return self.idx + 1

    def __post_init__(self):
        """Dataclass setup."""
        self.log = get_obj_log(self)
        self.msgs = []
        if isinstance(self.value, dict):
            self._handle_dict()
        elif isinstance(self.value, str):
            self._handle_str()
        else:
            self._handle_other()

    def _handle_dict(self):
        has_keys = [k for k in self.keys if k in self.value]
        for key in has_keys:
            value = AXID.strip(self.value[key])
            if value and AXID.is_axid(value):
                self.found_key = key
                self.found = True
                self.axid = value
                self.spew(f"{self._tdict_y} {self.found_key!r}", level="debug", do_echo=False)
                break
            else:
                self.error(f"{self._tdict_y_bad_pre} {key!r} {self._tdict_y_bad_post}", final=False)
        if not self.found:
            msg = f"{self._titem_keys} {self._tdict_n}"
            if has_keys:
                msg = f"{self._titem_keys} and has keys {has_keys}, {self._tdict_n_keys}"
            self.error(msg)

    def _handle_str(self):
        if not self.value.strip() or self.value.startswith("#"):
            return
        value = AXID.strip(self.value)
        if AXID.is_axid(value):
            self.found = True
            self.axid = value
            self.spew(f"{self._ttxt_y}", level="debug", do_echo=False)
        else:
            self.error(f"{self._ttxt_n}")

    def _handle_other(self):
        self.error(f"{self._tbadtype} {tlens(self.value)}")

    @property
    def _tin_item(self) -> str:
        """Pass."""
        return f"In item {self.num}/{self.count_supplied}"

    @property
    def _titem_keys(self) -> str:
        """Pass."""
        return f"item is a dict with keys {list(self.value)}"

    def error(self, msg: str, final: bool = True):
        """Pass."""
        self.spew(msgs=f"{self._tin_item}: {msg}", level="error")
        if final:
            self.error = msg
            self.had_error = True

    @property
    def _tstr_items(self) -> t.List[str]:
        return [
            f"idx={self.idx}",
            f"found={self.found}",
            f"had_error={self.had_error}",
        ]

    def __repr__(self) -> str:
        """Dunder."""
        return self.__str__()


@dataclasses.dataclass
class Grabber(BaseData, Mixins):
    """Get Asset IDs by checking for multiple keys from a list of dicts or a list of str."""

    items: t.Union[str, t.List[str], dict, t.List[dict], types.GeneratorType]
    keys: t.Optional[t.Union[str, t.List[str]]] = None
    do_echo: bool = True
    do_raise: bool = False
    source: t.Any = None

    log: t.ClassVar[logging.Logger] = None
    axids: t.ClassVar[t.Set[str]] = None
    hunters: t.ClassVar[t.List[Hunter]] = None
    keys_base: t.ClassVar[t.List[str]] = AXID.keys
    progress: t.ClassVar[int] = 10000
    _initialized: t.ClassVar[bool] = False
    _titems_empty: t.ClassVar[str] = "No items supplied"
    _tnone_found: t.ClassVar[str] = "No Asset IDs found"
    _terrors_mid: t.ClassVar[str] = "distinct errors while looking for Asset IDs in keys"

    @classmethod
    def from_json(cls, items: t.Union[str, bytes, t.IO, pathlib.Path], **kwargs) -> "Grabber":
        """Get Asset IDs from a JSON string with a list of dicts."""
        kwargs["items"] = post_load = json_load(obj=items)
        source = f"from_json items {tlens(items)} post_load {tlens(post_load)}"
        kwargs["source"] = add_source(source=source, kwargs=kwargs)
        return cls(**kwargs)

    @classmethod
    def from_jsonl(
        cls, items: t.Union[str, t.List[str], t.IO, pathlib.Path], **kwargs
    ) -> "Grabber":
        """Get Asset IDs from a JSONL string with one dict per line."""
        kwargs["items"] = post_load = jsonl_load(obj=items)
        kwargs["source"] = add_source(
            source=f"from_jsonl items {tlens(items)} post_load {tlens(post_load)}", kwargs=kwargs
        )
        return cls(**kwargs)

    @classmethod
    def from_csv(
        cls,
        items: t.Union[str, bytes, t.IO, pathlib.Path],
        load_args: t.Optional[dict] = None,
        **kwargs,
    ) -> "Grabber":
        """Get Asset IDs from a CSV string."""
        load_args = load_args if isinstance(load_args, dict) else {}
        load_args["value"] = items

        kwargs["items"] = post_load = csv_load(**load_args).rows
        kwargs["source"] = add_source(
            source=f"from_csv items {tlens(items)} post_load {tlens(post_load)}", kwargs=kwargs
        )
        return cls(**kwargs)

    @classmethod
    def from_text(cls, items: t.Union[str, t.List[str]], **kwargs):
        """Get Asset IDs from a text string."""
        kwargs["items"] = post_load = text_load(value=items)
        kwargs["source"] = add_source(
            source=f"from_text items {tlens(items)} post_load {tlens(post_load)}", kwargs=kwargs
        )
        return cls(**kwargs)

    @classmethod
    def from_json_path(cls, path: PathLike, **kwargs) -> "Grabber":
        """Get Asset IDs from a JSON file with a list of dicts."""
        path = pathify(path=path, as_file=True)
        kwargs["items"] = path
        kwargs["source"] = add_source(source=f"from_json_path {path}", kwargs=kwargs)
        return cls.from_json(**kwargs)

    @classmethod
    def from_jsonl_path(cls, path: PathLike, **kwargs) -> "Grabber":
        """Get Asset IDs from a JSONL file with one dict per line."""
        path = pathify(path=path, as_file=True)
        kwargs["items"] = path
        kwargs["source"] = add_source(source=f"from_jsonl_path {path}", kwargs=kwargs)
        return cls.from_jsonl(**kwargs)

    @classmethod
    def from_csv_path(cls, path: PathLike, **kwargs) -> "Grabber":
        """Get Asset IDs from a CSV file."""
        path = pathify(path=path, as_file=True)
        kwargs["items"] = path
        kwargs["source"] = add_source(source=f"from_csv_path {path}", kwargs=kwargs)
        return cls.from_csv(**kwargs)

    @classmethod
    def from_text_path(cls, path: PathLike, **kwargs):
        """Get Asset IDs from a text file."""
        path = pathify(path=path, as_file=True)
        kwargs["items"] = path
        kwargs["source"] = add_source(source=f"from_text_path {path}", kwargs=kwargs)
        return cls.from_text(**kwargs)

    def reorder_keys(self, key: t.Optional[str]):
        """Re-order keys for performance."""
        if key and key in self.keys:
            key_idx = self.keys.index(key)
            if key_idx != 0:
                self.keys.insert(0, self.keys.pop(key_idx))

    def _load_items(self):
        self.items = listify(self.items)
        cnt = self.count_supplied
        if cnt is None:
            cnt = "(count not yet known)"
        msgs = [f"Loaded {cnt} items from source: {self.source}"]
        sargs = {"top": True}
        if not self.items:
            sargs["exc"] = True
            msgs += [self._titems_empty]
        self.spew(msgs=msgs, **sargs)

    def _load_keys(self):
        self.keys = csv_able(self.keys)
        self.keys += [x for x in self.keys_base if x not in self.keys]
        self.spew(f"Searching for Asset IDs in keys: {self.keys}")

    def _load_hunters(self):
        self.hunters = []
        self.axids = set()
        for idx, x in enumerate(self.items):
            hunter = Hunter(
                value=x,
                idx=idx,
                keys=self.keys,
                do_echo=self.do_echo,
                count_supplied=self.count_supplied,
            )
            self.hunters.append(hunter)
            if isinstance(self.progress, int) and idx % self.progress == 0:
                self.spew(f"Hunting progress: {self._tfound} - still loading", level="debug")
                self.reorder_keys(hunter.found_key)
            if hunter.axid:
                self.axids.add(hunter.axid)

        sargs = {"top": True}
        if self.count_supplied != self.count_found:
            sargs["warn"] = True
        if not self.count_found:
            sargs["level"] = "error"
        self.spew(msgs=self._tfound, **sargs)
        self.handle_errors()

    def __post_init__(self):
        """Dataclass setup."""
        self.log = get_obj_log(self)
        self._load_keys()
        self._load_items()
        self._initialized = True
        self._load_hunters()

    def handle_errors(self):
        """Pass."""
        msgs = self.error_msgs
        sargs = {"top": True}
        if msgs:
            if self.do_raise:
                sargs["exc"] = True
            else:
                sargs["warn"] = True
        if not self.count_found:
            sargs["exc"] = True
            msgs += [self._tnone_found]
        if msgs:
            self.spew(msgs=msgs, **sargs)

    @property
    def error_msgs(self) -> t.List[str]:
        """Pass."""
        error_strs = self.error_strs
        msgs = []
        if error_strs:
            msg = f"{self._tfound} with {len(error_strs)} {self._terrors_mid}:\n{self.keys}"
            msgs += [msg, "", *error_strs, "", msg]
        return msgs

    @property
    def error_strs(self) -> t.List[str]:
        """Pass."""
        return [f"- Error in item numbers {v}: {k}" for k, v in self.error_map.items()]

    @property
    def error_map(self) -> t.Dict[str, str]:
        """Pass."""

        def get_nums(value):
            return ", ".join([f"{x.num}" for x in value])

        return {k: get_nums(v) for k, v in self._error_map.items()}

    @property
    def _error_map(self) -> t.Dict[str, t.List[Hunter]]:
        """Pass."""
        ret = {}
        for hunter in self.hunters:
            if hunter.had_error and hunter.error:
                if hunter.error not in ret:
                    ret[hunter.error] = []
                ret[hunter.error].append(hunter)
        return ret

    @property
    def _tfound(self) -> str:
        return f"Found {self.count_found} asset IDs from {self.count_supplied} items"

    @property
    def count_supplied(self) -> t.Optional[int]:
        """Pass."""
        if isinstance(self.items, list):
            return len(self.items)
        if isinstance(self.hunters, list):
            return len(self.hunters)
        return None

    @property
    def count_found(self) -> t.Optional[int]:
        """Pass."""
        if isinstance(self.axids, set):
            return len(self.axids)
        return None

    @property
    def _tstr_items(self) -> t.List[str]:
        items = [
            f"count_supplied={self.count_supplied}",
            f"count_found={self.count_found}",
            f"do_echo={self.do_echo}",
            f"do_raise={self.do_raise}",
            f"source={self.source!r}",
        ]
        return items

    def __repr__(self) -> str:
        """Dunder."""
        return self.__str__()
