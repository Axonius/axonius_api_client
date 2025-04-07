.. include:: /main/.special.rst

Invalid Names
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Throws an error listing all of the valid saved query names as the supplied names
  do not exist.

.. code:: shell

   $ axonshell devices saved-query delete \
     --name nosuchname \
     --name otherinvalidname

.. raw:: html

   <script id="asciicast-271732" src="https://asciinema.org/a/271732.js" async></script>

.. include:: notes.rst
