.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Find Single Item - Match Found
###############################################

This does the following:

* Get a device by hostname that does exist.
* This command builds a query for you, example:
  ``(specific_data.data.hostname == "WIN-76F9735PMOJ")``

.. code:: shell

   $ axonshell devices get-by-hostname \
     --value WIN-76F9735PMOJ \
     --export-file device.json

.. raw:: html

   <script id="asciicast-271557" src="https://asciinema.org/a/271557.js" async></script>

.. include:: notes.rst
