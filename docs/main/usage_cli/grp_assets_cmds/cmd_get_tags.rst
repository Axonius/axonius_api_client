.. include:: /main/.special.rst

devices/users get-tags
###############################################

This allows you to get all of the current tags in the system for devices or users.

.. seealso::

    :ref:`tagging_example` for how to tag and untag based on saved queries.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.
* There are no export options for this command since it only a simple list of known labels.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_get_tags_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_assets.cmd_get_tags:cmd
   :prog: axonshell devices/users get-tags
