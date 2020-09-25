# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import re
from typing import List, Optional, Tuple, Union

from cachetools import TTLCache, cached
from fuzzywuzzy import fuzz

from ...constants import (
    AGG_ADAPTER_ALTS,
    AGG_ADAPTER_NAME,
    FUZZY_SCHEMAS_KEYS,
    GET_SCHEMA_KEYS,
    GET_SCHEMAS_KEYS,
)
from ...exceptions import ApiError, NotFoundError
from ...tools import listify, split_str, strip_right
from ..mixins import ChildMixins
from ..parsers.fields import parse_fields

CACHE: TTLCache = TTLCache(maxsize=1024, ttl=300)


class Fields(ChildMixins):
    """Child API model for working with fields for the parent asset type."""

    @staticmethod
    def fuzzy_filter(
        search: str,
        schemas: List[dict],
        root_only: bool = True,
        do_contains: bool = True,
        token_score: int = 70,
        partial_score: int = 50,
        names: bool = False,
        **kwargs,
    ) -> List[dict]:
        def do_skip():
            if schema in matches:
                return True

            if schema["name"].endswith("_details"):
                return True

            if schema["name"] == "all":
                return True

            if root_only and not schema["is_root"]:
                return True

            if not schema.get("selectable", True):
                return True

            return False

        def is_match(method, **kwargs):
            for key in keys:
                if method(search, schema[key], **kwargs):
                    return True

            return False

        def token_set_ratio(search, value, score=70, **kwargs):
            return fuzz.token_set_ratio(search, value) >= score

        def partial_ratio(search, value, score=50, **kwargs):
            return fuzz.partial_ratio(search, value) >= score

        def contains(search, value, **kwargs):
            return search.strip().lower() in value.strip().lower()

        keys = kwargs.get("fuzzy_keys", FUZZY_SCHEMAS_KEYS)

        matches = []

        for schema in schemas:
            if do_contains and not do_skip() and is_match(contains):
                matches.append(schema)

            if token_score and not do_skip() and is_match(token_set_ratio):
                matches.append(schema)

        if partial_score and not matches:
            for schema in schemas:
                if not do_skip() and is_match(partial_ratio):
                    matches.append(schema)

        return [x["name_qual"] for x in matches] if names else matches

    @cached(cache=CACHE)
    def get(self) -> dict:
        """Get the schema of all adapters and their fields.

        Returns:
            :obj:`dict`: parsed output from :meth:`ParserFields.parse`
        """
        return parse_fields(raw=self._get())

    def get_adapter_names(self, value: str) -> List[str]:
        """Find an adapter by name regex."""
        fields = self.get()

        search = strip_right(obj=value.lower().strip(), fix="_adapter")

        if search in AGG_ADAPTER_ALTS:
            search = AGG_ADAPTER_NAME

        search = re.compile(search, re.I)
        matches = [x for x in fields if search.search(x)]

        if not matches:
            msg = ("No adapter found where name regex matches {!r}, valid adapters:\n  {}").format(
                value, "\n  ".join(list(fields))
            )
            raise NotFoundError(msg)
        return matches

    def get_adapter_name(self, value: str) -> str:
        """Find an adapter by name."""
        fields = self.get()

        search = strip_right(obj=value.lower().strip(), fix="_adapter")

        if search in AGG_ADAPTER_ALTS:
            search = AGG_ADAPTER_NAME

        if search in fields:
            return search

        msg = "No adapter found where name equals {!r}, valid adapters:\n  {}"
        msg = msg.format(value, "\n  ".join(list(fields)))
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
        keys_fuzzy = kwargs.get("keys_fuzzy", FUZZY_SCHEMAS_KEYS)

        search = value.lower().strip()

        schemas = [x for x in schemas if x.get("selectable", True)]

        for schema in schemas:
            for key in keys:
                if search.lower().strip() == schema[key].lower():
                    return schema

        err = "No fuzzy matches, all valid fields:"

        kwargs["search"] = value
        kwargs["schemas"] = schemas
        fuzzy = self.fuzzy_filter(**kwargs)
        if fuzzy:
            keys = keys_fuzzy
            err = "Maybe you meant one of these fuzzy matches:"

        ktxt = " or ".join(keys)
        pre = f"No field found where {ktxt} equals {value!r}"
        errs = [pre, err, "", *self._prettify_schemas(schemas=fuzzy or schemas)]
        raise NotFoundError("\n".join(errs))

    def get_field_name(
        self,
        value: str,
        field_manual: bool = False,
        fields_custom: Optional[dict] = None,
        key: str = "name_qual",
    ) -> str:
        """Pass."""
        if field_manual:
            return value

        adapter, fields = self.split_search(value=value)

        if len(fields) != 1:
            raise ApiError("More than one field supplied to {}".format(value))

        field = fields[0]

        fields = self.get()
        adapter = self.get_adapter_name(value=adapter)
        schemas = fields[adapter]
        if fields_custom and adapter in fields_custom:
            schemas += fields_custom[adapter]
        schema = self.get_field_schema(value=field, schemas=schemas)
        return schema[key] if key else schema

    def get_field_names_re(self, value: str) -> List[str]:
        """Pass."""
        splits = self.split_searches(value=value)
        fields = self.get()

        matches = []

        for adapter_re, fields_re in splits:
            adapters = self.get_adapter_names(value=adapter_re)

            for adapter in adapters:
                for field_re in fields_re:
                    fschemas = self.get_field_schemas(value=field_re, schemas=fields[adapter])
                    names = [x["name_qual"] for x in fschemas]
                    matches += [x for x in names if x not in matches]
        return matches

    def get_field_names_eq(self, value: str) -> List[str]:
        """Pass."""
        splits = self.split_searches(value=value)
        fields = self.get()

        matches = []

        for adapter_name, names in splits:
            adapter = self.get_adapter_name(value=adapter_name)
            for name in names:
                schemas = fields[adapter]
                schema = self.get_field_schema(value=name, schemas=schemas)
                if schema["name_qual"] not in matches:
                    matches.append(schema["name_qual"])

        return matches

    def get_field_names_fuzzy(self, value: str) -> List[str]:
        """Pass."""
        splits = self.split_searches(value=value)
        fields = self.get()

        matches = []

        for adapter_name, names in splits:
            adapter = self.get_adapter_name(value=adapter_name)
            for name in names:
                schemas = fields[adapter]
                amatches = self.fuzzy_filter(search=name, schemas=schemas, names=True)
                matches += [x for x in amatches if x not in matches]

        return matches

    def get_field_schemas_root(self, adapter: str) -> List[dict]:
        """Pass."""
        fields = self.get()
        adapter = self.get_adapter_name(value=adapter)
        schemas = fields[adapter]

        matches = [x for x in schemas if x.get("selectable") and x.get("is_root")]
        return matches

    def get_field_names_root(self, adapter: str) -> List[str]:
        """Pass."""
        schemas = self.get_field_schemas_root(adapter=adapter)
        names = [x["name_qual"] for x in schemas]
        return names

    def validate(
        self,
        fields: Optional[Union[List[str], str]] = None,
        fields_regex: Optional[Union[List[str], str]] = None,
        fields_manual: Optional[Union[List[str], str]] = None,
        fields_fuzzy: Optional[Union[List[str], str]] = None,
        fields_default: bool = True,
        fields_root: Optional[str] = None,
    ) -> List[dict]:
        """Validate provided fields."""

        def add(items):
            for item in items:
                if item not in selected:
                    selected.append(item)

        fields = listify(obj=fields)
        fields_manual = listify(obj=fields_manual)
        fields_fuzzy = listify(obj=fields_fuzzy)

        selected = []

        if fields_default and not fields_root:
            add(self.parent.fields_default)

        if fields_root:
            add(self.get_field_names_root(adapter=fields_root))

        add(fields_manual)
        add(self.get_field_names_eq(value=fields))
        add(self.get_field_names_re(value=fields_regex))
        add(self.get_field_names_fuzzy(value=fields_fuzzy))

        if not selected:
            raise ApiError("No fields supplied, must supply at least one field")

        return selected

    def split_searches(self, value: Union[List[str], str]) -> List[Tuple[str, List[str]]]:
        """Pass."""
        return [self.split_search(value=x) for x in listify(obj=value)]

    def split_search(self, value: str, adapter: str = AGG_ADAPTER_NAME) -> Tuple[str, List[str]]:
        """Pass."""
        search = value.strip().lower()

        if ":" in search:
            adapter_split, field = search.split(":", 1)
            if not adapter_split:
                adapter_split = adapter
        else:
            field = search
            adapter_split = adapter

        qual_check = re.match(r"adapters_data\.(.*?)\.", field)
        if qual_check and len(qual_check.groups()) == 1:
            adapter_split = qual_check.groups()[0]

        adapter_split = strip_right(obj=adapter_split.lower().strip(), fix="_adapter")

        fields = split_str(
            obj=field,
            split=",",
            strip=None,
            do_strip=True,
            lower=True,
            empty=False,
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
