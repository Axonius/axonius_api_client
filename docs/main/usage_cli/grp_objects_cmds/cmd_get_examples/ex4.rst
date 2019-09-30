.. include:: /main/.special.rst

With Query File And All Fields
###############################################

This does the following:

* Since a query is supplied, this will only return device assets that match the query.
* To avoid dealing with nested quoting and escapes in shells, we store the query in a
  file and supply that to --query-file.
* Get device assets and include all fields for all adapters.

.. code:: shell

   $ cat query.txt
   $ axonshell d get -qf query.txt -f all -xf device.json -xo

.. raw:: html

   <script id="asciicast-271584" src="https://asciinema.org/a/271584.js" async></script>

.. include:: notes.rst

.. warning::

   Getting all fields is a very heavy call and should be used sparingly.
   It can take 2 to 5 times longer to fetch assets when including all fields!

.. note::

   The data returned by all fields is too complex for CSV format. You will see a column
   named ``specific_data`` that just says:
   ``Data of type list is too complex for CSV format``
