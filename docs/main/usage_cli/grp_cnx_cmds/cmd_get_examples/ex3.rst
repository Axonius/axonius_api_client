.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

All adapters: all working connections
###############################################

This does the following:

* Get all of the adapters.
* Filter out the list of connections to only include those that are working.

.. code:: shell

   $ axonshell adapters get | \
     axonshell adapters cnx get --no-broken

.. raw:: html

   <script id="asciicast-271010" src="https://asciinema.org/a/271010.js" async></script>
