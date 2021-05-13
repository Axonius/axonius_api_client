# -*- coding: utf-8 -*-
"""API for working with fields for assets."""
import re
from typing import List, Optional, Tuple, Union

from cachetools import TTLCache, cached
from fuzzyfinder import fuzzyfinder

from ...constants.fields import (
    AGG_ADAPTER_ALTS,
    AGG_ADAPTER_NAME,
    FUZZY_SCHEMAS_KEYS,
    GET_SCHEMA_KEYS,
    GET_SCHEMAS_KEYS,
    PRETTY_SCHEMA_TMPL,
)
from ...exceptions import ApiError, NotFoundError
from ...parsers.fields import parse_fields
from ...tools import listify, split_str, strip_right
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..mixins import ChildMixins


class Fields(ChildMixins):
    """API for working with fields for the parent asset type.

    Examples:
        Create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
        ``apiobj`` is either ``client.devices`` or ``client.users``

        >>> apiobj = client.devices  # or client.users

        * Get schemas of all adapters and their fields: :meth:`get`
        * Validate field names supplied: :meth:`validate`

    See Also:
        * Device assets :obj:`axonius_api_client.api.assets.devices.Devices`
        * User assets :obj:`axonius_api_client.api.assets.users.Users`
    """

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def get(self) -> dict:
        """Get the schema of all adapters and their fields.

        Examples:
            Get all fields for all adapters

            >>> fields = apiobj.fields.get()

            See the adapter names

            >>> print(list(fields))

            See the field fully qualified name, short name, and title for all fields of an adapter

            >>> schemas = fields['agg']
            >>> for schema in schemas:
            ...     qual = schema['name_qual']
            ...     name = schema['name_base']
            ...     title = schema['title']
            ...     print(f"title {title!r}, qualified name {name!r}, base name {name!r}")

        """
        return parse_fields(raw=self._get().document_meta)

    def validate(
        self,
        fields: Optional[Union[List[str], str]] = None,
        fields_regex: Optional[Union[List[str], str]] = None,
        fields_manual: Optional[Union[List[str], str]] = None,
        fields_fuzzy: Optional[Union[List[str], str]] = None,
        fields_default: bool = True,
        fields_root: Optional[str] = None,
    ) -> List[dict]:
        """Get the fully qualified field names for getting asset data.

        Examples:
            * ``fields`` gets parsed by :meth:`get_field_names_eq`
            * ``fields_regex`` gets parsed by :meth:`get_field_names_re`
            * ``fields_fuzzy`` gets parsed by :meth:`get_field_names_fuzzy`
            * ``fields_root`` gets parsed by :meth:`get_field_names_root`
            * ``fields_default`` will add
              :attr:`axonius_api_client.api.assets.users.Users.fields_default` or
              :attr:`axonius_api_client.api.assets.devices.Devices.fields_default`
              based on the parent asset type

        Notes:
            This is used in a number of ways to allow the user to supply fields that
            are easier to refer to than the fully qualified name or title of a field.

        Args:
            fields: list of fields that must equal their base name, qual name, or title
            fields_regex: list of fields to regex match against their base name, qual name, or title
            fields_manual: list of already fully qualified field names
            fields_fuzzy: list of fields to fuzzy match against their base name or title
            fields_default: include the default fields defined in the parent API object
            fields_root: include all root fields from a single adapter

        Raises:
            :exc:`ApiError`: if no fields selected after all processing is done

        """

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

    def get_field_name(
        self,
        value: str,
        field_manual: bool = False,
        fields_custom: Optional[dict] = None,
        key: str = "name_qual",
    ) -> str:
        """Get the fully qualified name of a field.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
            ``apiobj`` is either ``client.devices`` or ``client.users``

            >>> apiobj = client.devices

            Get the FQDN of a field on the aggregated adapter

            >>> apiobj.fields.get_field_name(value='hostname')
            'specific_data.data.hostname'
            >>> apiobj.fields.get_field_name(value='agg:hostname')
            'specific_data.data.hostname'

            Get the title of a field on the aggregated adapter

            >>> apiobj.fields.get_field_name(value='hostname', key="title")
            'Host Name'

            Get the FQDN of a field on the AWS adapter

            >>> apiobj.fields.get_field_name(value='aws:aws_device_type')
            'adapters_data.aws_adapter.aws_device_type'

        Args:
            value: field to find in format of ``adapter_name:field_name``
            field_manual: treat the field name as fully qualified
            fields_custom: custom schemas to search thru in addition to API schemas
            key: key of schema to return, or if empty return the schema itself

        Raises:
            :exc:`ApiError`: if more than one field found in value after splitting it
        """
        if field_manual and key:
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

    def get_field_names_re(self, value: Union[str, List[str]], key: str = "name_qual") -> List[str]:
        """Get field names using regex.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
            ``apiobj`` is either ``client.devices`` or ``client.users``

            >>> apiobj = client.devices

            Get all aggregated field FQDNs that start with host

            >>> apiobj.fields.get_field_names_re('^host')
            ['specific_data.data.hostname', 'specific_data.data.hostname_preferred']


            Get fields names for AWS adapter that start with id and AGG adapter that start with
            host

            >>> apiobj.fields.get_field_names_re(['aws:^id', '^host'])
            [
                'adapters_data.aws_adapter.id',
                'specific_data.data.hostname',
                'specific_data.data.hostname_preferred'
            ]

            Get all aggregated field titles that start with host

            >>> apiobj.fields.get_field_names_re('^host', key="title")
            ['Host Name', 'Preferred Host Name']

            Get all aggregated field FQDNs that have a title of 'Host Name'

            >>> apiobj.fields.get_field_names_re('Host Name')
            ['specific_data.data.hostname', 'specific_data.data.hostname_preferred']

            Get all field FQDNs that start with id for all adapters that match regex 'ac'

            >>> apiobj.fields.get_field_names_re('ac:^id')
            [
                'adapters_data.active_directory_adapter.id',
                'adapters_data.carbonblack_defense_adapter.id',
                'adapters_data.limacharlie_adapter.id'
            ]

        Args:
            value: regex to search for fields
            key: key of schema to return
        """
        splits = self.split_searches(value=value)
        fields = self.get()

        matches = []

        for adapter_re, fields_re in splits:
            adapters = self.get_adapter_names(value=adapter_re)

            for adapter in adapters:
                for field_re in fields_re:
                    fschemas = self.get_field_schemas(value=field_re, schemas=fields[adapter])
                    names = [x[key] for x in fschemas]
                    matches += [x for x in names if x not in matches]
        return matches

    def get_field_names_eq(self, value: Union[str, List[str]], key: str = "name_qual") -> List[str]:
        """Get field names that equal a value.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
            ``apiobj`` is either ``client.devices`` or ``client.users``

            >>> apiobj = client.devices

            Get field names that equal aggregated hostname or id and AWS device type

            >>> apiobj.fields.get_field_names_eq(['hostname,id', 'aws:aws_device_type'])
            [
                'specific_data.data.hostname',
                'specific_data.data.id',
                'adapters_data.aws_adapter.aws_device_type'
            ]

            Get field names that equal aggregated hostname or id

            >>> apiobj.fields.get_field_names_eq('hostname,id')
            ['specific_data.data.hostname', 'specific_data.data.id']

        Args:
            value: value to search for fields
            key: key of schema to return
        """
        splits = self.split_searches(value=value)
        fields = self.get()

        matches = []

        for adapter_name, names in splits:
            adapter = self.get_adapter_name(value=adapter_name)
            for name in names:
                schemas = fields[adapter]
                schema = self.get_field_schema(value=name, schemas=schemas)
                match = schema[key] if key else schema
                if match not in matches:
                    matches.append(match)

        return matches

    def get_field_names_fuzzy(self, value: str, key: str = "name_qual") -> List[str]:
        """Get field names using that equal a value.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
            ``apiobj`` is either ``client.devices`` or ``client.users``

            >>> apiobj = client.devices

            Get field names that fuzzy match a misspelt version of hostname

            >>> apiobj.fields.get_field_names_fuzzy('hostnme')
            ['specific_data.data.hostname']

        Args:
            value: value to search for fields
            key: key of schema to return

        """
        splits = self.split_searches(value=value)
        fields = self.get()

        matches = []

        for adapter_name, names in splits:
            adapter = self.get_adapter_name(value=adapter_name)
            for name in names:
                schemas = fields[adapter]
                amatches = self.fuzzy_filter(search=name, schemas=schemas, key=key, root_only=True)
                matches += [x for x in amatches if x not in matches]

        return matches

    def get_field_schemas_root(self, adapter: str) -> List[dict]:
        """Get schemas of all root fields for a given adapter.

        Args:
            adapter: name of adapter to get all root fields for

        See Also:
            :meth:`get_field_names_root`

        Notes:
            root fields are fields that are fields that are not sub-fields of complex fields

            For instance 'specific_data.data.network_interfaces.ips' is NOT a root field,
            since it 'ips' is a sub field of 'specific_data.data.network_interfaces'

        """
        fields = self.get()
        adapter = self.get_adapter_name(value=adapter)
        schemas = fields[adapter]

        matches = [x for x in schemas if x.get("selectable") and x.get("is_root")]
        return matches

    def get_field_names_root(self, adapter: str, key: str = "name_qual") -> List[str]:
        """Get names of all root fields for a given adapter.

        Args:
            adapter: name of adapter to get all root fields for

        See Also:
            :meth:`get_field_schemas_root`

        """
        schemas = self.get_field_schemas_root(adapter=adapter)
        names = [x[key] for x in schemas]
        return names

    @staticmethod
    def fuzzy_filter(
        search: str,
        schemas: List[dict],
        root_only: bool = False,
        key: str = "name_qual",
        fuzzy_keys: List[str] = FUZZY_SCHEMAS_KEYS,
        **kwargs,
    ) -> List[dict]:
        """Perform a fuzzy search against a set of field schemas.

        Args:
            search: string to search for against the keys in fuzzy_keys
            schemas: field schemas to search through
            root_only: only search against schemas of root fields
            key: return the schema key value instead of the field schemas
            fuzzy_keys: list of keys to check search against in each field schema
        """

        def do_skip(schema):
            is_details = schema["name"].endswith("_details")
            is_all = schema["name"] == "all"
            not_select = not schema.get("selectable", True)
            is_root = root_only and not schema["is_root"]

            if any([schema in matches, is_details, is_all, not_select, is_root]):
                return True

            return False

        matches = []

        for schema in schemas:
            if do_skip(schema):
                continue

            values = [schema[x] for x in fuzzy_keys]

            if any([search.strip().lower() in x for x in values]):
                matches.append(schema)

        if not matches:
            for schema in schemas:
                if do_skip(schema):
                    continue

                values = [schema[x] for x in fuzzy_keys]

                if list(fuzzyfinder(search, values)):
                    matches.append(schema)

        return [x[key] for x in matches] if key else matches

    def get_adapter_names(self, value: str) -> List[str]:
        """Find adapter names that regex match a value.

        Args:
            value: regex of adapter to match

        Raises:
            :exc:`NotFoundError`: when no adapter name matches supplied value
        """
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
        """Find an adapter name that equals a value.

        Args:
            value: name of adapter

        Raises:
            :exc:`NotFoundError`: when no adapter name equals supplied value
        """
        fields = self.get()

        search = strip_right(obj=value.lower().strip(), fix="_adapter")

        if search in AGG_ADAPTER_ALTS:
            search = AGG_ADAPTER_NAME

        if search in fields:
            return search

        msg = "No adapter found where name equals {!r}, valid adapters:\n  {}"
        msg = msg.format(value, "\n  ".join(list(fields)))
        raise NotFoundError(msg)

    def get_field_schemas(
        self, value: str, schemas: List[dict], keys: List[str] = GET_SCHEMAS_KEYS
    ) -> List[dict]:
        """Find field schemes that regex match a value.

        Args:
            value: regex of name to match
            schemas: list of field schemas to search through
            keys: list of keys to check regex value against
        """
        search = re.compile(value.lower().strip(), re.I)

        matches = []

        for schema in schemas:
            if not schema.get("selectable"):
                continue

            for key in keys:
                if search.search(schema[key]) and schema not in matches:
                    matches.append(schema)
        return matches

    def get_field_schema(
        self,
        value: str,
        schemas: List[dict],
        keys: List[str] = GET_SCHEMA_KEYS,
        **kwargs,
    ) -> dict:
        """Find a field name that equals a value.

        Args:
            value: name of field
            schemas: list of field schemas to search through
            keys: list of keys to check if value equals
            **kwargs: passed to :meth:`fuzzy_filter` to print fuzzy matches in error
                if no matches found

        Raises:
            :exc:`NotFoundError`: when no field name equals supplied value
        """
        search = value.lower().strip()

        schemas = [x for x in schemas if x.get("selectable", True)]

        for schema in schemas:
            for key in keys:
                if search.lower().strip() == schema[key].lower():
                    return schema

        kwargs["search"] = value
        kwargs["schemas"] = schemas
        kwargs["key"] = ""
        fuzzy = self.fuzzy_filter(**kwargs)

        err = "No fuzzy matches, all valid fields:"
        if fuzzy:
            keys = kwargs.get("keys_fuzzy", FUZZY_SCHEMAS_KEYS)
            err = "Maybe you meant one of these fuzzy matches:"

        ktxt = " or ".join(keys)
        pre = f"No field found where {ktxt} equals {value!r}"
        errs = [pre, err, "", *self._prettify_schemas(schemas=fuzzy or schemas)]
        raise NotFoundError("\n".join(errs))

    def split_searches(self, value: Union[List[str], str]) -> List[Tuple[str, List[str]]]:
        """Split a list of strings into adapter:field(s) format.

        Args:
            value: format of ``'adapter:field1,field2'`` or
                ``['adapter1:field1', 'adapter2:field2']``

        """
        return [self.split_search(value=x) for x in listify(obj=value)]

    def split_search(self, value: str, adapter: str = AGG_ADAPTER_NAME) -> Tuple[str, List[str]]:
        """Split a string into adapter and field(s).

        Args:
            value: format of ``'adapter:field1,field2'`` or ``'field1,field2'`` or
                ``'field1'``
            adapter: default adapter name to use if no 'adapter:' found in value

        Raises:
            :exc:`ApiError`: if no fields found after splitting on ':'
        """
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

    def _prettify_schemas(
        self, schemas: List[dict], tmpl: str = PRETTY_SCHEMA_TMPL, len_key: str = "name_base"
    ) -> List[str]:
        """Prettify a set of schemas for output in human friendly format.

        Args:
            schemas: field schemas to prettify
            tmpl: template to use to prettify schemas
            len_key: schema key to get max length of and pass into tmpl as "len_max"
        """
        len_max = max([len(x[len_key]) for x in schemas]) if schemas else 0
        return [tmpl.format(len_max=len_max, **x) for x in schemas]

    def _get(self) -> json_api.generic.Metadata:
        """Private API method to get the schema of all fields."""
        api_endpoint = ApiEndpoints.assets.fields
        return api_endpoint.perform_request(http=self.auth.http, asset_type=self.parent.ASSET_TYPE)
