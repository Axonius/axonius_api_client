.. include:: /main/.special.rst

Delete with no options
###############################################

.. include:: /main/deprecation_banner.rst

This will throw an error because we didn't supply --force.

.. code:: shell

   $ # add a csv connection that we can delete
   $ axonshell a c a -a csv -c user_id=dvcs_from_axonshell -c csv=/demo/dvc.csv -npo

   $ axonshell adapters get --name csv | \
     axonshell adapters cnx get --id dvcs_from_axonshell | \
     axonshell adapters cnx delete

.. raw:: html

   <script id="asciicast-270864" src="https://asciinema.org/a/270864.js" async></script>
