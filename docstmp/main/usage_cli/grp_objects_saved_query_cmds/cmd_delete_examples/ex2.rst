.. include:: /main/.special.rst

Valid Names
###############################################

This does the following:

* Deletes two saved queries after waiting 5 seconds (instead of the default of 30 seconds).

.. code:: shell

   $ axonshell devices saved-query delete \
     --name "last seen in 2 days" \
     --name "bloop" \
     --wait 5

.. raw:: html

   <script id="asciicast-271733" src="https://asciinema.org/a/271733.js" async></script>

.. include:: notes.rst
