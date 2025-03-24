.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

With Query
###############################################

This does the following:

* Since a query is supplied, this will only return the count of device assets that match the query.

.. code:: shell

   $ axonshell devices count --query '(specific_data.data.last_seen >= date("NOW - 3d"))'

.. raw:: html

   <script id="asciicast-331825" src="https://asciinema.org/a/331825.js" async></script>

.. include:: notes.rst
