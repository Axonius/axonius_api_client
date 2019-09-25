.. include:: /main/.special.rst

CLI Usage
###############################################

CLI Quickstart
==============================================

Install the package
-----------------------------------------------

.. code ::

   $ pip install axonius-api-client

.. seealso::

   :ref:`Installation` for more details.

Setup connection information
----------------------------------------------

.. code::

    $ echo "AX_URL=x" >> .env
    $ echo "AX_KEY=x" >> .env
    $ echo "AX_SECRET=x" >> .env
    $ chmod 600 .env

.. seealso::

   :ref:`axtokens` to get the values for AX_KEY and AX_SECRET.

   :ref:`connection_options` for more details.

Use the axonshell CLI
----------------------------------------------

After installing this package, a script called `axonshell` will be added to the scripts
directory for python.

Show the main help page:

.. code::

   $ axonshell

Show the help pages for main command groups:

.. code::

   $ axonshell devices
   $ axonshell users
   $ axonshell adapters
   $ axonshell tools

Get a report of all device assets matching a query that shows all assets seen in the last 3 days.
Also include the columns for AWS device type and OS Type:

.. code::

   $ axonshell devices \
     --query '(specific_data.data.last_seen >= date("NOW - 3d"))' \
     --field aws:aws_device_type \
     --field os.type

.. seealso::

   :ref:`main/usage_cli:cli commands` for the list of all commands across all command groups.

   :ref:`main/usage_cli:cli groups` for the list of all command groups.

CLI Common Options
==============================================

.. toctree::
   :maxdepth: 1
   :glob:

   usage_cli/common_options/*

CLI Features
==============================================

.. toctree::
   :maxdepth: 1
   :glob:

   usage_cli/features/*

CLI Groups
==============================================

.. toctree::
   :maxdepth: 1
   :glob:

   usage_cli/root.rst
   usage_cli/grp_*

CLI Commands
==============================================

.. toctree::
   :maxdepth: 1
   :glob:

   usage_cli/grp_*_cmds/cmd_*

