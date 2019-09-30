.. include:: /main/.special.rst

adapters
###############################################

This is a command group under the main :doc:`root` that has commands for getting
metadata for adapters.

Sub Command Groups
===============================================

This command group has the following sub command groups:

* :doc:`grp_cnx` has commands to work with adapter connections.

Commands
===============================================

* :doc:`grp_adapters_cmds/cmd_get` to get metadata for adapters and filter based on
  a number of different attributes.

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_adapters:adapters
   :prog: axonshell adapters
