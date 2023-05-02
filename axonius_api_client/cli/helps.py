# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..constants.wizards import Docs

HELPSTR_AUTH = """
Detailed help for authentication:

--url: URL of an Axonius instance

    This can be an IP address, a hostname, or a fully qualified url (and can
    optionally include the port as :port)

--key: API Key of user in an Axonius instance

    See https://axonius-api-client.readthedocs.io/en/latest/main/axtokens.html

--secret: API Secret of user in an Axonius instance

    See https://axonius-api-client.readthedocs.io/en/latest/main/axtokens.html
"""


HELPSTR_EXPORT_ASSET = """
Detailed help for exporting assets:

--export-file:

    File to send data to

    If not supplied data will go to STDOUT, which can be redirected using
    standard OS redirection

    If supplied as a non-absolute path, it will be created as relative
    to --export-path

    If the file does not exist, it will get created with read/write permissions
    for the current user only

--export-path:

    Directory to write --export-file to

    If the directory does not exist, it will get created with read/write
    permissions for the current user only

    The default is the current working directory

--export-table-format:

    Table format to use for export-format=table

    For --export-format=json or csv: ignored

--export-table-max-rows:

    Only return this many rows for export-format=table

    The table format is not very useful for returning large datasets, so we limit
    this to a very low number by default

    For --export-format=json or csv: ignored

--export-include-schema/--no-export-include-schema:

    Add schema information to the export

    For --export-format=json: Add a row at the end of the list of assets with
    the full schema of all fields returned for each asset

    For --export-format=csv: Add 2 rows below the header row with the internal
    field name and the normalized value type

    For --export-format=table: ignored

--export-use-titles/--no-export-use-titles:

    Rename fields from internal field names to their column titles

    For --export-format=json: Rename the keys for each row from the internal
    field name to the field title

    For --export-format=csv or table: Use the field titles as headers
    instead of the internal field name (built-in behavior, can not turn off)

--export-join/--no-export-join:

    Join multivalue fields using --export-join-value

    For --export-format=csv or table: built-in behavior, can not turn off

--export-join-trim:

    Character length to trim joined multivalue fields

    When --export-join=True: if joined value is over this many characters,
    trim it and add a string showing why it was trimmed

    The default is just below the maximum cell character length of Excel (32767)

    If 0 is supplied, no trimming will be applied

--export-explode:

    Flatten and explode a fields values into multiple rows

    This will create new rows for each item in the supplied fields value
    with all other fields duplicated in each new row

    Missing complex sub-fields will be added with a value set to
    --field-null-value.

    This must be a field that has been supplied to --field and the
    field name can be:

    - a fully qualified field name: specific_data.data.installed_software

    - a short field name: installed_software

--export-flatten/--no-export-flatten:

    Remove complex fields and re-add their sub-field values to the row

    For example, open_ports has 3 sub-fields: port_id, protocol, service_name

    Flattening open_ports would remove it from each asset, and add
    open_ports.port_id, open_ports.protocol, and open_ports.service_name
    with their values

    Sub-fields that are not returned will be set using --export-null-value

--export-field-exclude:

    Fields to exclude from each row

    Supply multiple --export-field-exclude for each value

    This must be a field that has been supplied to --field and the field
    name can be any one of:

    - fully qualified field name: specific_data.data.installed_software

    - short field name: installed_software

    - fully qualified sub-field name: specific_data.data.installed_software.name

    - short sub-field name: installed_software.name

    - sub-field name: name
"""

HELPSTR_QUERY = """
Detailed help for supplying a query:

--query:
    Query built from the Query wizard in the GUI

    All assets are returned if this is not supplied

--query-file:
    Path to a file to override --query

    Path to a file containing a query built from the Query wizard in the GUI.
    Overrides --query if both are supplied

    This can be used to avoid dealing with quote escaping issues in varying
    command lines

    Supply '-' to read the file from STDIN.

"""

HELPSTR_SELECT_FIELDS = """
Detailed help for selecting fields:

--fields:
    Fields to include in the format of adapter:field

    Can supply multiple --field values.

    Examples:

    - hostname - get the aggregated hostname field
      (same as: generic:hostname, aggregated:hostname, specific_data.data.hostname)

    - aws:hostname - get the AWS adapter specific hostname field
      (same as adapters_data.aws_adapter)

    - hostname,network_interfaces - get the aggregated hostname and
      network_interfaces fields
"""

HELPSTR_MULTI_CNX_JSON = """
Example JSON input file:

[
    {
        "adapter_name": "ADAPTER_NAME",
        "config": {"domain": "HOSTNAME", "username": "USERNAME", "password": "PASSWORD"},
    },
    {
        "adapter_name": "ADAPTER_NAME",
        "node_name": "NODE_NAME",
        "config": {"domain": "HOSTNAME", "username": "USERNAME", "password": "PASSWORD"},
        "active": "n",
        "save_and_fetch": "n"
    }
]

Tips:
 - use "axonshell adapters cnx get --name ADAPTER_NAME --export-format table-schemas" to see the
   values that can be supplied for the "config" dictionary.
 - the first connection only supplies the required keys, and it will be added to the
   "Core instance" (usually "Master").
 - the second connection supplies everything, and does not fetch the connection after adding it
   and sets the connection as inactive
 - The schema format for this file was changed slightly in 4.20
    - adapter key now needs to be 'adapter_name'
    - node key now needs to be 'node_name'
"""


def asset_helper(**kwargs) -> str:
    """Return the help string for the asset helpers"""
    from ..constants.asset_helpers import ASSETS_HELPERS

    return ASSETS_HELPERS.to_str()


HELPSTRS = {
    "auth": HELPSTR_AUTH,
    "assetexport": HELPSTR_EXPORT_ASSET,
    "selectfields": HELPSTR_SELECT_FIELDS,
    "query": HELPSTR_QUERY,
    "wizard": Docs.TEXT,
    "wizard_csv": Docs.CSV,
    "multiple_cnx_json": HELPSTR_MULTI_CNX_JSON,
    "asset_helper": asset_helper,
}
