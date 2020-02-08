"""Metadata for user/device objects."""
from __future__ import absolute_import, division, print_function, unicode_literals

FIELD_FORMATS = ["discrete", "image", "date-time", "table", "ip", "subnet", "version"]
SCHEMA_FIELD_FORMATS = [
    "image",
    "date-time",
    "table",
    "logo",
    "tag",
    "ip",
    "subnet",
    "version",
]
FIELD_TYPES = ["string", "bool", "array", "integer", "number"]

QUERY_ID = '((internal_axon_id == "{internal_axon_id}"))'.format
QUERY_EQ = '(({f} == "{v}"))'.format
QUERY_FIELD_EXISTS = '(({field} == ({{"$exists":true,"$ne": ""}})))'.format
"""
# multi
((internal_axon_id == ({"$exists":true,"$ne":""})))
    and
((specific_data.data.username == ({"$exists":true,"$ne":""})))
    and
((specific_data.data.mail == ({"$exists":true,"$ne":""})))

# single
((internal_axon_id == ({"$exists":true,"$ne":""})))

"""

USERS_TEST_DATA = {
    "adapters": [
        {"search": "generic", "exp": "generic"},
        {"search": "active_directory_adapter", "exp": "active_directory"},
        {"search": "active_directory", "exp": "active_directory"},
    ],
    "single_field": {"search": "username", "exp": "specific_data.data.username"},
    "fields": [
        {"search": "username", "exp": ["specific_data.data.username"]},
        {"search": "generic:username", "exp": ["specific_data.data.username"]},
        {"search": "mail", "exp": ["specific_data.data.mail"]},
        {"search": "generic:mail", "exp": ["specific_data.data.mail"]},
        {
            "search": "generic:mail,username",
            "exp": ["specific_data.data.mail", "specific_data.data.username"],
        },
        {
            "search": "active_directory:username",
            "exp": ["adapters_data.active_directory_adapter.username"],
        },
        {
            "search": "adapters_data.active_directory_adapter.username",
            "exp": ["adapters_data.active_directory_adapter.username"],
        },
        {
            "search": "*,*,username",
            "exp": ["specific_data", "specific_data.data.username"],
        },
    ],
    "val_fields": [
        {
            "search": ["active_directory:username", "generic:username", "mail"],
            "exp": [
                "adapters_data.active_directory_adapter.username",
                "specific_data.data.username",
                "specific_data.data.mail",
            ],
        }
    ],
}

DEVICES_TEST_DATA = {
    "adapters": [
        {"search": "generic", "exp": "generic"},
        {"search": "active_directory_adapter", "exp": "active_directory"},
        {"search": "active_directory", "exp": "active_directory"},
    ],
    "single_field": {"search": "hostname", "exp": "specific_data.data.hostname"},
    "fields": [
        {
            "search": "network_interfaces.ips",
            "exp": ["specific_data.data.network_interfaces.ips"],
        },
        {
            "search": "generic:network_interfaces.ips",
            "exp": ["specific_data.data.network_interfaces.ips"],
        },
        {"search": "hostname", "exp": ["specific_data.data.hostname"]},
        {"search": "generic:hostname", "exp": ["specific_data.data.hostname"]},
        {
            "search": "generic:hostname,network_interfaces.ips",
            "exp": [
                "specific_data.data.hostname",
                "specific_data.data.network_interfaces.ips",
            ],
        },
        {
            "search": "active_directory:hostname",
            "exp": ["adapters_data.active_directory_adapter.hostname"],
        },
        {
            "search": "adapters_data.active_directory_adapter.hostname",
            "exp": ["adapters_data.active_directory_adapter.hostname"],
        },
        {
            "search": "*,*,hostname",
            "exp": ["specific_data", "specific_data.data.hostname"],
        },
    ],
    "val_fields": [
        {
            "search": [
                "active_directory:hostname",
                "generic:hostname",
                "network_interfaces.ips",
            ],
            "exp": [
                "adapters_data.active_directory_adapter.hostname",
                "specific_data.data.hostname",
                "specific_data.data.network_interfaces.ips",
            ],
        }
    ],
}
