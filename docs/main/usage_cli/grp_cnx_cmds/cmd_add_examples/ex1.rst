.. include:: /main/.special.rst

Prompt for settings
###############################################

.. include:: /main/deprecation_banner.rst

If you don't supply any configuration items on the command line, this command
will prompt for the value of each setting for connections of the supplied adapter.

This example adds a new connection for the CSV adapter.

.. code:: shell

   $ axonshell adapters cnx add --adapter csv --export-file cnxadded.json

.. raw:: html

   <script id="asciicast-270375" src="https://asciinema.org/a/270375.js" async></script>
