.. include:: /main/.special.rst

adapters cnx add
###############################################

Output feeds
===============================================

The output from this command is able to be supplied as input to these commands:

* :doc:`../grp_cnx_cmds/cmd_check`
* :doc:`../grp_cnx_cmds/cmd_delete`
* :doc:`../grp_cnx_cmds/cmd_discover`
* :doc:`../grp_cnx_cmds/cmd_get`

Common Options
===============================================

* :ref:`connection_options`
* :ref:`export_options`

Examples
===============================================

Prompt for settings
-----------------------------------------------

If you don't supply any configuration items on the command line, this command
will prompt for the value of each setting for connections of the supplied adapter.

This example adds a new connection for the CSV adapter.

.. code:: shell

   $ axonshell adapters cnx add --adapter csv --export-file cnxadded.json

.. raw:: html

   <script id="asciicast-270375" src="https://asciinema.org/a/270375.js" async></script>

Command line options for settings
-----------------------------------------------

This way you won't be prompted for the values of each setting, which will allow
you to automate adding a new connection.

Some adapters, like the CSV adapter, have multiple workflows that make the settings for connections all optional, when really in order for any given workflow to work
correctly, you need to provide some settings that are marked as optional.

The "user_id" setting is the only one marked as required by the CSV adapter. However, if we want to upload a file we need to supply the optional "csv" setting.

We can solve for that by supplying those items on the command line using
"-c / --config setting=value".

We also supply "-npo / --no-prompt-opt" to not be prompted for all of the other settings. We could use "-sk / --skip setting_name_regex" instead to skip specific settings.

.. code:: shell

   $ axonshell adapters cnx add --adapter csv \
     --export-file cnxadded.json \
     --config user_id=dvcs_from_axonshell \
     --config csv=dvc.csv \
     --no-prompt-opt

.. raw:: html

    <script id="asciicast-270379" src="https://asciinema.org/a/270379.js" async></script>

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_cnx.cmd_add:cmd
   :prog: axonshell adapters cnx add
