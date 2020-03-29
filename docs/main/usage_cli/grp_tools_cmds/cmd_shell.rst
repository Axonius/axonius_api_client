.. include:: /main/.special.rst

tools shell
###############################################

This command launches a python interactive shell session.

The python session will establish a connection to the Axonius instance as a
``client`` object and instantiate the API objects for
``devices``, ``users``, and ``adapters``.

Common Options
===============================================

* :ref:`connection_options` for examples of supplying the Axonius credentials and URL.

Examples
===============================================

.. toctree::
   :maxdepth: 1
   :glob:

   cmd_shell_examples/ex*

Help Page
===============================================

.. click:: axonius_api_client.cli.grp_tools.cmd_shell:cmd
   :prog: axonshell tools shell
