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

    def jdump(obj, **kwargs):
        """JSON dump utility."""
        print(axonapi.tools.json_reload(obj, **kwargs))

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
        log_request_attrs=["url", "method"],
        # log_response_attrs=["status", "size"],
        # log_request_body=True,
        # log_response_body=True,
        log_console=True,
    )

    ctx.start()
    devices = ctx.devices
    users = ctx.users
    adapters = ctx.adapters
    enforcements = ctx.enforcements
    system = ctx.system

    # schemas = devices.fields.get()
    # root_complex = [
    #     x["name_qual"] for x in schemas["agg"] if x["is_complex"] and x["is_root"]
    # ]
    '''
    z = devices.get(
        max_rows=1,
        # query="""(((specific_data.data.direct_connected_devices == ({"$exists":true,"$ne":[]})) and specific_data.data.direct_connected_devices != [])) and (((specific_data.data.connected_devices == ({"$exists":true,"$ne":[]})) and specific_data.data.connected_devices != [])) and (((specific_data.data.network_interfaces == ({"$exists":true,"$ne":[]})) and specific_data.data.network_interfaces != []))""",  # noqa
        # fields_manual=root_complex,
        fields=[
            "network_interfaces",
            "hostname_preferred",
            #     "open_ports",
            #     "connected_devices",
            #     "direct_connected_devices",
            #     # "installed_software.name",
            #     # "installed_software",
        ],
        fields_default=False,
        #
        # ---> echo/log first_page
        # first_page=True,  # for cli
        # ---> echo to stderr or log to debug
        do_echo=True,  # for cli
        # ---> field_null
        field_null=True,  # relies on field_null_value
        # field_null_value="MOOOOOOOO",
        # ---> field_excludes
        # field_excludes=[
        #     # "speed",
        #     # "installed_software",
        #     # "specific_data.data.hostname_preferred",
        #     "labels",
        #     # "internal_axon_id",
        #     "adapters",
        #     "adapter_list_length",
        #     # "installed_software.name",
        # ],
        # ---> field_flatten
        # field_flatten=True,
        # ---> field_explode
        field_explode="network_interfaces",
        # ---> report_adapters_missing
        # report_adapters_missing=True,
        # ---> field_join
        # field_join=True,  # depends on field_join_value and field_join_trim
        # field_join_value="!!!!!!",
        # field_join_trim=0,
        # field_titles=True,
        # ---> exporters
        export="json",  # csv, json; empty means no exporter
        # export_file="blah.json",  # empty means use stdout
        # export_path="moo",  # default CWD
        export_overwrite=True,  # default False
        # export_schema=True,  # add schema to csv/json
        # csv_dialect="excel",  # excel, excel-tab, unix
        # csv_quoting="nonnumeric",  # minimal, all, nonnumeric, none
        # table_max_rows=10,
        # table_format="fancy_grid",
    )
    '''


# def parse_schema(raw):
#     """Pass."""
#     parsed = {}
#     if raw:
#         schemas = raw["items"]
#         required = raw["required"]
#         for schema in schemas:
#             schema_name = schema["name"]
#             parsed[schema_name] = schema

#             # core settings: password_brute_force_protection: conditional
#             # has a list of dict enums, so turn it into a lookup map
#             if schema.get("enum"):
#                 if isinstance(schema["enum"][0], dict):
#                     schema["enum"] = {x["name"]: x for x in schema["enum"]}

#             # system settings have sub-schemas
#             if schema.get("items"):
#                 schema["sub_schemas"] = parse_schema(raw=schema)
#                 schema.pop("items")
#                 continue

#             schema["required"] = schema_name in required

#     return parsed


# def parse_settings(raw, pretty_name=""):
#     """Pass."""
#     pretty_name = raw["schema"].get("pretty_name", "") or pretty_name
#     sections = raw["schema"]["items"]

#     parsed = {}
#     parsed["titles"] = {"self": pretty_name}
#     parsed["sections"] = {}
#     parsed["config"] = raw["config"]

#     for section in sections:
#         section_name = section["name"]
#         section_title = section["title"]

#         parsed["titles"][section_name] = section_title
#         parsed["sections"][section_name] = parse_schema(raw=section)

#         # core settings: https_log_settings does not follow schema, so this:
#         if section_name in section:
#             for k, v in section[section_name].items():
#                 parsed["sections"][section_name][k]["default"] = v
#     return parsed


# # sub sub schemas, fml
# settings = system.settings_gui.get()
# parsed = parse_settings(settings)


def test(doc, method):
    """Pass."""

    def sub_test(arg1, **kwargs):
        doc
        return arg1, method

    sub_test.__doc__ = doc
    return sub_test
