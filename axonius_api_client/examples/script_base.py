#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import os

import axonius_api_client as axonapi

if __name__ == "__main__":
    axonapi.constants.load_dotenv()

    AX_URL = os.environ["AX_URL"]
    AX_KEY = os.environ["AX_KEY"]
    AX_SECRET = os.environ["AX_SECRET"]
    AX_CLIENT_CERT_BOTH = os.environ.get("AX_CLIENT_CERT_BOTH", None) or None
    AX_CLIENT_CERT_CERT = os.environ.get("AX_CLIENT_CERT_CERT", None) or None
    AX_CLIENT_CERT_KEY = os.environ.get("AX_CLIENT_CERT_KEY", None) or None
    jreload = axonapi.tools.json_reload

    def jdump(obj, **kwargs):
        """JSON dump utility."""
        print(jreload(obj, **kwargs))

    ctx = axonapi.Connect(
        url=AX_URL,
        key=AX_KEY,
        secret=AX_SECRET,
        certwarn=False,
        cert_client_both=AX_CLIENT_CERT_BOTH,
        cert_client_cert=AX_CLIENT_CERT_CERT,
        cert_client_key=AX_CLIENT_CERT_KEY,
        log_level_console="debug",
        log_level_api="debug",
        log_level_http="debug",
        # log_request_attrs=["url", "size", "method"],
        # log_response_attrs=["status", "size"],
        # log_request_body=True,
        # log_response_body=True,
        # log_console=True,
    )

    ctx.start()
    devices = ctx.devices
    users = ctx.users
    adapters = ctx.adapters
    enforcements = ctx.enforcements
    system = ctx.system
    j = jdump

    def handle_str(field):
        field_fmt = field.get("format", "")
        field_items = field.get("items", {})
        field_subs = field.get("sub_fields") or []

        if not field_fmt and not field_items:
            return

        if field_fmt in ["ip", "date-time", "version"]:
            assert not field_items, field_items
            assert not field_subs, field_subs
            return

        raise Exception(f"Unhandled string {jreload(field)}")

    def handle_bool(field):
        field_fmt = field.get("format", "")
        field_items = field.get("items", {})
        field_subs = field.get("sub_fields") or []
        assert not field_fmt, field_fmt
        assert not field_subs, field_subs
        assert not field_items, field_items
        return
        raise Exception(f"Unhandled bool {jreload(field)}")

    def handle_int(field):
        field_fmt = field.get("format", "")
        field_items = field.get("items", {})
        field_subs = field.get("sub_fields") or []
        assert not field_fmt, field_fmt
        assert not field_subs, field_subs
        assert not field_items, field_items
        return

    def handle_num(field):
        field_fmt = field.get("format", "")
        field_items = field.get("items", {})
        field_subs = field.get("sub_fields") or []
        assert not field_fmt, field_fmt
        assert not field_subs, field_subs
        assert not field_items, field_items
        return

    def handle_arr(field):
        field_fmt = field.get("format", "")
        field_items = field.get("items", {})
        field_subs = field.get("sub_fields") or []
        field_items.pop("dynamic", False)
        field_items.pop("source", {})

        if field["name"] == "all":
            return

        if field_fmt == "discrete":
            assert not field_subs, field_subs

            items_format = field_items.pop("format")
            items_enum = field_items.pop("enum")
            items_type = field_items.pop("type")
            assert not field_items, field_items
            assert items_format == "logo", items_format
            assert not items_enum, items_enum
            assert items_type == "string", items_type
            return

        if field_fmt == "ip":
            assert not field_subs, field_subs

            items_format = field_items.pop("format")
            items_type = field_items.pop("type")
            assert not field_items, field_items
            assert items_format == "ip", items_format
            assert items_type == "string", items_type
            return

        # complex!
        if field["is_complex"]:
            assert field_subs, field_subs

            assert not field_items, field_items

            field["sub_fields"] = [
                y for y in [handle(x) for x in field.get("sub_fields") or []] if y
            ]
            return

        if field_fmt == "subnet":
            assert not field_subs, field_subs
            items_format = field_items.pop("format")
            items_type = field_items.pop("type")
            assert not field_items, field_items
            assert items_format == "subnet", items_format
            assert items_type == "string", items_type
            return

        if field_items:
            assert not field_subs, field_subs
            items_type = field_items.pop("type")
            items_enum = field_items.pop("enum", [])
            items_fmt = field_items.pop("format", "")
            if items_type == "string":
                assert items_fmt in ["tag", "", "version", "date-time"], items_fmt
                assert not field_items, field_items
                # can have enum sometimes
                return

            if items_type == "integer":
                assert not items_fmt, items_fmt
                assert not items_enum, items_enum
                assert not field_items, field_items
                return

            raise Exception(f"Unhandled array items type {items_type} {jreload(field)}")

        raise Exception(f"Unhandled array {jreload(field)}")

    def handle(field):
        field_type = field.get("type", "")
        if not field["selectable"]:
            return

        try:
            if field_type == "string":
                return handle_str(field)
            if field_type == "array":
                return handle_arr(field)
            if field_type == "number":
                return handle_num(field)
            if field_type == "integer":
                return handle_int(field)
            if field_type == "bool":
                return handle_bool(field)
        except AssertionError as exc:
            raise Exception(f"assertion failed {exc} in field {jreload(field)}")

        raise Exception(f"Unhandled base type {field_type}")

    fields = devices.fields.get()

    for adapter in fields:
        fields[adapter] = [y for y in [handle(x) for x in fields[adapter]] if y]
