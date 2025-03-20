.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

devices/users get-fields
###############################################

This command will produce a report of all fields for users or devices.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* :ref:`export_options` for examples of exporting data in different formats and outputs.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_get_fields_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_assets.cmd_get_fields:cmd
   :prog: axonshell devices/users get-fields
