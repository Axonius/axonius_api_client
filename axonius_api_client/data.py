# -*- coding: utf-8 -*-
"""Base classes for data types."""
import dataclasses
import datetime
import enum
from typing import List


class BaseEnum(enum.Enum):
    """Base class for enums."""

    def _generate_next_value_(name, *args):
        """Get the next enum value in iterators."""
        return name

    def __str__(self):
        """Pass."""
        return str(self.value)


@dataclasses.dataclass
class BaseData:
    """Base class for dataclasses."""

    def to_dict(self) -> dict:
        """Get this dataclass object as a dictionary."""
        return dataclasses.asdict(self)

    def replace(self, **kwargs) -> "BaseData":
        """Pass."""
        return dataclasses.replace(self, **kwargs)

    @staticmethod
    def _human_key(key):
        """Pass."""
        return key.replace("_", " ").title()

    @classmethod
    def get_fields(cls) -> List[dataclasses.Field]:
        """Get a list of fields defined for current this dataclass object."""
        return dataclasses.fields(cls)


@dataclasses.dataclass
class PropsData(BaseData):
    """Pass."""

    raw: dict

    def __str__(self):
        """Pass."""
        return getattr(self, "_str_join", "\n").join(self.to_str_properties())

    def __repr__(self):
        """Pass."""
        return repr(self.__str__())

    def to_str_properties(self) -> List[str]:
        """Pass."""
        return [f"{self._human_key(x)}: {getattr(self, x)}" for x in self._properties]

    def to_dict(self, dt_obj: bool = False) -> dict:
        """Pass."""

        def get_val(prop):
            value = getattr(self, prop)
            if not dt_obj and isinstance(value, datetime.datetime):
                return str(value)
            return value

        ret = {k: get_val(k) for k in self._properties}
        return ret
