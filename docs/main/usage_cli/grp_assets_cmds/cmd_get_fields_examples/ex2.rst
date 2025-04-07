.. include:: /main/.special.rst

Adapter Regex Filter And All Fields
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Return a list where the keys are the adapter names and the values are
  valid fields for the adapter.
* Only return adapters that match the regular expression ``aws``.

.. code:: shell

   $ axonshell devices get-fields --adapter-re aws

.. raw:: html

   <script id="asciicast-331845" src="https://asciinema.org/a/331845.js" async></script>

.. include:: notes.rst
