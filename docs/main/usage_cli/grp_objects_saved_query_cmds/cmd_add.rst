.. include:: /main/.special.rst

devices/users saved-query add
###############################################

This command will add a saved query for users or devices.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* :ref:`export_options` for examples of exporting data in different formats and outputs.

Common Examples
===============================================

* :ref:`select_fields_ex` for examples of selecting which fields (columns) to include
  in the saved query for sort column, columns displayed, and column filters.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_add_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_saved_query.cmd_add:cmd
   :prog: axonshell devices/users saved-query add
