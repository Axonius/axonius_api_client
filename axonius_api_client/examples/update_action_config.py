#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base example for setting up the API client."""
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
client_args["certwarn"] = False
# client_args["log_console"] = True
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


ACTION_TYPE: str = "create_top_desk_incident"
CONFIG_SEARCH: dict = {
    "operator_name": "John Doe",
    "operator_group": "BLAH/BLAH/BLAH",
}
CONFIG_UPDATE: dict = {
    "operator_name": "Jane Doe",
    "operator_group": "MOE/MOE/MOE",
}

# get all enforcement objects in the system
enforcements = client.enforcements.get()

for enforcement in enforcements:
    # if it's not the action type we care about, skip it
    if enforcement.main_action_type != ACTION_TYPE:
        continue

    # get the config of the main action
    config = enforcement.main_action["config"]

    # get the operator and operator_group values from the config of the main action
    current = {k: config.get(k) for k in CONFIG_SEARCH}

    # if the operator or operator group is bad, update it
    if sorted(current.items()) == sorted(CONFIG_SEARCH.items()):
        config.update(CONFIG_UPDATE)
        client.enforcements._update(
            uuid=enforcement.uuid,
            name=enforcement.name,
            actions=enforcement.actions,
            folder_id=enforcement.folder.id,
            triggers=enforcement.triggers,
        )
        print(f"Updated enforcement {enforcement.name!r} main action with {CONFIG_UPDATE}")
