.. include:: /main/.special.rst

tools
###############################################

This is a command group under the main :doc:`root` that has commands for
starting a python interactive shell and writing a .env configuration file with
the credentials and URL for connecting to Axonius.

Commands
===============================================

* :doc:`grp_tools_cmds/cmd_shell` to start a python interactive shell.
* :doc:`grp_tools_cmds/cmd_write_config` to write a .env file with the credentials
  and URL for connecting to Axonius.

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_tools:tools
   :prog: axonshell tools
