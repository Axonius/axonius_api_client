# -*- coding: utf-8 -*-
"""Constants."""
import dataclasses
import enum
from typing import List, Optional, Union


def joiner(value: List[str], join: str, pre: bool = True):
    if isinstance(join, str):
        value = join.join(value)
        value = join + value if pre else value
    return value


class BaseEnum(enum.Enum):
    JOIN = joiner

    def _generate_next_value_(name, *args):
        return name

    def __str__(self):
        return self.value

    @classmethod
    def get_names(
        cls, join: Optional[str] = None, pre: bool = True
    ) -> Union[str, List[str]]:
        return cls.JOIN(value=[x.name for x in cls], join=join, pre=pre)

    @classmethod
    def get_values(
        cls, join: Optional[str] = None, pre: bool = True
    ) -> Union[str, List[str]]:
        return cls.JOIN(value=[x.name for x in cls], join=join, pre=pre)


@dataclasses.dataclass
class BaseData:
    JOIN = joiner

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def get_fields(cls) -> List[dataclasses.Field]:
        return dataclasses.fields(cls)

    @classmethod
    def get_names(
        cls, join: Optional[str] = None, pre: bool = True
    ) -> Union[str, List[str]]:
        return cls.JOIN(value=[x.name for x in cls.get_fields()], join=join, pre=pre)

    @classmethod
    def get_values(
        cls, join: Optional[str] = None, pre: bool = True
    ) -> Union[str, List[str]]:
        return cls.JOIN(value=[x.default for x in cls.get_fields()], join=join, pre=pre)
