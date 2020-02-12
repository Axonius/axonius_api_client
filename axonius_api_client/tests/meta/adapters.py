"""Metadata for adapters."""
from __future__ import absolute_import, division, print_function, unicode_literals

DEFAULT_NODE = "master"

CSV_FILENAME = "badwolf.csv"
CSV_FIELDS = ["mac_address", "field1"]
CSV_ROW = ["01:37:53:9E:82:7C", "e"]
CSV_FILECONTENTS = [",".join(CSV_FIELDS), ",".join(CSV_ROW)]
CSV_FILECONTENT_STR = "\r\n".join(CSV_FILECONTENTS) + "\r\n"
CSV_FILECONTENT_BYTES = CSV_FILECONTENT_STR.encode()

FAKE_CNX_OK = {
    "adapter_name": "fluff1",
    "adapter_name_raw": "fluff1_adapter",
    "id": "foobar1",
    "node_name": "xbxb",
    "node_id": "xbxb",
    "uuid": "abc123",
    "status": True,
}
FAKE_CNX_BAD = {
    "adapter_name": "fluff2",
    "adapter_name_raw": "fluff2_adapter",
    "node_name": "xbxb",
    "node_id": "xbxb",
    "id": "foobar2",
    "uuid": "zxy987",
    "status": False,
}
FAKE_CNXS = [FAKE_CNX_OK, FAKE_CNX_BAD]
FAKE_ADAPTER_CNXS_OK = {
    "cnx": [FAKE_CNX_OK],
    "name": "fluff1",
    "name_raw": "fluff1_adapter",
    "node_name": DEFAULT_NODE,
    "cnx_count": 1,
    "status": True,
}
FAKE_ADAPTER_CNXS_BAD = {
    "cnx": FAKE_CNXS,
    "name": "fluff2",
    "name_raw": "fluff2_adapter",
    "node_name": DEFAULT_NODE,
    "cnx_count": 2,
    "status": False,
}
FAKE_ADAPTER_NOCLIENTS = {
    "cnx": [],
    "name": "fluff3",
    "name_raw": "fluff3_adapter",
    "node_name": DEFAULT_NODE,
    "cnx_count": 0,
    "status": None,
}
FAKE_ADAPTERS = [FAKE_ADAPTER_CNXS_BAD, FAKE_ADAPTER_CNXS_OK, FAKE_ADAPTER_NOCLIENTS]
FAKE_FILE = "badwolf_fake.txt"
FAKE_FILE_CONTENTS = "id,hostname\nbadwolf9131,badwolf\n"
AD_CONFIG_SCHEMA_LIST = [
    ["dc_name", "badwolf_default"],
    ["user", CSV_FILENAME],
    ["password", CSV_FILENAME],
    ["do_not_fetch_users", False],
    ["fetch_disabled_devices", True],
    ["fetch_disabled_users", True],
    ["dns_server_address", "badwolf"],
    ["alternative_dns_suffix", "badwolf"],
    ["use_ssl", "Unencrypted"],
    ["ca_file", FAKE_FILE],
    ["is_ad_gc", "n"],
    ["ldap_ou_whitelist", "badwolf1,badwolf2"],
]
AD_CONFIG_SCHEMA = dict(AD_CONFIG_SCHEMA_LIST)
