.. include:: /main/.special.rst

devices/users get
###############################################

This allows you to get all of the assets for devices or users and export the data
to CSV or JSON.

.. seealso::

    :ref:`shellhell` for how to deal with quoting the query value in various shells.

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

* :ref:`select_fields_ex`

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_get_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_objects.cmd_get:cmd
   :prog: axonshell devices/users get
