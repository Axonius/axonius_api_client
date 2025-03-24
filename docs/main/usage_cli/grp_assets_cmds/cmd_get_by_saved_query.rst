.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

devices/users get-by-saved-query
###############################################

This command will get assets returned from a saved query for users or devices.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* :ref:`export_options` for examples of exporting data in different formats and outputs.
* :ref:`select_fields_ex` for examples of selecting which fields
  (columns) to include in the response. The fields you supply for get-by-saved-query
  will be appended to the fields specified inside of the saved query.
  (:blue:`added in 2.1.4`)

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_get_by_saved_query_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_assets.cmd_get_by_saved_query:cmd
   :prog: axonshell devices/users get-by-saved-query
