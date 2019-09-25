.. include:: /main/.special.rst

adapters cnx check
###############################################

Input feeds
===============================================

The input to this command as --rows must be from one of these commands:

* :doc:`../grp_adapters_cmds/cmd_get`: Supplying input from this command will check
  **ALL** of the connections for **ALL** of the adapters returned from this command.
* :doc:`../grp_cnx_cmds/cmd_get`: Supplying input from this command will check all
  of the connections that have been returned by the supplied filters.

.. seealso::

   :ref:`rows_option` for examples of working with input feeds.

   :doc:`../grp_cnx_cmds/cmd_get` for examples of filtering connections using
   `axonshell adapters get | axonshell adapters cnx get`.

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

.. code:: shell

   $ axonshell adapters get --name aws | \
     axonshell adapters cnx get --no-broken | \
     axonshell adapters cnx check -xf check.json

.. raw:: html

   <script id="asciicast-270380" src="https://asciinema.org/a/270380.js" async></script>

Check all connections for the AWS adapter
--------------------------------------------------

This does the following:

* Get the AWS adapter on the master node
* Check all of the connections listed in the AWS adapter metadata but do not
  stop when a connection test fails.

.. code:: shell

   $ axonshell adapters get --name aws | \
     axonshell adapters cnx check --no-error -xf check.json

.. raw:: html

   <script id="asciicast-270387" src="https://asciinema.org/a/270387.js" async></script>

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_cnx.cmd_check:cmd
   :prog: axonshell adapters cnx check
