.. include:: /main/.special.rst

Create Saved Query
###############################################

.. include:: /main/deprecation_banner.rst

This does the following:

* Create a saved query that includes the ``os.type`` field.
* Sorts the table in the GUI by the ``os.type`` field.
* Sorts the the ``os.type`` field in ascending order.
* Apply a column filter to only show data in the ``os.type`` column that matches
  ``Windows``.
* Set the table paging size in the GUI to show 50 rows at a time.

.. code:: shell

   $ axonshell devices saved-query add \
     --name 'last seen in 2 days' \
     --query '(specific_data.data.last_seen >= date("NOW - 2d"))' \
     --field os.type \
     --sort-field os.type \
     --sort-ascending \
     --column-filter os.type=Windows \
     --gui-page-size 50 \
     --export-file saved_query.json \
     --export-overwrite

.. raw:: html

   <script id="asciicast-271730" src="https://asciinema.org/a/271730.js" async></script>

.. include:: notes.rst
