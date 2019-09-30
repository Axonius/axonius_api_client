.. include:: /main/.special.rst

With No Query
###############################################

This does the following:

* Since no query supplied, this will return ALL device assets.
* Get device assets and include the generic field ``os.type``.

.. code:: shell

   $ axonshell d get -f os.type -xf device.json -xo

.. raw:: html

   <script id="asciicast-271579" src="https://asciinema.org/a/271579.js" async></script>

.. include:: notes.rst
