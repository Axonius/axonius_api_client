.. include:: /main/.special.rst

adapters cnx get
###############################################

This command is used to extract the metadata for connections from the output of
the `adapters get` command and optionally filter the connections based on status or id.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* :ref:`export_options` for examples of exporting data in different formats and outputs.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_get_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_adapters.grp_cnx.cmd_get:cmd
   :prog: axonshell adapters cnx get
