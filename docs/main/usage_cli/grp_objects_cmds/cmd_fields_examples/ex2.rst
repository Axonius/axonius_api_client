.. include:: /main/.special.rst

Adapter Regex Filter And All Fields
###############################################

This does the following:

* Return a dictionary of where the keys are the adapter names and the values are a list
  of valid fields for the adapter.
* Only return adapters that match the regular expression ``aws``.

.. code:: shell

   $ axonshell devices fields --adapter-re aws

.. raw:: html

   <script id="asciicast-271654" src="https://asciinema.org/a/271654.js" async></script>

.. include:: notes.rst
