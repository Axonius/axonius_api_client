.. include:: /main/.special.rst

adapters cnx check
###############################################

This command will add a perform a connectivity test for a connection for an adapter on
a node.

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

Common Options
===============================================

* :ref:`connection_options`
* :ref:`export_options`
* :ref:`rows_option`

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_check_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_cnx.cmd_check:cmd
   :prog: axonshell adapters cnx check
