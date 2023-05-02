# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from ....exceptions import NotFoundError
from ....parsers.tables import tablize
from ....tools import longest_str
from ..generic import Metadata, MetadataSchema


class AdaptersListSchema(MetadataSchema):
    """Schema for adapters list response."""

    class Meta:
        """JSONAPI config."""

        type_ = "metadata_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return AdaptersList


@dataclasses.dataclass
class AdaptersList(Metadata):
    """Model for adapters list response."""

    adapters: t.ClassVar[t.Dict[str, dict]] = None

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return AdaptersListSchema

    def __post_init__(self):
        """Pass."""
        items = self.document_meta["adapter_list"]
        self.adapters = {}
        for item in items:
            name_raw = item["name"]
            name = self._get_aname(name_raw)
            item["name_raw"] = name_raw
            item["name"] = name
            self.adapters[name] = item

    def find_by_name(self, value: str) -> dict:
        """Pass."""
        find_value = self._get_aname(value)

        if find_value not in self.adapters:
            padding = longest_str(list(self.adapters))
            valid = [f"{k:{padding}}: {v['title']}" for k, v in self.adapters.items()]
            pre = f"No adapter found with name of {value!r}"
            msg = [pre, "", *valid, "", pre]
            raise NotFoundError("\n".join(msg))
        ret = self.adapters[find_value]
        return ret

    def find(self, value: str, error: bool = True) -> t.Optional[dict]:
        """Find adapter basic data by title, name, or name_raw."""
        find_values = [value, self._get_aname(value)]
        valids = []
        for data in self.adapters.values():
            data_values = list(data.values())
            valids.append(data)
            if any([x in data_values for x in find_values]):
                return data
        if error:
            err = f"No Adapter found matching {find_values} out of {len(valids)} items"
            err_table = tablize(value=valids, err=err)
            raise NotFoundError(err_table)
        return None

    def get_title(self, value: str, error: bool = True) -> t.Optional[str]:
        """Pass."""
        found = self.find(value=value, error=error)
        if isinstance(found, dict):
            title = found.get("title")
            if isinstance(title, str) and title.strip():
                return title
        return None
