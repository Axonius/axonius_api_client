# -*- coding: utf-8 -*-
"""Constants."""
import dataclasses
import enum


class BaseEnum(enum.Enum):
    def _generate_next_value_(name, *args):
        return name

    def __str__(self):
        return self.value


@dataclasses.dataclass
class BaseData:
    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def get_fields(cls) -> list:
        return dataclasses.fields(cls)
