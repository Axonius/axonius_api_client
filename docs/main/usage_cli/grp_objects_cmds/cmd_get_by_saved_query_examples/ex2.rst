.. include:: /main/.special.rst

Valid Name
###############################################

This does the following:

* Return the assets of the query and the fields defined in the saved query
  ``SSH Open To Entire Internet``.

.. code:: shell

   $ axonshell devices get-by-saved-query \
     -n "SSH Open To Entire Internet" \
     -xf device.json -xo

.. raw:: html

   <script id="asciicast-271659" src="https://asciinema.org/a/271659.js" async></script>

.. include:: notes.rst
