"""Test meta data."""
import time

QUERIES = {
    "not_last_seen_day": '(not ("specific_data.data.last_seen" >= date("NOW - 1d")))',
    "exist_complex": '((("{f}" == ({{"$exists":true,"$ne":[]}})) and "{f}" != []))',
    "exist_simple": '(("{f}" == ({{"$exists":true,"$ne":""}})))',
}

TEST_CLIENT_CERT_NAME = "client_cert.crt"
TEST_CLIENT_CERT = """
-----BEGIN CERTIFICATE-----
MIIEtDCCApygAwIBAgIJAPuK1/Z7X2zbMA0GCSqGSIb3DQEBDQUAMFgxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMRkwFwYDVQQKDBBBeG9uaXVzIENJ
IFRlc3RzMRkwFwYDVQQDDBBBeG9uaXVzQ0lUZXN0c0NBMB4XDTE5MTIyNDEzMTYx
NFoXDTM5MDIyMjEzMTYxNFowgYsxCzAJBgNVBAYTAklMMREwDwYDVQQIDAhUZWwg
QXZpdjEKMAgGA1UEBwwBLjEKMAgGA1UEEQwBLjEQMA4GA1UECgwHQXhvbml1czEM
MAoGA1UECwwDUiZEMQwwCgYDVQQDDANCb2IxIzAhBgkqhkiG9w0BCQEWFGJvYkBh
eG9uaXVzdGVzdHMubGFuMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
t/p+x2hlsidVdoDkEnAV7S0t4DTQE4Iir8VGm/Rjb9Gv+O3T/VWPGYYm2roiSS0q
0DCNOSy8qx28+vccgdPdyflCte9/mas6dTRvXDM3nDLloqI9lQy8Tf1X3rhRDs8a
EZCmfiATUETPr7vp3+LjriHpSnc/siaUFdDxEWRIbAIR3zNDv7MJD7k16HQCK+5k
iCtJJXcelYC856vEASORJibUU/Q15KqgegM/ATf6NLem5fYO2dZhQMSj8nW8Cw2Q
pAo+uUdeDMLscREEG933zH0qDCNaGyjAY7JUqlHXEBtL2GSADNp2WGLyK4xMdTiB
HqGi05DvFKRXnBvs1YOdnQIDAQABo00wSzAxBgNVHSUEKjAoBggrBgEFBQcDAQYI
KwYBBQUHAwIGCCsGAQUFBwMDBggrBgEFBQcDBDAJBgNVHRMEAjAAMAsGA1UdDwQE
AwIF4DANBgkqhkiG9w0BAQ0FAAOCAgEAlyog4NTiu4jvEOisGtm4fWupNBaEC25B
c9+hntj2454NG3i3s5hkB65A6tFEoWWNSI74CEw/VKzecjqOzAuW4d5qYxA/jtX4
50Ws0fqzPxKvJTnhzzgOAHpiyxWrJASlp3fhK73Z2aRY6xNr8RoAXsQabj5wU3gm
kNzUZel5VVcB0Entmjcp2COqIvIm81Wumz+URE732hoC5ZnRDBAlu8zrMqptHU+4
WBgGBoQUMI3AJcE2UmZlCofsXni+jdr8ZN1j/xbu79W7xCHcQzm3//teWy2KAXp/
JfFfJ6tkO63hVGV9xGlIC0DK6Z17qy1uEwNKfu2qFvl6msCNT8AeyM5DJwEX//3S
ITxeZCPzznQx38Hth/ZOuCx5C8FT+mLv8Eoac+bC45HOckCK3wACYIPUCzwSDzxn
2AWBWP9ltF5/wJu854s23ylJ0Wu2NJArq5vuuA8SSf2Hb4f3Q4J6097iAQ0zunYK
t06o6EU8iDGxCZ+0Ev1Ocx/6d6wU1W/TBrN1veDQxsd5SQpNc0Q18m5YCcq1yDyt
DvpaMDAyxvLZtDAfPOd/KgpWUThIcdhAmT+tzde8bTrT306PPzbi5pIgaCsNGBb8
w4gw3wK/xMly7xZxoLD3YujN/sCcOFY3nhkB+L71GRlX8qYV5uS9fdbTKGZD7SYs
Ck4QKLYy+P0=
-----END CERTIFICATE-----
"""

TEST_CLIENT_KEY_NAME = "client_cert.key"
TEST_CLIENT_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAt/p+x2hlsidVdoDkEnAV7S0t4DTQE4Iir8VGm/Rjb9Gv+O3T
/VWPGYYm2roiSS0q0DCNOSy8qx28+vccgdPdyflCte9/mas6dTRvXDM3nDLloqI9
lQy8Tf1X3rhRDs8aEZCmfiATUETPr7vp3+LjriHpSnc/siaUFdDxEWRIbAIR3zND
v7MJD7k16HQCK+5kiCtJJXcelYC856vEASORJibUU/Q15KqgegM/ATf6NLem5fYO
2dZhQMSj8nW8Cw2QpAo+uUdeDMLscREEG933zH0qDCNaGyjAY7JUqlHXEBtL2GSA
DNp2WGLyK4xMdTiBHqGi05DvFKRXnBvs1YOdnQIDAQABAoIBAGOGeiDrg+AtURlL
PpYO1n24rBGW4F09UABgKwNg4I30FEsIdV6dc00uekRm3vdRHNEFAtDEN8glzT7C
gURmVZvWYNVFG3UI4RXYaMmq11GDYyBovgGsow1ZmLheY1MsjACmjLq8JVaN8wAx
GqLH/b0MkUR8YBPCtOdcYZyz8E2kohvw2P8DBmzUCFXuELHRh5eJ4nRv9ZdF8jw2
YOYnnBFrWJzE9YA+UCi67oGpMumcu91+tsenc3tvxXJX/HCSBiCc3GEHSROw0SjQ
TKLLPC+pT5wfmHGFeBPvKFpcfncx50IiTAcnHuBTQJvUvoNkiViBhS5ZG8Pranlq
w+fBlyECgYEA3wqTnkZFWR6Rl1cSUZRIAeKga380lNcnydhLbmBhiFxr7KoGiuyZ
cBcGqock0/sng6AwEl9d59ni3I5/2p4DtJmYxx8QU2XmUXSKdGH34qIXL6T27ow0
292vYIUFAT4vyawkKtO7FlKc+p5frL+dzIDcNOJPj0wfMivRDd33dokCgYEA0yo2
X9hLqNoq5X+UUVfhlgAswb7wDelx19up3QWX12eRMnwztTp070L/aoMpJaQuXUTC
HwF4Muffe8XsHMM+n9Jb8SToacspXwF0QrciVVowfdN/tyyP9ZVYzM9jSTm7K0NA
upfUccDxhgSNv6zNQNKix2qoNIQQuq4OxQpaqXUCgYEAxzmgT/D+wrL+YwtAbqQf
iaePmVV/dy+T98R+5DGtDOtY74WT4IWkLK40ox+h8sNVMUplhhOvQoiqDk4uv+0C
7E+CWuJRZ90OVFXf0kMr80DLqyAT/VI5aObkXzeSF+EfOGnNyH9ljnPuiiHq3dgu
sFut1oMLg7j/6IWg710ETNkCgYEAz/PWMHU1rUeMzw3g5mqBQdNSQErk5Q5sioNM
uNj1O7BGkU03LtYuqiF0n1QjhWo2Lquz8Azmblti/uVfLMQqPAJRgR0ztFvaljE8
aScorJ1w+7j5IU7FRriZBrmFsWslI+nLKPa0xIGaWLzLS2PFjnzgyToEBBO61dzr
tqgHuLECgYBA5nJsbMc36x55d61/4XLkX4Pmoh/LtTEZt9LyoWXUOq86vZuP1W/u
fcCY7mv+lRAoiAC1Z38YjGgJmZINH9EoaVnZJNeaO/86qemnlwYQ5/DIViycPZWI
oXO3sikOr2yrDS95jHjVzU0iW3xzu8bM9D01swBx0T5kYKWZo4ywpQ==
-----END RSA PRIVATE KEY-----
"""

FIELD_FORMATS = [
    "discrete",
    "connection_label",
    "date-time",
    "image",
    "ip",
    "logo",
    "ip_preferred",
    "os-distribution",
    "password",
    "subnet",
    "table",
    "tag",
    "time",
    "version",
    "dynamic_field",  # ~3.13
    "date",  # 4.5
    "sq",
    "expirable-tag",  # 4.6
    "data_scope",
]
SCHEMA_FIELD_FORMATS = FIELD_FORMATS
SCHEMA_TYPES = ["string", "bool", "array", "integer", "number", "file"]
TAGS = ["badwolf_tag_1", "badwolf_tag_2"]

LINUX_QUERY = 'specific_data.data.os.type == "Linux"'
SHELL_ACTION_NAME = "Badwolf Shell Action"
SHELL_ACTION_CMD = "echo 'Badwolf' > /tmp/badwolf.txt"
DEPLOY_ACTION_NAME = "Badwolf Deploy Action"
DEPLOY_FILE_NAME = "badwolf.sh"
DEPLOY_FILE_CONTENTS = b"#!/bin/bash\necho badwolf!"

CREATE_EC_NAME = "Badwolf EC Example"
CREATE_EC_TRIGGER1 = {
    "name": "Trigger",
    "conditions": {
        "new_entities": False,
        "previous_entities": False,
        "above": 1,
        "below": 0,
    },
    "period": "never",
    "run_on": "AllEntities",
}

CREATE_EC_ACTION_MAIN = {
    "name": "Badwolf Create Notification {}".format(time.time()),
    "action": {"action_name": "create_notification", "config": {}},
}


CSV_FILENAME = "badwolf.csv"
CSV_FIELDS = ["mac_address", "field1"]
CSV_ROW = ["01:37:53:9E:82:7C", "e"]
CSV_FILECONTENTS = [",".join(CSV_FIELDS), ",".join(CSV_ROW)]
CSV_FILECONTENT_STR = "\r\n".join(CSV_FILECONTENTS) + "\r\n"
CSV_FILECONTENT_BYTES = CSV_FILECONTENT_STR.encode()

NORM_TYPES = [
    "string",
    "string_datetime",
    "string_image",
    "string_version",
    "string_ipaddress",
    "bool",
    "integer",
    "number",
    "complex_table",
    "complex",
    "list_integer",
    "list_string",
    "list_string",
    "list_string_version",
    "list_string_datetime",
    "list_string_subnet",
    "list_string",
    "list_string_ipaddress",
    "complex_complex",
]
SCHEMA_STR = {"name": "schema_str", "type": "string", "required": False}
SCHEMA_STR_PASSWORD = {
    "name": "schema_str_password",
    "type": "string",
    "format": "password",
    "required": False,
}
SCHEMA_STR_ENUM = {
    "name": "schema_str_enum",
    "type": "string",
    "enum": ["badwolf"],
    "required": False,
}
SCHEMA_INT = {"name": "schema_int", "type": "integer", "required": False}
SCHEMA_NUM = {"name": "schema_num", "type": "number", "required": False}
SCHEMA_BOOL = {"name": "schema_bool", "type": "bool", "required": False}
SCHEMA_ARRAY = {"name": "schema_array", "type": "array", "required": False}
SCHEMA_FILE = {"name": "schema_file", "type": "file", "required": False}
SCHEMA_UNKNOWN = {"name": "schema_unknown", "type": "badwolf", "required": False}
SCHEMAS = [
    SCHEMA_STR,
    SCHEMA_STR_PASSWORD,
    SCHEMA_STR_ENUM,
    SCHEMA_INT,
    SCHEMA_NUM,
    SCHEMA_BOOL,
    SCHEMA_ARRAY,
    SCHEMA_FILE,
]
SCHEMAS_DICT = {x["name"]: x for x in SCHEMAS}

TEST_USER = "badwolfy"
TEST_ROLE = "badwolfy"
TEST_PERM = "Restricted"
# ABOUT_KEYS = ["Build Date", "Version"]
# ABOUT_KEYS_EMPTY_OK = ["Version"]
# ABOUT on BUILD: ["Build Date", "Commit Date", "Commit Hash", "Version"]
# ABOUT on RELEASE: ["Build Date", "Customer ID", "Version"]
NO_TITLES = ["system_research_date", "system_research_weekdays"]

USER_NAME = "badwolf"
EMAIL = "jim@axonius.com"
EMAIL_ALT = "james@axonius.com"


class CsvKeys:
    """Pass."""

    user_id: str = "user_id"
    file_path: str = "file_path"
    verify_ssl: str = "verify_ssl"


class CsvData:
    """Pass."""

    from axonius_api_client.tools import csv_writer

    adapter_name: str = "csv"
    adapter_name_raw: str = "csv_adapter"
    file_field_name: str = "file_path"
    file_name: str = "badwolfzzzzzzzz.csv"
    user_id: str = "badwolfzzzzzzzz"
    rows = [
        {
            "name": "why",
            "mac_address": "01:37:53:9E:82:7C",
            "extra_field": "foo1",
        },
        {
            "name": "cuz",
            "mac_address": "01:37:53:9E:82:8C",
            "extra_field": "foo2",
        },
    ]
    file_contents: str = csv_writer(rows=rows)
    config: dict = {CsvKeys.user_id: user_id, CsvKeys.verify_ssl: False}


class TanKeys:
    """Pass."""

    domain: str = "domain"
    username: str = "username"
    password: str = "password"


class TanData:
    """Pass."""

    adapter_name: str = "tanium"
    adapter_name_raw: str = "tanium_adapter"
    bad_val: str = "dumdum"
    config_bad: dict = {
        TanKeys.domain: bad_val,
        TanKeys.username: bad_val,
        TanKeys.password: bad_val,
    }
