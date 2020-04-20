.. include:: /main/.special.rst

devices get-by-ip
###############################################

This command lets you search for devices by IP Address and export the data to CSV or JSON.

Output feeds
===============================================

The output from this command is able to be supplied as input to these commands:

* :doc:`../grp_assets_reports_cmds/cmd_missing_adapters` to build a report of
  missing adapters for all assets returned from this command.
* :doc:`../grp_assets_labels_cmds/cmd_add` to add labels to all assets returned from
  this command.
* :doc:`../grp_assets_labels_cmds/cmd_remove` to remove labels from all assets returned
  from this command.

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

.. click:: axonius_api_client.cli.grp_assets.cmd_get_by_ip:cmd
   :prog: axonshell devices get-by-ip
