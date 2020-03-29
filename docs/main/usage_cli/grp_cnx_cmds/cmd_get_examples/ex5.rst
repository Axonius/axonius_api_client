.. include:: /main/.special.rst

Single adapter: single connection by valid ID
###############################################

This does the following:

* Get the Active Directory adapter.
* Get a single connection with a valid ID.

.. code:: shell

   $ axonshell adapters get --name active_directory | \
     axonshell adapters cnx get --id TestDomain.test

.. raw:: html

   <script id="asciicast-271012" src="https://asciinema.org/a/271012.js" async></script>
