.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

devices/users get
###############################################

This allows you to get all of the assets for devices or users and export the data
to CSV or JSON.

.. seealso::

    :ref:`shellhell` for how to deal with quoting the query value in various shells.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* :ref:`export_options` for examples of exporting data in different formats and outputs.

Common Examples
===============================================

* :ref:`select_fields_ex` for examples of selecting which fields (columns) to include
  in the response.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_get_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_assets.cmd_get:cmd
   :prog: axonshell devices/users get
