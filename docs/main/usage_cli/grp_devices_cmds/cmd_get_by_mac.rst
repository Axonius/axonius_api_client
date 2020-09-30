.. include:: /main/.special.rst

devices get-by-mac
###############################################

This command lets you search for devices by MAC Address and export the data to CSV or JSON.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* :ref:`export_options` for examples of exporting data in different formats and outputs.

Common Examples
===============================================

* :ref:`get_by_ex` for examples that are common to all ``get-by..`` commands.
* :ref:`select_fields_ex` for examples of selecting which fields (columns) to include
  in the response.

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_assets:cmd_get_by_mac
   :prog: axonshell devices get-by-mac
