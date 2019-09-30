.. include:: /main/.special.rst

adapters cnx
###############################################

This is a sub-command group under :doc:`grp_adapters` that has commands for getting,
adding, deleting, checking (test reachability), and discovering (triggering a fetch)
of connections.

Commands
===============================================

* :doc:`grp_cnx_cmds/cmd_add` to add a connection for an adapter.
* :doc:`grp_cnx_cmds/cmd_check` to check (test the reachability) of an existing connection
  for an adapter.
* :doc:`grp_cnx_cmds/cmd_delete` to delete an existing connection for an adapter.
* :doc:`grp_cnx_cmds/cmd_discover` to discover (trigger a fetch) of an existing
  connection for an adapter.
* :doc:`grp_cnx_cmds/cmd_get` to filter metadata from adapters to only include
  connections that match various attributes.

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_cnx:cnx
   :prog: axonshell adapters cnx

