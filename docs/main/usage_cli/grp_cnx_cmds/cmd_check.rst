.. include:: /main/.special.rst

adapters cnx check
###############################################

Input feeds
===============================================

See :ref:`rows_option` for examples of working with input feeds.

The input to this command as --rows must be from one of these commands:

* :doc:`../grp_adapters_cmds/cmd_get`: Supplying input from this command will check ALL of the connections for ALL of the adapters returned from this command.
* :doc:`../grp_cnx_cmds/cmd_get`

The input for --rows can also be from these commands, although they don't make
much sense to use because a check is already performed by the API:

* :doc:`../grp_cnx_cmds/cmd_add`:
* :doc:`../grp_cnx_cmds/cmd_check`:
* :doc:`../grp_cnx_cmds/cmd_discover`

Output feeds
===============================================

The output from this command is able to be supplied as input to these commands:

* :doc:`../grp_cnx_cmds/cmd_delete`
* :doc:`../grp_cnx_cmds/cmd_discover`
* :doc:`../grp_cnx_cmds/cmd_get`

Common Options
===============================================

* :ref:`connection_options`
* :ref:`export_options`
* :ref:`rows_option`

Examples
===============================================

Check only working connections for the AWS adapter
--------------------------------------------------

This does the following:

* Get the AWS adapter on the master node
* Get only the working connections from the AWS adapter metadata
* Check that the working connections can reach their endpoints.

.. raw:: html

   <script id="asciicast-270380" src="https://asciinema.org/a/270380.js" async></script>

Check all connections for the AWS adapter
--------------------------------------------------

This does the following:

* Get the AWS adapter on the master node
* Check all of the connections listed in the AWS adapter metadata but do not
  stop when a connection test fails.

.. raw:: html

   <script id="asciicast-270387" src="https://asciinema.org/a/270387.js" async></script>

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_cnx.cmd_check:cmd
   :prog: axonshell adapters cnx check
