.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Find Using Multiple Values
###############################################

This does the following:

* Get devices by hostname that match multiple values.
* This command builds a query for you, example:
  ``(specific_data.data.hostname in ['WIN-76F9735PMOJ', 'EC2AMAZ-V8E9DHF'])``

.. code:: shell

   $ axonshell devices get-by-hostname \
     --value "WIN-76F9735PMOJ" \
     --value "EC2AMAZ-V8E9DHF" \
     --export-file device.json \
     --export-overwrite

.. raw:: html

    <script id="asciicast-271561" src="https://asciinema.org/a/271561.js" async></script>

.. include:: notes.rst
