.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Command line options for settings
###############################################

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

