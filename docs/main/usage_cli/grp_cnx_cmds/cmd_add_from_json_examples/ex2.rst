.. include:: /main/.special.rst

Check all connections for an adapter
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Get the AWS adapter on the master node
* Check all of the connections listed in the AWS adapter metadata but do not
  stop when a connection test fails.

.. code:: shell

   $ axonshell adapters get --name aws | \
     axonshell adapters cnx check --no-error -xf check.json

.. raw:: html

   <script id="asciicast-270387" src="https://asciinema.org/a/270387.js" async></script>
