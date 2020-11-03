# -*- coding: utf-8 -*-
"""Base classes for data types."""
import dataclasses
import enum
from typing import List


class BaseEnum(enum.Enum):
    """Base class for enums."""

    def _generate_next_value_(name, *args):
        """Get the next enum value in iterators."""
        return name


@dataclasses.dataclass
class BaseData:
    """Base class for dataclasses."""

    def to_dict(self) -> dict:
        """Get this dataclass object as a dictionary."""
        return dataclasses.asdict(self)

    @classmethod
    def get_fields(cls) -> List[dataclasses.Field]:
        """Get a list of fields defined for current this dataclass object."""
        return dataclasses.fields(cls)
