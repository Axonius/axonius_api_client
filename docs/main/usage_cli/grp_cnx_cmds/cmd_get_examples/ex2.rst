.. include:: /main/.special.rst

All adapters: single connection by invalid ID
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Get all of the adapters.
* Try to find an connection with an invalid ID, which will throw
  an error showing all of the valid ID's for all of the connections across all of
  the adapters.

.. code:: shell

   $ axonshell adapters get | \
     axonshell adapters cnx get --id foxtrot_tango

.. raw:: html

   <script id="asciicast-271008" src="https://asciinema.org/a/271008.js" async></script>
