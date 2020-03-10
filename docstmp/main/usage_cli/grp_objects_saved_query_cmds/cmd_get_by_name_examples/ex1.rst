.. include:: /main/.special.rst

Invalid Name
###############################################

This does the following:

* Throws an error listing all of the valid saved query names as the supplied names
  do not exist.

.. code:: shell

   $ axonshell devices saved-query get-by-name \
     --value "nosuchname" \
     --export-file saved_query.json \
     --export-overwrite

.. raw:: html

   <script id="asciicast-271737" src="https://asciinema.org/a/271737.js" async></script>

.. include:: notes.rst
