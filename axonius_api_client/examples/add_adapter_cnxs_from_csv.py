#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base example for setting up the API client."""
import copy  # noqa
import csv
import sys
from typing import List

import click

import axonius_api_client as axonapi

# client.activity_logs          # get audit logs
# client.adapters               # get adapters and update adapter settings
# client.adapters.cnx           # CRUD for adapter connections
# client.dashboard              # get/start/stop discovery cycles
# client.devices                # get device assets
# client.devices.fields         # get field schemas for device assets
# client.devices.labels         # add/remove/get tags for device assets
# client.devices.saved_queries  # CRUD for saved queries for device assets
# client.enforcements           # CRUD for enforcements
# client.instances              # get instances and instance meta data
# client.meta                   # get product meta data
# client.remote_support         # enable/disable remote support settings
# client.settings_global        # get/update global system settings
# client.settings_gui           # get/update gui system settings
# client.settings_ip            # get/update identity provider system settings
# client.settings_lifecycle     # get/update lifecycle system settings
# client.signup                 # perform initial signup and use password reset tokens
# client.system_roles           # CRUD for system roles
# client.system_users           # CRUD for system users
# client.users                  # get user assets
# client.users.fields           # get field schemas for user assets
# client.users.labels           # add/remove/get tags for user assets
# client.users.saved_queries    # CRUD for saved queries for user assets
# client.openapi                # get the OpenAPI specification file

client_args = {}

# --- get the URL, API key, API secret, & certwarn from the default ".env" file
client_args.update(axonapi.get_env_connect())

# --- OR override OS env vars with the values from a custom .env file
# client_args.update(axonapi.get_env_connect(ax_env="/path/to/envfile", override=True))

# --- OR supply them here in the script
# client_args["url"] = "10.20.0.94"
# client_args["key"] = ""
# client_args["secret"] = ""

# --- Enable logging
# client_args["log_console"] = True  # enable logging to console
# client_args["log_request_attrs"] = "all"  # log all request attributes
# client_args["log_request_body"] = True  # log all request bodies
# client_args["log_response_attrs"] = "all"  # log all response attributes
# client_args["log_response_body"] = True  # log all response bodies

# create a client using the url, key, and secret from OS env
client = axonapi.Connect(**client_args)

j = client.jdump  # json dump helper

client.start()  # connect to axonius


def load_csv(path: str) -> (List, List):
    """Load a CSV and return the configs and rows."""
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file)
        configs = [x.strip() for x in next(csv_reader, [])]
        rows = []
        for row in csv_reader:
            if len(row) == 0:
                continue
            rows.append(row)
        return configs, rows


def get_adapter_schema(adapter_name: str) -> (dict, dict):
    """Get the available schema map for an adapter."""
    adapter = client.adapters.get_by_name(name=adapter_name)
    cnxs = client.adapters.cnx._get(adapter_name=adapter["name_raw"])
    return cnxs.meta.get("schema").get("items"), cnxs.schema_cnx


def print_adapter_schema(schema: dict):
    """Get the adapter schema in string form and print it."""
    j(schema)
    sys.exit(0)


def check_schema(schema: dict, configs: List, ignore_unknown_keys: bool = False) -> List:
    """Checks that the configs from the CSV match what is needed to add a connection."""
    schema_keys = schema.keys()
    required_keys = [v.get("name") for k, v in schema.items() if v.get("required")]
    for key in required_keys:
        if key not in configs:
            raise KeyError(f"Required key `{key}` is missing from CSV configs.")
    for i, key in enumerate(configs):
        if key not in schema_keys:
            message = f"Unknown key `{key}` found in CSV configs."
            if not ignore_unknown_keys:
                raise KeyError(message)
            print(message + " Ignoring...", file=sys.stderr, end="\n\n")
            configs[i] = None
    return configs


def add_adapter_connection(
    adapter: str,
    configs: List,
    row: List,
    active: bool = False,
    save_and_fetch: bool = False,
) -> None:
    """Add an adapter using the adapter str and config."""
    config = {}
    for i, value in enumerate(row):
        if not value:
            continue
        config[configs[i]] = value
    try:
        cnx = client.adapters.cnx.add(
            adapter_name=adapter, active=active, save_and_fetch=save_and_fetch, **config
        )
    except axonapi.exceptions.CnxAddError as err:
        print(err, file=sys.stderr, end="\n\n")


class PathNotProvided(Exception):
    """Exception thrown when a CSV file path was not provided."""

    def __init__(self, message="A path to a CSV file must be provided with `--path`."):
        self.message = message
        super().__init__(self.message)


@click.command()
@click.option("--adapter", required=True, help="Adapter you want to add connections to.")
@click.option("--path", type=click.Path(exists=True), help="Path to the CSV file to open.")
@click.option("--show-schemas", is_flag=True, help="Show the adapter's schema and exit.")
@click.option(
    "--active",
    is_flag=True,
    default=False,
    help="Set the newly added adapter connections active.",
)
@click.option(
    "--ignore-unknown-keys",
    is_flag=True,
    default=False,
    help="Ignore config keys not in the adapter's schema.",
)
@click.option(
    "--save-and-fetch",
    is_flag=True,
    default=False,
    help="Immediately start a fetch for the newly added adapter.",
)
def main(
    adapter: str,
    path: str,
    show_schemas: bool,
    active: bool,
    ignore_unknown_keys: bool,
    save_and_fetch: bool,
) -> None:
    """Simple script that reads rows from a CSV and adds connections to the specified adapter."""
    # check adapter and load schema
    schema, schema_by_name = get_adapter_schema(adapter_name=adapter)
    if show_schemas:
        print_adapter_schema(schema=schema_by_name)

    if not path:
        raise PathNotProvided

    # load the csv pulling the config params from the header row
    configs, rows = load_csv(path=path)

    # check the configs to make sure it's inline with the schema
    configs = check_schema(
        schema=schema_by_name, configs=configs, ignore_unknown_keys=ignore_unknown_keys
    )

    # for each row
    for row in rows:
        # add a connection
        add_adapter_connection(adapter, configs, row, active=active, save_and_fetch=save_and_fetch)


if __name__ == "__main__":
    main()
