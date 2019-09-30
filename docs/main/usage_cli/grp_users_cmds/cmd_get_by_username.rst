.. include:: /main/.special.rst

users get-by-username
###############################################

This command lets you search for users by username and export the data to CSV or JSON.

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

Common Examples
===============================================

* :ref:`get_by_ex`
* :ref:`select_fields_ex`

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_objects.cmd_get_by_username:cmd
   :prog: axonshell users get-by-username
