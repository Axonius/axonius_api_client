.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Check only working connections for an adapter
##################################################

This does the following:

* Get the AWS adapter on the master node
* Get only the working connections from the AWS adapter metadata
* Check that the working connections can reach their endpoints.

.. code:: shell

   $ axonshell adapters get --name aws | \
     axonshell adapters cnx get --no-broken | \
     axonshell adapters cnx check -xf check.json

.. raw:: html

   <script id="asciicast-270380" src="https://asciinema.org/a/270380.js" async></script>
