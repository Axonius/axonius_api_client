.. include:: /main/.special.rst

adapters get
###############################################

This command allows you to get metadata of adapters and their connections.

JSON data structure
==============================================

The JSON format returns a list of dictionaries.

Each dictionary represents an instance of an adapter on a node and has the keys:

* name: The human friendly name of the adapter
* name_raw: The name of the adapter as known by the API.
* name_plugin: The name of the adapter plugin as known by the API.
* node_name: The name of the node this adapter instance is running on.
* node_id: The ID of the node this adapter instance is running on.
* status: A boolean value reflecting the status of this adapter, one of:

  * None: has no connections
  * True: has connections all connections are working
  * False: has connections and one or more connections are broken

* status_raw: The text the API uses to represent the status of this adapter, one of:

  * "": has no connections
  * "success": has connections and all connections are working
  * "warning": has connections and one or more connections are broken

* cnx_count: The count of all connections for this adapter.
* cnx_ok: The count of all working connections for this adapter.
* cnx_bad: The count of all broken connections for this adapter.
* cnx: A list of dictionaries for all connections of this adapter (TODO cnx ref for cnx metadata)
* cnx_ok: A list of dictionaries for all working connections of this adapter (TODO cnx ref for cnx metadata)
* cnx_bad: A list of dictionaries for all broken connections of this adapter (TODO cnx ref for cnx metadata)
* cnx_settings: A dictionary describing each of the settings that can be supplied when creating a new connection for this adapter.
* settings: A dictionary showing the metadata and values for each adapter specific setting, if the adapter has specific settings under Advanced Settings in the GUI.
* adv_settings: A dictionary showing the metadata and values for each setting in Advanced Settings in the GUI.

Output feeds
===============================================

The output from this command is able to be supplied as input to these commands:

* :doc:`../grp_cnx_cmds/cmd_check`
* :doc:`../grp_cnx_cmds/cmd_delete`
* :doc:`../grp_cnx_cmds/cmd_discover`
* :doc:`../grp_cnx_cmds/cmd_get`

Common Options
===============================================

* :ref:`connection_options`
* :ref:`export_options`

Examples
===============================================

No filters, json and csv exports
-----------------------------------------------

.. raw:: html

    <script id="asciicast-270350" src="https://asciinema.org/a/270350.js" async></script>

Filtering on adapter name and/or node name
-----------------------------------------------

.. raw:: html

   <script id="asciicast-270351" src="https://asciinema.org/a/270351.js" async></script>

Filtering on adapter status
-----------------------------------------------

.. raw:: html

    <script id="asciicast-270362" src="https://asciinema.org/a/270362.js" async></script>

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_adapters.cmd_get:cmd
   :prog: axonshell adapters get
