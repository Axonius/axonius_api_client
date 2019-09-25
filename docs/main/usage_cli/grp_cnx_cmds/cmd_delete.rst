.. include:: /main/.special.rst

adapters cnx delete
###############################################

Input feeds
===============================================

The input to this command as --rows must be from one of these commands:

* :doc:`../grp_adapters_cmds/cmd_get`: Supplying input from this command will delete
  **ALL** of the connections for **ALL** of the adapters returned from this command.
* :doc:`../grp_cnx_cmds/cmd_get`: Supplying input from this command will delete all
  of the connections that have been returned by the supplied filters.

.. seealso::

   :ref:`rows_option` for examples of working with input feeds.

   :doc:`../grp_cnx_cmds/cmd_get` for examples of filtering connections using
   `axonshell adapters get | axonshell adapters cnx get`.

Common Options
===============================================

* :ref:`connection_options`
* :ref:`export_options`
* :ref:`rows_option`

Examples
===============================================

Delete with no options
--------------------------------------------------

This will throw an error because we didn't supply --force.

.. code:: shell

   $ # add a csv connection that we can delete
   $ axonshell a c a -a csv -c user_id=dvcs_from_axonshell -c csv=/demo/dvc.csv -npo

   $ axonshell adapters get --name csv | \
     axonshell adapters cnx get --id dvcs_from_axonshell | \
     axonshell adapters cnx delete

.. raw:: html

   <script id="asciicast-270864" src="https://asciinema.org/a/270864.js" async></script>

Delete with --force
--------------------------------------------------

This will delete a connection in --wait seconds (30 by default).

.. code:: shell

   $ # add a csv connection that we can delete
   $ axonshell a c a -a csv -c user_id=dvcs_from_axonshell -c csv=/demo/dvc.csv -npo

   $ axonshell adapters get --name csv | \
     axonshell adapters cnx get --id dvcs_from_axonshell | \
     axonshell adapters cnx delete --force


.. raw:: html

  <script id="asciicast-270865" src="https://asciinema.org/a/270865.js" async></script>

Delete with --force --wait 0 --delete-entities
--------------------------------------------------

This will delete a connection and all of its associated entities in 0 seconds.

.. code:: shell

   $ # add a csv connection that we can delete
   $ axonshell a c a -a csv -c user_id=dvcs_from_axonshell -c csv=/demo/dvc.csv -npo

   $ axonshell adapters get --name csv | \
     axonshell adapters cnx get --id dvcs_from_axonshell | \
     axonshell adapters cnx delete --force --wait 0 --delete-entities

.. raw:: html

   <script id="asciicast-270866" src="https://asciinema.org/a/270866.js" async></script>

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_cnx.cmd_delete:cmd
   :prog: axonshell adapters cnx delete
