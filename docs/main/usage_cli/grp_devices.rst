.. include:: /main/.special.rst


devices
###############################################

.. include:: /main/deprecation_banner.rst

This is a command group under the main :doc:`root` that has commands for getting
device assets using queries built by the Query Wizard in the GUI, saved queries, and
queries built for you by various ``get-by..`` commands.

Sub Command Groups
===============================================

* :doc:`grp_devices_saved_query` has commands to add, delete, or get saved queries for
  device assets.

Commands
===============================================

* :doc:`grp_assets_cmds/cmd_count` to get the count of device assets that would be returned
  from a query built by the Query Wizard in the GUI.
* :doc:`grp_assets_cmds/cmd_count_by_saved_query` to get the count of device assets that
  would be returned from a saved query.
* :doc:`grp_assets_cmds/cmd_get_fields` to get the fields (columns) that are available
  for device assets from all adapters.
* :doc:`grp_assets_cmds/cmd_get` to get device assets using a query built by
  the Query Wizard in the GUI.
* :doc:`grp_assets_cmds/cmd_get_by_saved_query` to get device assets using a
  saved query.
* :doc:`grp_devices_cmds/cmd_get_by_hostname` to build a query for you that gets
  device assets by hostname.
* :doc:`grp_devices_cmds/cmd_get_by_ip` to build a query for you that gets
  device assets by IP address.
* :doc:`grp_devices_cmds/cmd_get_by_mac` to build a query for you that gets
  device assets by MAC address.
* :doc:`grp_devices_cmds/cmd_get_by_subnet` to build a query for you that gets
  device assets that are in a given subnet.

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_assets:devices
   :prog: axonshell devices
