.. include:: /main/.special.rst

All adapters: all broken connections
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Get all of the adapters.
* Filter out the list of connections to only include those that are broken.

.. code:: shell

   $ axonshell adapters get | \
     axonshell adapters cnx get --no-working

.. raw:: html

   <script id="asciicast-271011" src="https://asciinema.org/a/271011.js" async></script>
