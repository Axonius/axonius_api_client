.. include:: /main/.special.rst

Find Using Regular Expressions - No Matches Found
#################################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Get devices by hostname that match a regular expression.
* This command builds a query for you, example:
  ``(specific_data.data.hostname == regex("nosuchname.*", "i"))``

.. code:: shell

   $ axonshell devices get-by-hostname \
     --value "nosuchname.*" \
     --value-regex \
     --export-file device.json \
     --export-overwrite

.. raw:: html

   <script id="asciicast-271558" src="https://asciinema.org/a/271558.js" async></script>

.. include:: notes.rst
