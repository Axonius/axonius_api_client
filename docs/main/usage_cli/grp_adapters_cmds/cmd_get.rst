.. include:: /main/.special.rst

adapters get
###############################################

.. include:: /main/deprecation_banner.rst

This command allows you to get metadata of adapters and their connections.

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

.. click:: axonius_api_client.cli.grp_adapters.cmd_get:cmd
   :prog: axonshell adapters get
