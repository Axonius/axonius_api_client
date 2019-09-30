.. include:: /main/.special.rst

Select Fields: Invalid Generic Field
###############################################

This does the following:

* Raises an error that shows all of the valid generic fields because no generic
  field named ``foo`` exists.

.. code:: shell

   $ axonshell devices get \
     --field foo \
     --export-file device.json \
     --export-overwrite

.. raw:: html

    <script id="asciicast-271571" src="https://asciinema.org/a/271571.js" async></script>

.. include:: notes.rst
