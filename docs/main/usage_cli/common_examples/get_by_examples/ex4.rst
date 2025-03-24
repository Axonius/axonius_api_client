.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Find Using Regular Expressions - Matches Found
###############################################

This does the following:

* Get devices by hostname that match a regular expression.
* This command builds a query for you, example:
  ``(specific_data.data.hostname == regex("win.*", "i"))``

.. code:: shell

   $ axonshell devices get-by-hostname \
     --value "win.*" \
     --value-regex \
     --export-file device.json \
     --export-overwrite

.. raw:: html

   <script id="asciicast-271559" src="https://asciinema.org/a/271559.js" async></script>

.. include:: notes.rst

.. note::

    The ``devices get-by-subnet`` command does not support using regular expressions,
    so it does not have a --value-regex option.
