.. include:: /main/.special.rst

No filters, json and json-full exports
###############################################

.. code:: shell

   $ # export as STR (the default) to STDOUT
   $ axonshell adapters get

   $ # export as JSON to a file
   $ axonshell adapters get --export-format json > adapters.json

   $ # export as JSON-FULL to a file to show additional details
   $ axonshell adapters get --export-format json-full > adapters.json

.. raw:: html

    <script id="asciicast-332401" src="https://asciinema.org/a/332401.js" async></script>
