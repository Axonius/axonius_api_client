.. include:: /main/.special.rst

.. _tools_write_config:

tools write-config
###############################################

This command will prompt for the :ref:`connection_options`, test if the supplied values connect properly, then write the variables to a .env file in the current
working directory.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_write_config_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_tools.cmd_write_config:cmd
   :prog: axonshell tools write-config
