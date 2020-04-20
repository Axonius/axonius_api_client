.. include:: /main/.special.rst

users labels
###############################################

This is a sub-command group under :doc:`grp_users` that has commands to
add, remove, or get labels (tags) for user assets.

Commands
===============================================

* :doc:`grp_assets_labels_cmds/cmd_add` to add labels to user assets.
* :doc:`grp_assets_labels_cmds/cmd_get` to get all labels defined for user assets.
* :doc:`grp_assets_labels_cmds/cmd_remove` to remove labels from user assets.

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_labels:labels
   :prog: axonshell users labels
