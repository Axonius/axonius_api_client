.. include:: /main/.special.rst

Multiple Item Not Found
###############################################

This does the following:

* Get a device by hostname using regular expression that does not match anything.
* This will not throw an error when 0 matches are found.

.. code:: shell

   $ axonshell devices get-by-hostname \
     --value "nosuchname.*" \
     --value-regex \
     --export-file device.json \
     --export-overwrite

.. raw:: html

   <script id="asciicast-271482" src="https://asciinema.org/a/271482.js" async></script>
