.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Find Single Item - No Match Found
###############################################

This does the following:

* Get a device by hostname that does not exist.
* Throws an error because 0 matches were found.
* This command builds a query for you, example:
  ``(specific_data.data.hostname == "nosuchname")``

.. code:: shell

   $ axonshell devices get-by-hostname \
     --value nosuchname

.. raw:: html

   <script id="asciicast-271555" src="https://asciinema.org/a/271555.js" async></script>

.. include:: notes.rst
