# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re

from .. import constants, exceptions, tools
from . import mixins


class Fields(mixins.Child):
    """Child API model for working with fields for the parent asset type."""

    _GENERIC_ALTS = ["generic", "general", "specific", "agg", "aggregated"]
    """:obj:`list` of :obj:`str`: list of alternatives for 'generic' adapter."""
    _ALL_ALTS = ["all", "*", "specific_data"]
    """:obj:`list` of :obj:`str`: list of alternatives for getting 'all' fields."""

    def pretty_schemas(self, schemas):
        """Pass."""
        stmpl = "{column_name:{longest}} -> {column_title}".format
        longest = tools.longest_str([x["column_name"] for x in schemas.values()])
        schemas = [stmpl(longest=longest, **v) for v in schemas.values()]
        return schemas

    def _get(self):
        """Direct API method to get the schema of all fields.

        Returns:
            :obj:`dict`: schema of all fields
        """
        return self._parent._request(method="get", path=self._parent._router.fields)

    def find_adapter(self, adapter, error=True, all_fields=None):
        """Find an adapter by name.

        Args:
            adapter (:obj:`str`): Description
            error (:obj:`bool`, optional): default ``True`` - throw exc if no
                matches found for **adapter**
            all_fields (:obj:`list` of :obj:`dict`, optional): default ``None`` -
                if not supplied, will use return of :meth:`get`

        Returns:
            :obj:`tuple` of (:obj:`str`, :obj:`dict`):
                fully qualified name of adapter and its field schemas

        Raises:
            exceptions.ValueNotFound: if **adapter** does not match the name keys
                of any keys in **all_fields**
        """
        all_fields = all_fields or self.get()

        check = tools.strip_right(obj=adapter.lower().strip(), fix="_adapter")

        if check in self._GENERIC_ALTS:
            check = "aggregated"

        if check in all_fields:
            vmsg = "Validated adapter name {cn!r} (supplied {n!r})"
            vmsg = vmsg.format(n=adapter, cn=check)
            self._log.debug(vmsg)

            return check, all_fields[check]

        if error:
            raise exceptions.ValueNotFound(
                value=adapter,
                value_msg="adapter by name",
                known=list(all_fields),
                known_msg="adapter names",
            )

        fmsg = "Failed to validate adapter {cn!r} (supplied {n!r})"
        fmsg = fmsg.format(n=adapter, cn=check)
        self._log.warning(fmsg)

        return None, {}

    def get_schemas_flat(self, short=False, all_fields=None):
        """Return a flat dict of fields keyed on the fqdn of field."""
        all_fields = all_fields or self.get()
        if short:
            return {
                f["column_name"]: f for fs in all_fields.values() for f in fs.values()
            }
        return {f["name"]: f for fs in all_fields.values() for f in fs.values()}

    def get_schemas(self, fields, all_fields=None):
        """Get the flattened schema of selected fields."""
        all_fields = all_fields or self.get()
        flat = self.get_schemas_flat(all_fields=all_fields)

        schemas = {}
        for field in fields:
            if field in flat:
                schemas[field] = flat[field]
            else:
                self._log.warning("field {} not found in schemas!".format(field))
        return schemas

    def find_single(self, field, all_fields=None):
        """Find a single field.

        Args:
            field (:obj:`str`): name of field to find
            all_fields (:obj:`list` of :obj:`dict`, optional): default ``None`` -
                if not supplied, will use return of :meth:`get`

        Returns:
            :obj:`str`: validated and processed field
        """
        found = self.find(field=field, error=True, all_fields=all_fields)
        return found[0]

    def find(self, field, error=True, all_fields=None):
        """Find a field for a given adapter.

        Args:
            field (:obj:`str` or :obj:`list` of :obj:`str`): name(s) of fields
                to find
            error (:obj:`bool`, optional): default ``True`` - throw exc if field
                can not be found
            all_fields (:obj:`list` of :obj:`dict`, optional): default ``None`` -
                if not supplied, will use return of :meth:`get`

        Returns:
            :obj:`list` of :obj:`str`: validated and processed fields

        Raises:
            :exc:`exceptions.ValueNotFound`: if **field** not found and **error** is True
        """
        all_fields = all_fields or self.get()

        all_fq = [f["name"] for af in all_fields.values() for f in af.values()]

        check = field.strip()

        if check in all_fq:
            fqmsg = "Validated field {sf!r} as already fully qualified"
            fqmsg = fqmsg.format(sf=field)
            self._log.debug(fqmsg)

            return [check]

        if ":" in check:
            search_adapter, search_fields = check.split(":", 1)
        else:
            search_adapter, search_fields = ("aggregated", check)

        search_adapter = search_adapter.strip()
        search_fields = tools.split_str(obj=search_fields)

        if not search_fields:
            msg = "No fields provided in {!r}, format must be 'adapter:field'"
            msg = msg.format(field)
            raise exceptions.ApiError(msg)

        real_adapter, real_fields = self.find_adapter(
            adapter=search_adapter, error=error, all_fields=all_fields
        )

        found = []

        if not real_adapter:
            return found

        for search_field in search_fields:
            found_field = None

            if search_field.startswith("manual_"):
                found_field = tools.strip_left(obj=search_field, fix="manual_").strip()
            else:
                if search_field in self._ALL_ALTS:
                    found_field = real_fields["all"]["name"]
                elif search_field in all_fq:
                    found_field = search_field
                elif search_field in real_fields:
                    found_field = real_fields[search_field]["name"]

            if not found_field:
                if error:
                    value_msg = "adapter {a!r} field"
                    value_msg = value_msg.format(a=real_adapter)

                    known_msg = "field names for adapter {a!r}"
                    known_msg = known_msg.format(a=real_adapter)
                    pretty_schemas = sorted(self.pretty_schemas(schemas=real_fields))

                    raise exceptions.ValueNotFound(
                        value=search_field,
                        known=pretty_schemas,
                        value_msg=value_msg,
                        known_msg=known_msg,
                    )

                wmsg = "Failed to validate field {sf!r} for adapter {a!r} as {ff!r}"
                wmsg = wmsg.format(a=real_adapter, sf=search_field, ff=found_field)
                self._log.warning(wmsg)
            else:
                if found_field not in found:
                    found.append(found_field)

                vfmsg = "Validated field {sf!r} for adapter {a!r} as {ff!r}"
                vfmsg = vfmsg.format(a=real_adapter, sf=search_field, ff=found_field)
                self._log.debug(vfmsg)

        vsmsg = "Validated field search {s!r} as {f!r}"
        vsmsg = vsmsg.format(s=field, f=found)
        self._log.debug(vsmsg)

        return found

    def find_regex(self, field, all_fields=None):
        """Find a field for a given adapter using regexes.

        Args:
            field (:obj:`str` or :obj:`list` of :obj:`str`): regex(es) of fields
                to find
            all_fields (:obj:`list` of :obj:`dict`, optional): default ``None`` -
                if not supplied, will use return of :meth:`get`

        Returns:
            :obj:`list` of :obj:`str`: validated and processed fields
        """
        all_fields = all_fields or self.get()

        check = field.strip()

        if ":" in check:
            search_adapter, search_fields = check.split(":", 1)
        else:
            search_adapter, search_fields = (".", check)

        search_adapter_fix = tools.strip_right(
            obj=search_adapter.lower().strip(), fix="_adapter"
        )

        search_adapter_re = re.compile(search_adapter_fix, re.I)
        found_adapters = {
            k: v for k, v in all_fields.items() if search_adapter_re.search(k)
        }

        search_fields = [x.strip() for x in search_fields if x.strip()]

        if not search_fields:
            msg = "No fields provided in {!r}, format must be 'adapter:field_regex'"
            msg = msg.format(field)
            raise exceptions.ApiError(msg)

        search_fields_re = [
            re.compile(x.strip().lower(), re.I) for x in search_fields.split(",")
        ]

        found_fields = []

        for field_re in search_fields_re:
            for adapter, adapter_fields in found_adapters.items():
                for adapter_field, adapter_field_info in adapter_fields.items():
                    if field_re.search(adapter_field):
                        found_fields.append(adapter_field_info["name"])

        return found_fields

    def get(self):
        """Direct API method to get the schema of all fields.

        Returns:
            :obj:`dict`: parsed output from :meth:`ParserFields.parse`
        """
        raw = self._get()
        parser = ParserFields(raw=raw, parent=self)
        return parser.parse()

    def validate(
        self,
        fields=None,
        fields_regex=None,
        fields_manual=None,
        default=True,
        error=True,
        all_fields=None,
    ):
        """Validate provided fields.

        Args:
            fields (:obj:`list` of :obj:`str`, optional): default ``None`` -
                fields to parse, find, and add
            fields_regex (:obj:`list` of :obj:`str`, optional): default ``None`` -
                list of fields to find and add using regular expression matches
            fields_manual (:obj:`list` of :obj:`str`, optional): default ``None`` -
                list of fully qualified fields to add
            fields_default (:obj:`bool`, optional): default ``True`` -
                add the fields in _default_fields from the parent asset object
            error (:obj:`bool`, optional): default ``True`` - throw exc if field
                can not be found
            all_fields (:obj:`list` of :obj:`dict`, optional): default ``None`` -
                if not supplied, will use return of :meth:`get`

        Returns:
            :obj:`list` of :obj:`str`: fields that have been parsed, fully qualified,
                and validated
        """

        def listify(obj):
            return [
                x for x in tools.listify(obj=obj) if isinstance(x, constants.STR) and x
            ]

        fields = listify(obj=fields)
        fields_manual = listify(obj=fields_manual)
        fields_regex = listify(obj=fields_regex)
        all_fields = all_fields or self.get()

        val_fields = []

        if default:
            val_fields += self._parent._default_fields

        val_fields += fields_manual

        for field in fields:
            found = self.find(field=field, all_fields=all_fields, error=error)
            val_fields += [x for x in found if x not in val_fields]

        for field_re in fields_regex:
            found_re = self.find_regex(field=field_re, all_fields=all_fields)
            val_fields += [x for x in found_re if x not in val_fields]

        return val_fields


class ParserFields(mixins.Parser):
    """Parser to make the raw fields returned by the API into a more usable format."""

    def _add(self, key, value, dest):
        """Sanity check to make sure a key is not duplicated during parsing.

        Args:
            key (:obj:`str`): key to check in dest
            dest (:obj:`list` of :obj:`str`): obj to check if key already exists in
            desc (:obj:`str`): description of key

        Raises:
            :exc:`exceptions.ApiError`: if key already exists in dest
        """
        if key in dest:
            msg = "Key {key!r} value {value!r} already exists in {dest}"
            msg = msg.format(value=value, key=key, dest=dest)
            raise exceptions.ApiError(msg)
        dest[key] = value

    @property
    def _fmaps(self):
        """Map of field types into their normalized typed.

        Returns:
            :obj:`tuple` of :obj:`tuple`
        """
        return (
            # (type, format, items.type, items.format), normalized
            (("string", "", "", ""), "string"),
            (("string", "date-time", "", ""), "string_datetime"),
            (("string", "image", "", ""), "string_image"),
            (("string", "version", "", ""), "string_version"),
            (("string", "ip", "", ""), "string_ipaddress"),
            (("bool", "", "", ""), "bool"),
            (("integer", "", "", ""), "integer"),
            (("number", "", "", ""), "number"),
            (("array", "table", "array", ""), "complex_table"),
            (("array", "", "array", ""), "complex"),
            (("array", "", "integer", ""), "list_integer"),
            (("array", "", "string", ""), "list_string"),
            (("array", "", "string", "tag"), "list_string"),
            (("array", "version", "string", "version"), "list_string_version"),
            (("array", "date-time", "string", "date-time"), "list_string_datetime"),
            (("array", "subnet", "string", "subnet"), "list_string_subnet"),
            (("array", "discrete", "string", "logo"), "list_string"),
            (("array", "ip", "string", "ip"), "list_string_ipaddress"),
        )

    def _normtype(self, field):
        """Get the normalized type of a field."""
        ftype = field["type"]
        ffmt = field.get("format", "")
        fitype = field.get("items", {}).get("type", "")
        fifmt = field.get("items", {}).get("format", "")
        check = (ftype, ffmt, fitype, fifmt)

        for fmap in self._fmaps:
            if check == fmap[0]:
                return fmap[1]

        check = dict(zip(("type", "format", "items.type", "items.format"), check))
        fmsg = "Unmapped normalized type: {}: {}".format(field["name"], check)
        self._log.warning(fmsg)
        return "unknown"

    def is_complex(self, field):
        """Determine if a field is complex from its schema."""
        field_type = field["type"]
        field_items_type = field.get("items", {}).get("type")
        if field_type == "array" and field_items_type == "array":
            return True
        return False

    def is_root(self, name, names):
        """Determine if a field is a root field."""
        dots = name.split(".")
        return not (len(dots) > 1 and dots[0] in names)

    def _handle_complex(self, field):
        """Pass."""
        field["is_complex"] = self.is_complex(field=field)
        if field["is_complex"]:
            col_title = field["column_title"]
            col_name = field["column_name"]
            name_base = field["name_base"]
            prefix = field["adapter"]["prefix"]
            field["sub_fields"] = sub_fields = {}
            items = field.pop("items")["items"]

            field_names = [f["name"] for f in items]

            for sub_field in items:
                sub_title = sub_field["title"]
                sub_name = sub_field["name"]
                sub_name_base = "{}.{}".format(name_base, sub_name)
                sub_name_qual = "{}.{}".format(prefix, sub_name_base)

                sub_field["name_base"] = sub_name_base
                sub_field["name_qual"] = sub_name_qual
                sub_field["is_root"] = self.is_root(name=sub_name, names=field_names)
                sub_field["is_list"] = sub_field["type"] == "array"
                sub_field["adapter"] = field["adapter"]
                sub_field["column_title"] = "{}: {}".format(col_title, sub_title)
                sub_field["column_name"] = "{}.{}".format(col_name, sub_name)
                sub_field["type_norm"] = self._normtype(field=sub_field)
                self._handle_complex(field=sub_field)
                self._add(key=sub_field["name"], value=sub_field, dest=sub_fields)

    def _fields(self, name, prefix, prefix_parse, title, raw_fields):
        """Parse fields."""
        fields = {}

        adapter = {
            "prefix": prefix,
            "title": title,
            "prefix_parse": prefix_parse,
            "name": name,
        }

        fields["all"] = {
            "name": name,
            "name_qual": name,
            "name_base": name,
            "title": "All Adapter Specific Data",
            "type": "array",
            "type_norm": "complex_complex",
            "adapter": adapter,
            "is_complex": True,
            "is_root": False,
            "is_list": True,
            "column_title": "All Adapter Specific Data".format(title),
            "column_name": "{}:all".format(prefix_parse),
        }

        field_names = [
            tools.strip_left(obj=f["name"], fix=prefix).strip(".") for f in raw_fields
        ]

        for field in raw_fields:
            name_base = tools.strip_left(obj=field["name"], fix=prefix).strip(".")
            field["name_base"] = name_base
            field["name_qual"] = field["name"]
            field["is_root"] = self.is_root(name=name_base, names=field_names)
            field["is_list"] = field["type"] == "array"
            field["adapter"] = adapter
            field["column_title"] = "{}: {}".format(title, field["title"])
            field["column_name"] = "{}:{}".format(prefix_parse, name_base)
            field["type_norm"] = self._normtype(field=field)
            self._handle_complex(field=field)
            self._add(key=name_base, value=field, dest=fields)

        return fields

    def parse(self):
        """Parse all generic and adapter specific fields.

        Returns:
            :obj:`dict`: parsed generic and adapter specific fields
        """
        parsed = {}
        parsed["aggregated"] = self._fields(
            name="specific_data",
            prefix="specific_data.data",
            prefix_parse="agg",
            title="Aggregated",
            raw_fields=self._raw["generic"],
        )

        for name, raw_fields in self._raw["specific"].items():
            # name = aws_adapter
            prefix = "adapters_data.{}".format(name)
            # prefix = adapters_data.aws_adapter
            prefix_parse = tools.strip_right(obj=name, fix="_adapter")
            # prefix_parse = aws
            title = " ".join(prefix_parse.split("_")).title()
            # title = "Aws"
            fields = self._fields(
                name=name,
                prefix=prefix,
                prefix_parse=prefix_parse,
                title=title,
                raw_fields=raw_fields,
            )
            self._add(key=prefix_parse, value=fields, dest=parsed)

        return parsed
