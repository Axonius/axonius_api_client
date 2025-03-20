.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

With Query Using File
###############################################

This does the following:

* Since a query is supplied, this will only return the count of device assets that match the query.
* To avoid dealing with nested quoting and escapes in shells, we store the query in a
  file and supply that to --query-file.

.. code:: shell

   $ axonshell devices count --query-file query.txt

.. raw:: html

   <script id="asciicast-331828" src="https://asciinema.org/a/331828.js" async></script>

.. include:: notes.rst
