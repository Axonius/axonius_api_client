.. include:: /main/.special.rst

Find Matches With A Query Prefix
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Get devices by hostname and add ``INCLUDE OUTDATED:`` to the beginning of the
  query built by the command.
* This command builds a query for you, example:
  ``INCLUDE OUTDATED: (specific_data.data.hostname == regex("WIN.*", "i"))``

.. code:: shell

   $ axonshell devices get-by-hostname \
     --value "WIN.*" \
     --value-regex \
     --query-pre "INCLUDE OUTDATED:" \
     --export-file device.json \
     --export-overwrite

.. raw:: html

    <script id="asciicast-271562" src="https://asciinema.org/a/271562.js" async></script>

.. include:: notes.rst
