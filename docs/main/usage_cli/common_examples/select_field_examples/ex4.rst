.. include:: /main/.special.rst

Select Fields: Multiple Fields
###############################################

This does the following:

* Get device assets and include the generic fields ``os.type`` and ``os.distribution``,
  and the aws adapter fields ``aws_device_type`` and ``aws_region`` in the response data.

.. code:: shell

   $ axonshell devices get \
     -f os.type \
     -f os.distribution \
     -f aws:aws_device_type \
     -f aws:aws_region \
     --export-file device.json \
     --export-overwrite

.. raw:: html

    <script id="asciicast-271575" src="https://asciinema.org/a/271575.js" async></script>

.. include:: notes.rst
