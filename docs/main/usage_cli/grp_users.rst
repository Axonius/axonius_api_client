.. include:: /main/.special.rst

users
###############################################

.. include:: /main/deprecation_banner.rst

This is a command group under the main :doc:`root` that has commands for getting
user assets using queries built by the Query Wizard in the GUI, saved queries, and
queries built for you by various ``get-by..`` commands.

Sub Command Groups
===============================================

* :doc:`grp_users_saved_query` has commands to add, delete, or get saved queries for
  user assets.

Commands
===============================================

* :doc:`grp_assets_cmds/cmd_count` to get the count of user assets that would be returned
  from a query built by the Query Wizard in the GUI.
* :doc:`grp_assets_cmds/cmd_count_by_saved_query` to get the count of user assets that
  would be returned from a saved query.
* :doc:`grp_assets_cmds/cmd_get_fields` to get the fields (columns) that are available
  for user assets from all adapters.
* :doc:`grp_assets_cmds/cmd_get` to get user assets using a query built by
  the Query Wizard in the GUI.
* :doc:`grp_assets_cmds/cmd_get_by_saved_query` to get user assets using a
  saved query.
* :doc:`grp_users_cmds/cmd_get_by_mail` to build a query for you that gets
  user assets by email address.
* :doc:`grp_users_cmds/cmd_get_by_username` to build a query for you that gets
  user assets by username.


Help Page
===============================================

.. click:: axonius_api_client.cli.grp_assets:users
   :prog: axonshell users
