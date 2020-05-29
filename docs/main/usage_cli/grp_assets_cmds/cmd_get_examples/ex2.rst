.. include:: /main/.special.rst

With Query
###############################################

This does the following:

* Since a query is supplied, this will only return device assets that match the query.
* Get device assets and include the generic field ``os.type``.

.. code:: shell

   $ axonshell devices get \
     --query '(specific_data.data.last_seen >= date("NOW - 3d")) and (specific_data.data.os.type == "Windows")' \
     --field os.type --max-rows 4

.. raw:: html

   <script id="asciicast-332359" src="https://asciinema.org/a/332359.js" async></script>

.. include:: notes.rst
