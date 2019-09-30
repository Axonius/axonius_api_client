.. include:: /main/.special.rst

devices get-by-subnet
###############################################

This command lets you search for devices that are in a given subnet and export the data to CSV or JSON.

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
