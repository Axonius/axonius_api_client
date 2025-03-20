.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Adapter Regex Filter And Fields Regex Filter
###############################################

This does the following:

* Return a list where the keys are the adapter names and the values are
  valid fields for the adapter.
* Only return adapters that match the regular expression ``aws`` and fields that match
  the regular expression ``ip``.

.. code:: shell

   $ axonshell devices get-fields --adapter-re aws --field-re ip

.. raw:: html

   <script id="asciicast-331846" src="https://asciinema.org/a/331846.js" async></script>

.. include:: notes.rst
