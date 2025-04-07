.. include:: /main/.special.rst

.. _adapter_structure:

Adapter Metadata JSON-FULL Data Structure
###############################################

.. include:: /main/deprecation_banner.rst

The JSON-FULL format returns a list of dictionaries.

Each dictionary represents an instance of an adapter on a node and has the keys:

* name: The human friendly name of the adapter.
* name_raw: The name of the adapter as known by the REST API.
* name_plugin: The name of the adapter plugin as known by the REST API.
* node_name: The name of the node this adapter instance is running on.
* node_id: The ID of the node this adapter instance is running on.
* status: The text the REST API uses to represent the status of this adapter, one of:

  - "": has no connections
  - "success": has connections and all connections are working
  - "warning": has connections and one or more connections are broken

* features: Attributes associated with the adapter (example: "Triggerable")
* schemas:

  - cnx: A dictionary describing each of the settings that can be supplied when creating a new connection for this adapter.
  - generic: A dictionary showing the metadata and values for each adapter specific setting, if the adapter has specific settings under Advanced Settings in the GUI.

* config: A dictionary showing the metadata and values for each setting in Advanced Settings in the GUI.
* cnx: A list of dictionaries for all connections of this adapter.
* cnx_count_total: The count of all connections for this adapter.
* cnx_broken: The count of all broken connections for this adapter.
* cnx_working: The count of all working connections for this adapter.

.. seealso::

   :ref:`cnx_structure`: The JSON structure of connection metadata found in `cnx`,
   `cnx_bad`, and `cnx_ok`.
