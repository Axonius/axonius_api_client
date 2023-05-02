#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base example for setting up the API client."""
import axonius_api_client as axonapi

# get the URL, API key, API secret, & certwarn from the default ".env" file
client_args = axonapi.get_env_connect()

# OR override OS env vars with the values from a custom .env file
# client_args = axonapi.get_env_connect(ax_env="/path/to/envfile", override=True)

# create a client using the url, key, and secret from OS env
client = axonapi.Connect(log_console=True, **client_args)

j = client.jdump  # json dump helper

client.start()  # connect to axonius
devices = client.devices  # work with device assets
users = client.users  # work with user assets
adapters = client.adapters  # work with adapters and adapter connections
enforcements = client.enforcements  # work with enforcements
instances = client.instances  # work with instances
dashboard = client.dashboard  # work with dashboards and discovery cycles
system_users = client.system_users  # work with system users
system_roles = client.system_roles  # work with system roles
meta = client.meta  # work with instance metadata
settings_global = client.settings_global  # work with core system settings
settings_gui = client.settings_gui  # work with gui system settings
settings_lifecycle = client.settings_lifecycle  # work with lifecycle system settings
