.. include:: /main/.special.rst

devices/users get-fields-default
###############################################

This command will produce a report of the default fields (columns) for users or devices.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* :ref:`export_options` for examples of exporting data in different formats and outputs.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_get_fields_default_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_assets.cmd_get_fields_default:cmd
   :prog: axonshell devices/users get-fields-default
