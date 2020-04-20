.. include:: /main/.special.rst

Adapter Regex Filter And Fields Regex Filter
###############################################

This does the following:

* Return a dictionary of where the keys are the adapter names and the values are a list
  of valid fields for the adapter.
* Only return adapters that match the regular expression ``aws`` and fields that match
  the regular expression ``ip``.

.. code:: shell

   $ axonshell devices fields --adapter-re aws --field-re ip

.. raw:: html

   <script id="asciicast-271642" src="https://asciinema.org/a/271642.js" async></script>

.. include:: notes.rst
