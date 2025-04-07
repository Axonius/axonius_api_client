.. include:: /main/.special.rst

Select Fields: Invalid Adapter
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Raises an error that shows all of the valid adapters because no adapter
  named ``foo`` exists.

.. code:: shell

   $ axonshell devices get \
     --field foo:bar \
     --export-file device.json \
     --export-overwrite

.. raw:: html

    <script id="asciicast-271573" src="https://asciinema.org/a/271573.js" async></script>

.. include:: notes.rst
