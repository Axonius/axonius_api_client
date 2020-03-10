.. include:: /main/.special.rst

Filtering on adapter name and/or node name
###############################################

.. code:: shell

   $ # this will fail and print a list of valid adapters and nodes
   $ axonshell adapters get --name awsx

   $ # this will fail and print a list of valid adapters and nodes
   $ axonshell adapters get --name aws --node x

   $ # these will both work because aws is a valid adapter on master node
   $ axonshell adapters get --name aws --node master
   $ axonshell adapters get --name aws

.. raw:: html

   <script id="asciicast-270351" src="https://asciinema.org/a/270351.js" async></script>
