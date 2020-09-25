# -*- coding: utf-8 -*-
"""Constants."""
import dataclasses
import enum
from typing import List  # , Optional, Union


class BaseEnum(enum.Enum):
    def _generate_next_value_(name, *args):
        return name


@dataclasses.dataclass
class BaseData:
    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def get_fields(cls) -> List[dataclasses.Field]:
        return dataclasses.fields(cls)
