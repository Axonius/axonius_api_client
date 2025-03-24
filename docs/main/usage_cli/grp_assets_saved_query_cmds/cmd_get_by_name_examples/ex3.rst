.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Multiple using Regular Expressions
###############################################

This does the following:

* Gets multiple saved queries that match a regular expression.

.. code:: shell

   $ axonshell devices saved-query get-by-name \
     --value "[y-z]" \
     --value-regex \
     --export-file saved_query.json \
     --export-overwrite

.. raw:: html

   <script id="asciicast-271739" src="https://asciinema.org/a/271739.js" async></script>

.. include:: notes.rst
