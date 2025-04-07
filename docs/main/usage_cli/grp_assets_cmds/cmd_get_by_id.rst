.. include:: /main/.special.rst

devices/users get-by-id
###############################################

.. include:: /main/deprecation_banner.rst

This command will get ALL data for a single asset.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_get_by_id_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_assets.cmd_get_by_id:cmd
   :prog: axonshell devices/users get-by-id
