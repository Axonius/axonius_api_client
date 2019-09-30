.. include:: /main/.special.rst

All Adapters And Fields Regex Filter
###############################################

This does the following:

* Return a dictionary of where the keys are the adapter names and the values are a list
  of valid fields for the adapter.
* Only return adapters fields that match the regular expression ``last`` for all adapters.

.. code:: shell

   $ axonshell devices fields --field-re last

.. raw:: html

   <script id="asciicast-271656" src="https://asciinema.org/a/271656.js" async></script>

.. include:: notes.rst
