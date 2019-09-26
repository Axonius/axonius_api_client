.. include:: /main/.special.rst

adapters cnx delete
###############################################

This command will delete a connection from an adapter on a node.

Input feeds
===============================================

The input to this command as --rows must be from one of these commands:

* :doc:`../grp_adapters_cmds/cmd_get`: Supplying input from this command will delete
  **ALL** of the connections for **ALL** of the adapters returned from this command.
* :doc:`../grp_cnx_cmds/cmd_get`: Supplying input from this command will delete all
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

   cmd_delete_examples/*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_cnx.cmd_delete:cmd
   :prog: axonshell adapters cnx delete
