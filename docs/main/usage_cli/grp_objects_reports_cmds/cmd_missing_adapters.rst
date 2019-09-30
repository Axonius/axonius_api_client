.. include:: /main/.special.rst

devices/users reports missing-adapters
###############################################

This command will produce a report of all adapters missing from assets. In essence,
all this command does is add two new fields to the asset data:

* missing_nocnx: all of the adapters that are missing from this asset but have no connections.
* missing: all of the adapters that are missing from this asset but have connections.

Input feeds
===============================================

The input to this command as --rows must be from one of these commands:

* :doc:`../grp_objects_cmds/cmd_get`: To remove labels from all device or user
  assets returned from the query provided to the get command.
* :doc:`../grp_objects_cmds/cmd_get_by_saved_query`: To remove labels from all device or user
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
* :ref:`export_options` for examples of exporting data in different formats and outputs.
* :ref:`rows_option` for examples of working with input feeds.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_missing_adapters_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_reports.cmd_missing_adapters:cmd
   :prog: axonshell devices/users reports missing-adapters
