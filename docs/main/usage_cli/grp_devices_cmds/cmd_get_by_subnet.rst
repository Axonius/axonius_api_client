.. include:: /main/.special.rst

devices get-by-subnet
###############################################

This command lets you search for devices that are in a given subnet and export the data to CSV or JSON.

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

.. note::

   While this command shares most of the options with all the other ``get-by-..``
   commands, it does not have a --value-regex option.

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_objects.cmd_get_by_subnet:cmd
   :prog: axonshell devices get-by-subnet
