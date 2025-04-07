.. include:: /main/.special.rst

Multiple using NOT
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Gets multiple saved queries that do NOT match a set of regular expression.

.. code:: shell

   $ axonshell devices saved-query get-by-name \
     --value "[y-z]" \
     --value "[m-n]" \
     --value-regex \
     --value-not \
     --export-file saved_query.json \
     --export-overwrite

.. raw:: html

   <script id="asciicast-271740" src="https://asciinema.org/a/271740.js" async></script>

.. include:: notes.rst
