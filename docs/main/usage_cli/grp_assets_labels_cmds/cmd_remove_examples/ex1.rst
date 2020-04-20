.. include:: /main/.special.rst

Remove Multiple labels
###############################################

This does the following:

* Removes 2 labels from all device assets that have an endpoint protection platform.

.. code:: shell

   $ axonshell devices get \
     -q '(specific_data.data.adapter_properties == "Endpoint_Protection_Platform")' | \
     axonshell devices labels remove -l missing_epp -l fixme

.. raw:: html

   <script id="asciicast-271720" src="https://asciinema.org/a/271720.js" async></script>

.. include:: notes.rst
