.. include:: /main/.special.rst

Filtering on adapter status
###############################################

.. code:: shell

   $ # filter out adapters with no connections
   $ axonshell adapters get --name awsx --no-cnx-none

   $ # only show adapters with broken connections
   $ axonshell adapters get --name awsx --no-cnx-none --no-cnx-working

.. raw:: html

    <script id="asciicast-270362" src="https://asciinema.org/a/270362.js" async></script>

