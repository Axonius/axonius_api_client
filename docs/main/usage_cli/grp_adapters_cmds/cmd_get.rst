.. include:: /main/.special.rst

adapters get
###############################################

This command allows you to get metadata of adapters and their connections.

Output feeds
===============================================

The output from this command is able to be supplied as input to these commands:

* :doc:`../grp_cnx_cmds/cmd_check`
* :doc:`../grp_cnx_cmds/cmd_delete`
* :doc:`../grp_cnx_cmds/cmd_discover`
* :doc:`../grp_cnx_cmds/cmd_get`

Common Options
===============================================

* :ref:`connection_options`
* :ref:`export_options`

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_get_examples/*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_adapters.cmd_get:cmd
   :prog: axonshell adapters get
