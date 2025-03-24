.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

With Query File And All Fields
###############################################

This does the following:

* Since a query is supplied, this will only return device assets that match the query.
* To avoid dealing with nested quoting and escapes in shells, we store the query in a
  file and supply that to --query-file.
* Get device assets and include all fields for all adapters.

.. code:: shell

   $ axonshell devices get --query-file query.txt --field all --max-rows 3

.. raw:: html

   <script id="asciicast-332363" src="https://asciinema.org/a/332363.js" async></script>

.. include:: notes.rst

.. warning::

   Getting all fields is a very heavy call and should be used sparingly.
   It can take 2 to 5 times longer to fetch assets when including all fields!

.. note::

   The data returned by all fields is too complex for CSV format. You will see a column
   named ``specific_data`` that just says:
   ``Data of type list is too complex for CSV format``
