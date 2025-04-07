.. include:: /main/.special.rst

All adapters: all connections
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Get all of the adapters.
* Get all of the connections for all of the adapters.

.. code:: shell

   $ axonshell adapters get | \
     axonshell adapters cnx get > cnxs.json

   $ # count the number of connections
   $ cat cnxs.json | jq '. | length'

.. raw:: html

   <script id="asciicast-271007" src="https://asciinema.org/a/271007.js" async></script>
