.. include:: /main/.special.rst

devices labels
###############################################

This is a sub-command group under :doc:`grp_devices` that has commands to
you add, remove, or get labels (tags) for user assets.

Commands
===============================================

* :doc:`grp_assets_labels_cmds/cmd_add` to add labels to device assets.
* :doc:`grp_assets_labels_cmds/cmd_get` to get all labels defined for device assets.
* :doc:`grp_assets_labels_cmds/cmd_remove` to remove labels from device assets.


Help Page
===============================================

.. click:: axonius_api_client.cli.grp_labels:labels
   :prog: axonshell devices labels
