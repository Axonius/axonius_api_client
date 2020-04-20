.. include:: /main/.special.rst

devices/users labels get
###############################################

This command will get all of the labels known by the system for users or devices.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* There are no export options for this command since it only a simple list of known
  labels.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_get_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_labels.cmd_get:cmd
   :prog: axonshell devices/users labels get
