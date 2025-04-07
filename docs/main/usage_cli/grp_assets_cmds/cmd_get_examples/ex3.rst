.. include:: /main/.special.rst

With Query Using File
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Since a query is supplied, this will only return device assets that match the query.
* To avoid dealing with nested quoting and escapes in shells, we store the query in a
  file and supply that to --query-file.
* Get device assets and include the generic field ``os.type``.

.. code:: shell

   $ axonshell devices get --query-file query.txt --field os.type --max-rows 4

.. raw:: html

   <script id="asciicast-332362" src="https://asciinema.org/a/332362.js" async></script>

.. include:: notes.rst
