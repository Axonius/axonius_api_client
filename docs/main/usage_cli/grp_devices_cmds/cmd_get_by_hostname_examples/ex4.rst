.. include:: /main/.special.rst

Multiple Item Found
###############################################

This does the following:

* Get a device by hostname using regular expression that does match.

.. code:: shell

   $ axonshell devices get-by-hostname \
     --value "win.*" \
     --value-regex \
     --export-file device.json \
     --export-overwrite

.. raw:: html

   <script id="asciicast-271486" src="https://asciinema.org/a/271486.js" async></script>
