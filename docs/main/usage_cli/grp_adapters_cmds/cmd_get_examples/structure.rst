.. include:: /main/.special.rst

JSON data structure
###############################################

The JSON format returns a list of dictionaries.

Each dictionary represents an instance of an adapter on a node and has the keys:

* name: The human friendly name of the adapter.
* name_raw: The name of the adapter as known by the REST API.
* name_plugin: The name of the adapter plugin as known by the REST API.
* node_name: The name of the node this adapter instance is running on.
* node_id: The ID of the node this adapter instance is running on.
* status: A boolean value reflecting the status of this adapter, one of:

  * None: has no connections
  * True: has connections and all connections are working
  * False: has connections and one or more connections are broken

* status_raw: The text the REST API uses to represent the status of this adapter, one of:

  * "": has no connections
  * "success": has connections and all connections are working
  * "warning": has connections and one or more connections are broken

* cnx_count: The count of all connections for this adapter.
* cnx_ok: The count of all working connections for this adapter.
* cnx_bad: The count of all broken connections for this adapter.
* cnx: A list of dictionaries for all connections of this adapter. (TODO cnx ref for cnx metadata)
* cnx_ok: A list of dictionaries for all working connections of this adapter. (TODO cnx ref for cnx metadata)
* cnx_bad: A list of dictionaries for all broken connections of this adapter. (TODO cnx ref for cnx metadata)
* cnx_settings: A dictionary describing each of the settings that can be supplied when creating a new connection for this adapter.
* settings: A dictionary showing the metadata and values for each adapter specific setting, if the adapter has specific settings under Advanced Settings in the GUI.
* adv_settings: A dictionary showing the metadata and values for each setting in Advanced Settings in the GUI.
