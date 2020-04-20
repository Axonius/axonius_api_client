.. include:: /main/.special.rst

Add Multiple labels
###############################################

This does the following:

* Adds 2 labels to all device assets that are missing an endpoint protection platform.

.. code:: shell

   $ axonshell devices get \
     -q 'not (specific_data.data.adapter_properties == "Endpoint_Protection_Platform")' | \
     axonshell devices labels add -l missing_epp -l fixme

.. raw:: html

   <script id="asciicast-271717" src="https://asciinema.org/a/271717.js" async></script>

.. include:: notes.rst
