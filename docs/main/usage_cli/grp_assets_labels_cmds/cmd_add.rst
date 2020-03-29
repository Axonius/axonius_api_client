.. include:: /main/.special.rst

devices/users labels add
###############################################

This command will add labels (tags) to users or devices.

Input feeds
===============================================

The input to this command as --rows must be from one of these commands:

* :doc:`../grp_assets_cmds/cmd_get`: To remove labels from all device or user
  assets returned from the query provided to the get command.
* :doc:`../grp_assets_cmds/cmd_get_by_saved_query`: To remove labels from all device or user
  assets returned from the query defined in the saved query.
* :doc:`../grp_devices_cmds/cmd_get_by_hostname`: To remove labels from all device assets returned
  from the query built by the get_by command.
* :doc:`../grp_devices_cmds/cmd_get_by_ip`: To remove labels from all device assets returned
  from the query built by the get_by command.
* :doc:`../grp_devices_cmds/cmd_get_by_mac`: To remove labels from all device assets returned
  from the query built by the get_by command.
* :doc:`../grp_devices_cmds/cmd_get_by_subnet`: To remove labels from all device assets returned
  from the query built by the get_by command.
* :doc:`../grp_users_cmds/cmd_get_by_mail`: To remove labels from all user assets returned
  from the query built by the get_by command.
* :doc:`../grp_users_cmds/cmd_get_by_username`: To remove labels from all user assets returned
  from the query built by the get_by command.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* :ref:`rows_option` for examples of working with input feeds.
* There are no export options for this command since it only returns the number of
  assets tagged.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_add_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_labels.cmd_add:cmd
   :prog: axonshell devices/users labels add
