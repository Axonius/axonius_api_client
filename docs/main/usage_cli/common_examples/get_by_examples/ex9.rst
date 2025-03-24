.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Find Matches With A Query Postfix
###############################################

This does the following:

* Get devices by hostname and add a filter for installed_software exists to the end
  of the query built by the command.
* This command builds a query for you, example (broken up due to length):

.. code::

   (
     specific_data.data.hostname == regex("WIN.*", "i")
   )
   and (
     (
       (
         specific_data.data.installed_software == ({"$exists":true,"$ne":[]})
       ) and specific_data.data.installed_software != []
     )
   )

* This query will now not only return assets that match ``WIN.*``, but also only assets
  that have Installed Software information.

.. code:: shell

   $ axonshell devices get-by-hostname \
     --value "WIN.*" \
     --value-regex \
     --query-post 'and (((specific_data.data.installed_software == ({"$exists":true,"$ne":[]})) and specific_data.data.installed_software != []))' \
     --export-file device.json \
     --export-overwrite

.. raw:: html

    <script id="asciicast-271564" src="https://asciinema.org/a/271564.js" async></script>

.. include:: notes.rst
