.. include:: /main/.special.rst

users reports
###############################################

This is a sub-command group under :doc:`grp_users` that has commands to produce
reports for user assets.

Commands
===============================================

* :doc:`grp_objects_reports_cmds/cmd_missing_adapters` to create a report that shows
  the adapters that are missing from user assets that are fed into the input
  of this command.

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_reports:reports
   :prog: axonshell users reports
