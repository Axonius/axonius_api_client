.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Select Fields: Valid Generic Field
###############################################

This does the following:

* Get device assets and include the ``os.type`` generic field in the response data.

.. code:: shell

   $ axonshell devices get \
     --field os.type \
     --export-file device.json \
     --export-overwrite

.. raw:: html

    <script id="asciicast-271570" src="https://asciinema.org/a/271570.js" async></script>

.. include:: notes.rst
