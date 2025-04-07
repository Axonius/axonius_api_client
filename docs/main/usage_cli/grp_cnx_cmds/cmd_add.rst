.. include:: /main/.special.rst

adapters cnx add
###############################################

.. include:: /main/deprecation_banner.rst

This command will add a new connection for an adapter on a node.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* :ref:`export_options` for examples of exporting data in different formats and outputs.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_add_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_adapters.grp_cnx.cmd_add:cmd
   :prog: axonshell adapters cnx add
