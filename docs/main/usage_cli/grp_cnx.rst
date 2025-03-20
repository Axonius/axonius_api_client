.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

adapters cnx
###############################################

This is a sub-command group under :doc:`grp_adapters` that has commands for getting,
adding, deleting, checking (test reachability), and discovering (triggering a fetch)
of connections.

Commands
===============================================

* :doc:`grp_cnx_cmds/cmd_add` to add a connection for an adapter.
* :doc:`grp_cnx_cmds/cmd_add_from_json` to add multiple connections from JSON.
* :doc:`grp_cnx_cmds/cmd_get` to get connections for an adapter
* :doc:`grp_cnx_cmds/cmd_get_by_id` to get connections for an adapter by ID
* :doc:`grp_cnx_cmds/cmd_get` to test a connection for an adapter
* :doc:`grp_cnx_cmds/cmd_get_by_id` to test a connection for an adapter

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_adapters.grp_cnx:cnx
   :prog: axonshell adapters cnx

