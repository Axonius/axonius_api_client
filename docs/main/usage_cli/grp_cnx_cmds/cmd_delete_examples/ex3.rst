.. include:: /main/.special.rst

Delete with --force --wait 0 --delete-entities
###############################################

This will delete a connection and all of its associated entities in 0 seconds.

.. code:: shell

   $ # add a csv connection that we can delete
   $ axonshell a c a -a csv -c user_id=dvcs_from_axonshell -c csv=/demo/dvc.csv -npo

   $ axonshell adapters get --name csv | \
     axonshell adapters cnx get --id dvcs_from_axonshell | \
     axonshell adapters cnx delete --force --wait 0 --delete-entities

.. raw:: html

   <script id="asciicast-270866" src="https://asciinema.org/a/270866.js" async></script>
