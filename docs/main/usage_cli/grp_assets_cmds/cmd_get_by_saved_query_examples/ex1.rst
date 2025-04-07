.. include:: /main/.special.rst

Invalid Name
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Since the saved query name is invalid, an error will be thrown listing all of the
  valid saved queries for device assets.

.. code:: shell

   $ axonshell devices get-by-saved-query --name invalid_name

.. raw:: html

   <script id="asciicast-332384" src="https://asciinema.org/a/332384.js" async></script>

.. include:: notes.rst
