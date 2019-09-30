.. include:: /main/.special.rst

Report On Missing Adapters
###############################################

This does the following:

* Get an asset by hostname and add the missing* fields to the asset data.

.. code:: shell

   $ axonshell devices get-by-hostname -v WIN-76F9735PMOJ | \
     axonshell devices reports missing-adapters -xf report.json -xo

.. raw:: html

   <script id="asciicast-271725" src="https://asciinema.org/a/271725.js" async></script>

.. include:: notes.rst
