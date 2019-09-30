.. include:: /main/.special.rst

With Query Using File
###############################################

This does the following:

* Since a query is supplied, this will only return the count of device assets that match the query.
* To avoid dealing with nested quoting and escapes in shells, we store the query in a
  file and supply that to --query-file.

.. code:: shell

   $ axonshell d count -qf query.txt

.. raw:: html

   <script id="asciicast-271645" src="https://asciinema.org/a/271645.js" async></script>

.. include:: notes.rst
