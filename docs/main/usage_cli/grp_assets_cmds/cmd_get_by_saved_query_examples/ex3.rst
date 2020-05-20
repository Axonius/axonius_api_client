.. include:: /main/.special.rst

.. _tagging_example:

Tag/Untag Assets Found In Query
###############################################

This does the following:

* Tag or untag assets fround in query results using --tag and --untag

.. code:: shell

   # Show number of assets currently tagged with 'unmanaged'
   $ axonshell devices count --query '(labels == regex("unmanaged", "i"))'

   # Tag assets in query
   $ axonshell devices get-by-saved-query --name 'Unmanaged Devices' --tag 'unmanaged'

   # Show new count of assets tagged with 'unmanaged'
   axonshell devices count --query '(labels == regex("unmanaged", "i"))'

   # Untag assets in query
   $ axonshell devices get-by-saved-query --name 'Unmanaged Devices' --untag 'unmanaged'

   # Show count with no assets tagged again
   axonshell devices count --query '(labels == regex("unmanaged", "i"))'

.. raw:: html

   <script id="asciicast-332437" src="https://asciinema.org/a/332437.js" async></script>

.. include:: notes.rst
