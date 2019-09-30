.. include:: /main/.special.rst

Find Using NOT
###############################################

This does the following:

* Get devices by hostname that do NOT match a value.
* This command builds a query for you, example:
  ``not (specific_data.data.hostname == "WIN-76F9735PMOJ"))``

.. code:: shell

   $ axonshell devices get-by-hostname \
     --value "WIN-76F9735PMOJ" \
     --value-not \
     --export-file device.json \
     --export-overwrite

.. raw:: html

    <script id="asciicast-271560" src="https://asciinema.org/a/271560.js" async></script>

.. include:: notes.rst
