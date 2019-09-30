.. include:: /main/.special.rst

Get with query
###############################################

This does the following:

* Since a query is supplied, this will only return device assets that match the query.
* Get device assets and include the generic field ``os.type``.

.. code:: shell

   $ axonshell d get \
     -q '(specific_data.data.last_seen >= date("NOW - 3d")) and (specific_data.data.os.type == "Windows")' \
     -f os.type -xf device.json -xo

.. raw:: html

   <script id="asciicast-271581" src="https://asciinema.org/a/271581.js" async></script>

.. include:: notes.rst
