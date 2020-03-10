.. include:: /main/.special.rst

With Query
###############################################

This does the following:

* Since a query is supplied, this will only return the count of device assets that match the query.

.. code:: shell

   $ axonshell d count -q '(specific_data.data.last_seen >= date("NOW - 3d"))'

.. raw:: html

   <script id="asciicast-271644" src="https://asciinema.org/a/271644.js" async></script>

.. include:: notes.rst
