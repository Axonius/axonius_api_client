.. include:: /main/.special.rst

adapters cnx test-by-id
###############################################

.. include:: /main/deprecation_banner.rst

This command will trigger a test_by_id (aka fetch) for a connection of an adapter on a node.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* :ref:`export_options` for examples of exporting data in different formats and outputs.
* :ref:`rows_option` for examples of working with input feeds.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_test_by_id_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_adapters.grp_cnx.cmd_test_by_id:cmd
   :prog: axonshell adapters cnx test-by-id
