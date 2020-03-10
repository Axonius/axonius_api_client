.. include:: /main/.special.rst

Discover a single connection on an adapter
###############################################

.. code:: shell

   $ axonshell adapters get --name aws | \
     axonshell adapters cnx get --id ***REMOVED*** | \
     axonshell adapters cnx discover --no-error

.. raw:: html

   <script id="asciicast-270870" src="https://asciinema.org/a/270870.js" async></script>
