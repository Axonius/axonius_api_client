# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

from ....tools import listify


"""
ftype: type = list ; is_list: bool = ftype == list ; is_list  # True
ftype: type = t.List[str] ; is_list: bool = t.get_origin(ftype) == list ; is_list  # True

ftype = t.List[str] ; typeargs = t.get_args(ftype) == list ; is_list  # True
True

"""


def is_subclass(value: t.Any, cls: t.Any) -> bool:
    """Pass."""
    try:
        return issubclass(value, cls)
    except Exception:
        return False


def is_instance(value: t.Any, cls: t.Any) -> bool:
    """Pass."""
    try:
        return isinstance(value, cls)
    except Exception:
        return False


class SerialMixins:
    """Mixins to help with serialization."""

    def to_dict2(
        self,
        explode: bool = False,
        prepend_class: bool = False,
        strip_tz: bool = False,
        skips: t.Optional[t.List[str]] = None,
    ) -> dict:
        """Serialize self into a dictionary."""
        '''csv columns should be like
        name: key_pre + key
        description: description
        type: str
        '''
        data: dict = {}
        skips: t.List[str] = listify(skips)
        key_pre: str = f"{self.__class__.__name__.lower()}_" if prepend_class else ""
        prepend_class: bool = True if explode else prepend_class

        for field in self._get_fields():
            key: str = f'{key_pre}{field.name}'
            # description: str = field.metadata.get("description", "")
            # type: str = cls._type_str(field.type)

            if any([x in skips for x in [field.name, key]]):
                continue

            value: t.Any = getattr(self, field.name, None)
            if strip_tz and isinstance(value, datetime.datetime):
                value: str = str(value.replace(tzinfo=None))
            if isinstance(value, self.__class__):
                # prepend_class should be true if explode?
                value: dict = value.to_dict2(
                    prepend_class=True if explode else prepend_class,
                    explode=explode,
                    skips=skips,
                    strip_tz=strip_tz,
                )
        return data

    def to_dict(self, *args, skips: t.Optional[t.List[str]] = None, **kwargs) -> dict:
        """Serialize self into a dictionary."""
        data: dict = super().to_dict(*args, **kwargs)
        return {k: v for k, v in data.items() if k not in listify(skips)}

    def to_dict_csv(self) -> dict:
        """Serialize self into a CSV friendly dictionary."""
        data: dict = {
            self._csv_key(k): self._csv_value(v)
            for k, v in self.to_dict(skips=self._csv_skips()).items()
        }
        return data

    def to_dict_new(
        self,
        *args,
        skips: t.Optional[t.List[str]] = None,
        prepend_class: bool = False,
        strip_tz: bool = False,
        **kwargs,
    ) -> dict:
        """Serialize self into a dictionary."""

        def dkey(key: str, value: t.Any) -> str:
            """Pass."""
            if prepend_class:
                key = f"{self.__class__.__name__.lower()}_{key}"
            return key

        def dvalue(self, key: str, value: t.Any) -> t.Any:
            """Pass."""
            if strip_tz:
                if isinstance(value, datetime.datetime):
                    value: str = str(value.replace(tzinfo=None))
            return value

        skips: t.List[str] = listify(skips)
        data: dict = super().to_dict(*args, **kwargs)
        data: dict = {dkey(k, v): dvalue(k, v) for k, v in data.items() if k not in skips}
        return data

    @classmethod
    def get_csv_headers(cls) -> dict:
        """Get a row with the headers to be used in CSV."""
        ret: dict = {x: x for x in cls.get_csv_columns()}
        for child in cls._csv_children():
            ret.update(child.get_csv_headers())
        return ret

    @classmethod
    def get_csv_descriptions(cls) -> dict:
        """Get a row with descriptions for headers to be used in CSV."""
        ret: dict = {
            cls._csv_key(x.name): x.metadata.get("description", "")
            for x in cls._get_fields(skips=cls._csv_skips())
        }
        for child in cls._csv_children():
            ret.update(child.get_csv_descriptions())
        return ret

    # need more control over flatten...
    @classmethod
    def get_csv_types(cls) -> dict:
        """Get a row with types for headers to be used in CSV."""
        ret: dict = {
            cls._csv_key(x.name): cls._type_str(x.type)
            for x in cls._get_fields(skips=cls._csv_skips())
        }
        for child in cls._csv_children():
            ret.update(child.get_csv_types())
        return ret

    @classmethod
    def get_csv_columns(cls) -> t.List[str]:
        """Get the columns to use in CSV."""
        ret: t.List[str] = [cls._csv_key(x.name) for x in cls._get_fields(skips=cls._csv_skips())]
        for child in cls._csv_children():
            ret += child.get_csv_columns()
        return ret

    @staticmethod
    def _csv_value(value: t.Any) -> t.Any:
        """Coerce value for CSV format as needed."""
        if isinstance(value, datetime.datetime):
            value: str = str(value.replace(tzinfo=None))
        return value

    @classmethod
    def _csv_skips(cls) -> t.List[str]:
        """Get the field names that should be skipped in CSV."""
        return []

    @classmethod
    def _csv_key(cls, key: str) -> str:
        """Build a key for use in CSV."""
        return key

    @classmethod
    def _csv_children(cls) -> t.List[t.Type["SerialMixins"]]:
        """Get a list of complex children objects to include in CSV."""
        return []

    @classmethod
    def _get_fields(
        cls, *args, skips: t.Optional[t.List[str]] = None, **kwargs
    ) -> t.List[dataclasses.Field]:
        """Get the fields for this dataclass."""
        return [x for x in super()._get_fields(*args, **kwargs) if x.name not in listify(skips)]

    @staticmethod
    def _type_str(value: t.Any) -> str:
        """Try to get the type string."""
        try:
            return ", ".join([str(x.__name__).replace("Type", "") for x in value.__args__])
        except Exception:
            return str(value)
