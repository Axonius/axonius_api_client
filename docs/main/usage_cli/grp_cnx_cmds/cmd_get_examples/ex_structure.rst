.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

.. _cnx_structure:

Connecton Metadata JSON Data Structure
==============================================

The JSON format returns a list of dictionaries.

Each dictionary represents an instance of a connection for an adapter on a node
and has the keys:

* node_name: The name of the node this connections adapter is running on.
* node_id: The ID of the node this connections adapter is running on.
* adapter_name: The human friendly name of this connections adapter.
* adapter_name_raw: The name of this connections adapter as known by the REST API.
* adapter_status: A boolean value reflecting the status of this connections adapter,
  one of:

  * None: has no connections
  * True: has connections all connections are working
  * False: has connections and one or more connections are broken

* status: A boolean value reflecting the status of this connection, one of:

  * True: this connection is working
  * False: this connection is broken

* status_raw: The text the API uses to represent the status of this adapter, one of:

  * "success": this connection is working
  * "error": this connection is broken

* config: A dictionary showing the configuration of this connection. Each key represents
  a setting name, with the value being a dictionary that shows the metadata for
  each setting (title, type, required, and value).
* config_raw: A dictionary showing the raw configuration of this connection as stored
  by the REST API.
* id: The ID of this connection, which is usually a string formed from the value for
  the configuration key `domain`.
* uuid: The unique ID for this connection, as known by the REST API.
* date_fetched: The timestamp when this connection was last fetched. This does not
  record when the last regularly scheduled discovery was done, rather it records
  the last time this connection was updated and saved.
* error: If not empty, the error the connection had when connection to the product
  associated with this connections adapter.

.. seealso::

   :ref:`adapter_structure`: The JSON structure of adapter metadata that holds
   connection metadata.
