.. include:: /main/.special.rst

devices saved_query
###############################################

This is a sub-command group under :doc:`grp_devices` that has commands
to add, delete, or get saved queries for device assets.

Commands
===============================================

* :doc:`grp_assets_saved_query_cmds/cmd_add` to add a saved query for device assets.
* :doc:`grp_assets_saved_query_cmds/cmd_delete` to delete an existing saved query for
  device assets.
* :doc:`grp_assets_saved_query_cmds/cmd_get` to get all saved queries for device assets.
* :doc:`grp_assets_saved_query_cmds/cmd_get_by_name` to get a single saved query by
  name for device assets.

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_saved_query:saved_query
   :prog: axonshell devices saved_query
