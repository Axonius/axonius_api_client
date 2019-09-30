.. include:: /main/.special.rst

adapters cnx get
###############################################

This command is used to extract the metadata for connections from the output of
the `adapters get` command and optionally filter the connections based on status or id.

Input feeds
===============================================

The input to this command as --rows must be from one of these commands:

* :doc:`../grp_adapters_cmds/cmd_get`: You need to feed the input of `adapters get` to
  this command.

.. seealso::

   :ref:`rows_option` for examples of working with input feeds.

Common Options
===============================================

* :ref:`connection_options`
* :ref:`export_options`
* :ref:`rows_option`

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_get_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_cnx.cmd_get:cmd
   :prog: axonshell adapters cnx get
