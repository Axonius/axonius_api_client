.. include:: /main/.special.rst

.. _tools_write_config:

tools write-config
###############################################

This command will prompt for the :ref:`connection_options`, test if the supplied values connect properly, then write the variables to a .env file in the current
working directory.

Examples
===============================================

Prompt for connection info, test connection, write .env file
--------------------------------------------------------------------

.. raw:: html

   <script id="asciicast-270345" src="https://asciinema.org/a/270345.js" async></script>

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_tools.cmd_write_config:cmd
   :prog: axonshell tools write-config
