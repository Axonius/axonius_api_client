# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import re
from typing import List, Optional, Tuple, Union

from ...constants import (
    AGG_ADAPTER_ALTS,
    AGG_ADAPTER_NAME,
    GET_SCHEMA_KEYS,
    GET_SCHEMAS_KEYS,
)
from ...exceptions import ApiError, NotFoundError
from ...tools import listify, split_str, strip_right
from ..mixins import ChildMixins
from ..parsers.fields import parse_fields


class Fields(ChildMixins):
    """Child API model for working with fields for the parent asset type."""

    def get(self) -> dict:
        """Get the schema of all adapters and their fields.

        Returns:
            :obj:`dict`: parsed output from :meth:`ParserFields.parse`
        """
        return parse_fields(raw=self._get())

    def get_adapter_names(
        self, value: str, fields_map: Optional[dict] = None
    ) -> List[str]:
        """Find an adapter by name regex."""
        fields_map = fields_map or self.get()

        search = strip_right(obj=value.lower().strip(), fix="_adapter")

        if search in AGG_ADAPTER_ALTS:
            search = AGG_ADAPTER_NAME

        search = re.compile(search, re.I)
        matches = [x for x in fields_map if search.search(x)]

        if not matches:
            msg = (
                "No adapter found where name regex matches {!r}, valid adapters:\n  {}"
            ).format(value, "\n  ".join(list(fields_map)))
            raise NotFoundError(msg)
        return matches

    def get_adapter_name(self, value: str, fields_map: Optional[dict] = None) -> str:
        """Find an adapter by name."""
        fields_map = fields_map or self.get()

        search = strip_right(obj=value.lower().strip(), fix="_adapter")

        if search in AGG_ADAPTER_ALTS:
            search = AGG_ADAPTER_NAME

        if search in fields_map:
            return search

        msg = "No adapter found where name equals {!r}, valid adapters:\n  {}"
        msg = msg.format(value, "\n  ".join(list(fields_map)))
        raise NotFoundError(msg)

    def get_field_schemas(self, value: str, schemas: List[dict], **kwargs) -> List[dict]:
        """Find a schema for a field by regex of name."""
        keys = kwargs.get("keys", GET_SCHEMAS_KEYS)
        search = re.compile(value.lower().strip(), re.I)

        matches = []

        for schema in schemas:
            if not schema.get("selectable"):
                continue

            for key in keys:
                if search.search(schema[key]) and schema not in matches:
                    matches.append(schema)
        return matches

    def get_field_schema(self, value: str, schemas: List[dict], **kwargs) -> dict:
        """Find a schema for a field by name."""
        keys = kwargs.get("keys", GET_SCHEMA_KEYS)
        search = value.lower().strip()

        schemas = [x for x in schemas if x.get("selectable", True)]

        for schema in schemas:
            for key in keys:
                if search == schema[key].lower():
                    return schema

        msg = "No field found where any of {} equals {!r}, valid fields: \n{}"
        msg = msg.format(keys, value, "\n".join(self._prettify_schemas(schemas=schemas)))
        raise NotFoundError(msg)

    def get_field_name(
        self,
        value: str,
        field_manual: bool = False,
        fields_map: Optional[dict] = None,
        custom_fields_map: Optional[dict] = None,
        key: str = "name_qual",
    ) -> str:
        """Pass."""
        if field_manual:
            return value

        adapter, fields = self.split_search(value=value)

        if len(fields) != 1:
            raise ApiError("More than one field supplied to {}".format(value))

        field = fields[0]

        fields_map = fields_map or self.get()
        adapter = self.get_adapter_name(value=adapter, fields_map=fields_map)
        schemas = fields_map[adapter]
        if custom_fields_map and adapter in custom_fields_map:
            schemas += custom_fields_map[adapter]
        schema = self.get_field_schema(value=field, schemas=schemas)
        return schema[key] if key else schema

    def get_field_names_re(
        self, value: str, fields_map: Optional[dict] = None
    ) -> List[str]:
        """Pass."""
        splits = self.split_searches(value=value)
        fields_map = fields_map or self.get()

        matches = []

        for adapter_re, fields in splits:
            adapters = self.get_adapter_names(value=adapter_re, fields_map=fields_map)

            for adapter in adapters:
                for field in fields:
                    fschemas = self.get_field_schemas(
                        value=field, schemas=fields_map[adapter]
                    )
                    names = [x["name_qual"] for x in fschemas]
                    matches += [x for x in names if x not in matches]
        return matches

    def get_field_names_eq(
        self, value: str, fields_map: Optional[dict] = None
    ) -> List[str]:
        """Pass."""
        splits = self.split_searches(value=value)
        fields_map = fields_map or self.get()

        matches = []

        for adapter_name, names in splits:
            adapter = self.get_adapter_name(value=adapter_name, fields_map=fields_map)
            for name in names:
                schemas = fields_map[adapter]
                schema = self.get_field_schema(value=name, schemas=schemas)
                if schema["name_qual"] not in matches:
                    matches.append(schema["name_qual"])

        return matches

    def get_field_schemas_root(
        self, adapter: str, fields_map: Optional[dict] = None
    ) -> List[dict]:
        """Pass."""
        fields_map = fields_map or self.get()
        adapter = self.get_adapter_name(value=adapter, fields_map=fields_map)
        schemas = fields_map[adapter]

        matches = [x for x in schemas if x.get("selectable") and x.get("is_root")]
        return matches

    def get_field_names_root(
        self, adapter: str, fields_map: Optional[dict] = None
    ) -> List[str]:
        """Pass."""
        schemas = self.get_field_schemas_root(adapter=adapter, fields_map=fields_map)
        names = [x["name_qual"] for x in schemas]
        return names

    def validate(
        self,
        fields: Optional[Union[List[str], str]] = None,
        fields_regex: Optional[Union[List[str], str]] = None,
        fields_manual: Optional[Union[List[str], str]] = None,
        fields_default: bool = True,
        fields_map: Optional[dict] = None,
        fields_root: Optional[str] = None,
    ) -> List[dict]:
        """Validate provided fields."""
        fields_manual = listify(obj=fields_manual)
        selected = []

        if fields_default and not fields_root:
            selected += self.parent.fields_default

        if fields_manual:
            selected += [x for x in fields_manual if x not in selected]

        if fields_root:
            fields_map = fields_map or self.get()
            matches_root = self.get_field_names_root(
                adapter=fields_root, fields_map=fields_map
            )
            selected += [x for x in matches_root if x not in selected]

        if not any([fields, fields_regex]):
            if not selected:
                raise ApiError("No fields supplied, must supply at least one field")
            return selected

        fields_map = fields_map or self.get()

        matches_eq = self.get_field_names_eq(value=fields, fields_map=fields_map)
        selected += [x for x in matches_eq if x not in selected]

        matches_re = self.get_field_names_re(value=fields_regex, fields_map=fields_map)
        selected += [x for x in matches_re if x not in selected]

        return selected

    def split_searches(
        self, value: Union[List[str], str]
    ) -> List[Tuple[str, List[str]]]:
        """Pass."""
        return [self.split_search(value=x) for x in listify(obj=value)]

    def split_search(
        self, value: str, adapter: str = AGG_ADAPTER_NAME
    ) -> Tuple[str, List[str]]:
        """Pass."""
        search = value.strip().lower()

        if ":" in search:
            adapter_split, field = search.split(":", 1)
            if not adapter_split:
                adapter_split = adapter
        else:
            field = search
            adapter_split = adapter

        # XXX needs test case
        qual_check = re.match(r"adapters_data\.(.*?)\.", field)
        if qual_check and len(qual_check.groups()) == 1:
            adapter_split = qual_check.groups()[0]

        adapter_split = strip_right(obj=adapter_split.lower().strip(), fix="_adapter")

        fields = split_str(
            obj=field, split=",", strip=None, do_strip=True, lower=True, empty=False,
        )

        if not fields:
            msg = "No fields provided in {!r}, format must be 'adapter:field'"
            msg = msg.format(value)
            raise ApiError(msg)

        return adapter_split, fields

    def _get(self) -> dict:
        """Direct API method to get the schema of all fields.

        Returns:
            :obj:`dict`: schema of all fields
        """
        return self.request(method="get", path=self.router.fields)

    def _prettify_schemas(self, schemas: List[dict]) -> List[str]:
        """Pass."""
        stmpl = "{adapter_name}:{name_base:{name_base_len}} -> {column_title}".format
        name_base_len = max([len(x["name_base"]) for x in schemas])
        return [stmpl(name_base_len=name_base_len, **x) for x in schemas]
