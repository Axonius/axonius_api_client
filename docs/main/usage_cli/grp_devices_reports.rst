.. include:: /main/.special.rst

devices reports
###############################################

This is a sub-command group under :doc:`grp_devices` that has commands to produce
reports for device assets.

Commands
===============================================

* :doc:`grp_assets_reports_cmds/cmd_missing_adapters` to create a report that shows
  the adapters that are missing from device assets that are fed into the input
  of this command.

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_reports:reports
   :prog: axonshell devices reports
