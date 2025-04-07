.. include:: /main/.special.rst

Select Fields: No default fields
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Get device assets and include the generic field ``os.type``, but don't include the
  default fields defined for devices or users in the API client.

.. code:: shell

   $ axonshell devices get \
     -f os.type \
     --no-fields-default \
     --export-file device.json \
     --export-overwrite

.. raw:: html

    <script id="asciicast-271577" src="https://asciinema.org/a/271577.js" async></script>

.. include:: notes.rst
