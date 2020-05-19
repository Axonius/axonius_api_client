.. include:: /main/.special.rst

All Adapters And Fields Regex Filter
###############################################

This does the following:

* Return a dictionary of where the keys are the adapter names and the values are a list
  of valid fields for the adapter.
* Only return adapters fields that match the regular expression ``last`` for all adapters.

.. code:: shell

   $ axonshell devices get-fields --field-re last

.. raw:: html

   <script id="asciicast-331847" src="https://asciinema.org/a/331847.js" async></script>

.. include:: notes.rst
