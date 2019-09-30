.. include:: /main/.special.rst

devices/users saved-query get
###############################################

This command will get all saved queries for users or devices.

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

.. click:: axonius_api_client.cli.grp_saved_query.cmd_get:cmd
   :prog: axonshell devices/users saved-query get
