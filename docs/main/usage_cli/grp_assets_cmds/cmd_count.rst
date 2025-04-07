.. include:: /main/.special.rst

devices/users count
###############################################

.. include:: /main/deprecation_banner.rst

This command will get the count of assets that a query would return for users or devices
and could be used as part of a script to do something based on the number returned.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* There are no export options for this command since it only returns a number.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_count_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_assets.cmd_count:cmd
   :prog: axonshell users/devices count
