.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Delete with --force
###############################################

This will delete a connection in --wait seconds (30 by default).

.. code:: shell

   $ # add a csv connection that we can delete
   $ axonshell a c a -a csv -c user_id=dvcs_from_axonshell -c csv=/demo/dvc.csv -npo

   $ axonshell adapters get --name csv | \
     axonshell adapters cnx get --id dvcs_from_axonshell | \
     axonshell adapters cnx delete --force

.. raw:: html

  <script id="asciicast-270865" src="https://asciinema.org/a/270865.js" async></script>
