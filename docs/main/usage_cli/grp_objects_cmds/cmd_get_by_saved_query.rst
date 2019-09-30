.. include:: /main/.special.rst

devices/users get-by-saved-query
###############################################

This command will get assets returned from a saved query for users or devices.

Output feeds
===============================================

The output from this command is able to be supplied as input to these commands:

* :doc:`../grp_objects_reports_cmds/cmd_missing_adapters`
* :doc:`../grp_objects_labels_cmds/cmd_add`
* :doc:`../grp_objects_labels_cmds/cmd_remove`

Common Options
===============================================

* :ref:`connection_options`
* :ref:`export_options`

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_get_by_saved_query_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_objects.cmd_get_by_saved_query:cmd
   :prog: axonshell devices/users get-by-saved-query
