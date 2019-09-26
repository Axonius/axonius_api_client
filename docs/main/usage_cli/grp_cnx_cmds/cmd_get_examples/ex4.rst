.. include:: /main/.special.rst

All adapters: all broken connections
###############################################

This does the following:

* Get all of the adapters.
* Filter out the list of connections to only include those that are broken.

.. code:: shell

   $ axonshell adapters get | \
     axonshell adapters cnx get --no-working

.. raw:: html

   <script id="asciicast-271011" src="https://asciinema.org/a/271011.js" async></script>

Single adapter: single connection by valid ID
-------------------------------------------------

This does the following:

* Get the Active Directory adapter.
* Get a single connection with a valid ID.

.. code:: shell

   $ axonshell adapters get --name active_directory | \
     axonshell adapters cnx get --id TestDomain.test

.. raw:: html

   <script id="asciicast-271012" src="https://asciinema.org/a/271012.js" async></script>
