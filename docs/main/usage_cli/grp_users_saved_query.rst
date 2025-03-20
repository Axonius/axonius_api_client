.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

users saved_query
###############################################

This is a sub-command group under :doc:`grp_users` that has commands
to add, delete, or get saved queries for user assets.

Commands
===============================================

* :doc:`grp_assets_saved_query_cmds/cmd_add` to add a saved query.
* :doc:`grp_assets_saved_query_cmds/cmd_delete_by_name` to delete a saved query by name.
* :doc:`grp_assets_saved_query_cmds/cmd_delete_by_tags` to delete saved queries by tags.
* :doc:`grp_assets_saved_query_cmds/cmd_get` to get all saved queries.
* :doc:`grp_assets_saved_query_cmds/cmd_get_by_name` to get a saved query by name.


Help Page
===============================================

.. click:: axonius_api_client.cli.grp_assets.grp_saved_query:saved_query
   :prog: axonshell users saved_query
