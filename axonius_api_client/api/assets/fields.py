# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import re

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

    def get(self):
        """Get the schema of all adapters and their fields.

        Returns:
            :obj:`dict`: parsed output from :meth:`ParserFields.parse`
        """
        return parse_fields(raw=self._get())

    def get_adapter_names(self, value, fields_map=None):
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

    def get_adapter_name(self, value, fields_map=None):
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

    def get_field_schemas(self, value, schemas, **kwargs):
        """Find a schema for a field by regex of name."""
        keys = kwargs.get("keys", GET_SCHEMAS_KEYS)
        search = re.compile(value.lower().strip(), re.I)

        matches = []

        for schema in schemas:
            for key in keys:
                if search.search(schema[key]) and schema not in matches:
                    matches.append(schema)

        # XXX fix test case for this
        # os\. will fail for adapters that do not have os.type/dist/etc
        # if not matches:
        #     msg = "No field found where {} matches regex {!r}, valid fields: \n{}"
        #     msg = msg.format(
        #         keys, value, "\n".join(self._prettify_schemas(schemas=schemas)),
        #     )
        #     raise NotFoundError(msg)
        return matches

    def get_field_schema(self, value, schemas, **kwargs):
        """Find a schema for a field by name."""
        keys = kwargs.get("keys", GET_SCHEMA_KEYS)
        search = value.lower().strip()

        for schema in schemas:
            for key in keys:
                if search == schema[key].lower():
                    return schema

        msg = "No field found where any of {} equals {!r}, valid fields: \n{}"
        msg = msg.format(keys, value, "\n".join(self._prettify_schemas(schemas=schemas)))
        raise NotFoundError(msg)

    def get_field_name(self, value, field_manual=False, fields_map=None):
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
        schema = self.get_field_schema(value=field, schemas=schemas)
        return schema["name_qual"]

    def get_field_names_re(self, value, fields_map=None):
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

    def get_field_names_eq(self, value, fields_map=None):
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

    def validate(
        self,
        fields=None,
        fields_regex=None,
        fields_manual=None,
        fields_default=True,
        fields_map=None,
    ):
        """Validate provided fields."""
        fields_manual = listify(obj=fields_manual)

        selected = []

        if fields_default:
            selected += self.parent.fields_default

        if fields_manual:
            selected += [x for x in fields_manual if x not in selected]

        if not any([fields, fields_regex]):
            if not selected:
                raise ApiError("No fields supplied, must supply at least one field")
            return selected

        fields_map = fields_map or self.get()

        for field in self.get_field_names_eq(value=fields, fields_map=fields_map):
            if field not in selected:
                selected.append(field)

        for field in self.get_field_names_re(value=fields_regex, fields_map=fields_map):
            if field not in selected:
                selected.append(field)

        return selected

    def split_searches(self, value):
        """Pass."""
        return [self.split_search(value=x) for x in listify(obj=value)]

    def split_search(self, value, adapter=AGG_ADAPTER_NAME):
        """Pass."""
        search = value.strip().lower()

        if ":" in search:
            adapter_split, field = search.split(":", 1)
            if not adapter_split:
                adapter_split = adapter
        else:
            field = search
            adapter_split = adapter

        adapter_split = strip_right(obj=adapter_split.lower().strip(), fix="_adapter")

        fields = split_str(
            obj=field, split=",", strip=None, do_strip=True, lower=True, empty=False,
        )

        if not fields:
            msg = "No fields provided in {!r}, format must be 'adapter:field'"
            msg = msg.format(value)
            raise ApiError(msg)

        return adapter_split, fields

    def _get(self):
        """Direct API method to get the schema of all fields.

        Returns:
            :obj:`dict`: schema of all fields
        """
        return self.request(method="get", path=self.router.fields)

    def _prettify_schemas(self, schemas):
        """Pass."""
        stmpl = "{adapter_name}:{name_base:{name_base_len}} -> {column_title}".format
        name_base_len = max([len(x["name_base"]) for x in schemas])
        return [stmpl(name_base_len=name_base_len, **x) for x in schemas]
