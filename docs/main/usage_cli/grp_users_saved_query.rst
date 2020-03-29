.. include:: /main/.special.rst

users saved_query
###############################################

This is a sub-command group under :doc:`grp_users` that has commands
to add, delete, or get saved queries for user assets.

Commands
===============================================

* :doc:`grp_objects_saved_query_cmds/cmd_add` to add a saved query for user assets.
* :doc:`grp_objects_saved_query_cmds/cmd_delete` to delete an existing saved query for
  user assets.
* :doc:`grp_objects_saved_query_cmds/cmd_get` to get all saved queries for user assets.
* :doc:`grp_objects_saved_query_cmds/cmd_get_by_name` to get a single saved query by
  name for user assets.

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_saved_query:saved_query
   :prog: axonshell users saved_query
