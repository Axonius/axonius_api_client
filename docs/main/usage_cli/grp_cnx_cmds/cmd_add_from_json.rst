.. include:: /main/.special.rst

adapters cnx add-from-json
###############################################

This command will add a perform a connectivity test for a connection for an adapter on
a node.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* :ref:`export_options` for examples of exporting data in different formats and outputs.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_add_from_json_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_adapters.grp_cnx.cmd_add_from_json:cmd
   :prog: axonshell adapters cnx add-from-json
