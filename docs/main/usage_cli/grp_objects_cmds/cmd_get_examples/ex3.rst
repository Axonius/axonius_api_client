.. include:: /main/.special.rst

With Query Using File
###############################################

This does the following:

* Since a query is supplied, this will only return device assets that match the query.
* To avoid dealing with nested quoting and escapes in shells, we store the query in a
  file and supply that to --query-file.
* Get device assets and include the generic field ``os.type``.

.. code:: shell

   $ cat query.txt
   $ axonshell d get -qf query.txt -f os.type -xf device.json -xo

.. raw:: html

   <script id="asciicast-271583" src="https://asciinema.org/a/271583.js" async></script>

.. include:: notes.rst
