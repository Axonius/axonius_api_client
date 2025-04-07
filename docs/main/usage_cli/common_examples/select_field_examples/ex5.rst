.. include:: /main/.special.rst

Select Fields: Multiple Fields Using Commas
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Get device assets and include the generic fields ``os.type`` and ``os.distribution``,
  and the aws adapter fields ``aws_device_type`` and ``aws_region`` in the response data.
* This uses commas to seperate the fields per adapter.

.. code:: shell

   $ axonshell devices get \
     -f os.type,os.distribution \
     -f aws:aws_device_type,aws_region \
     --export-file device.json \
     --export-overwrite

.. raw:: html

    <script id="asciicast-271576" src="https://asciinema.org/a/271576.js" async></script>

.. include:: notes.rst
