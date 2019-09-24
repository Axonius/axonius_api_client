.. include:: /main/.special.rst

API Usage
###############################################

API Quickstart
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

Establish a connection
----------------------------------------------

The axonius_api_client.connect.Connect object will connect to the Axonius instance and
give you access to the API objects for devices, users, adapters, and enforcements:

.. code:: python

    import os

    import axonius_api_client as axonapi

    axonapi.cli.cli_constants.load_dotenv()

    AX_URL = os.environ["AX_URL"]
    AX_KEY = os.environ["AX_KEY"]
    AX_SECRET = os.environ["AX_SECRET"]

    ctx = axonapi.Connect(
        url=AX_URL,
        key=AX_KEY,
        secret=AX_SECRET,
    )

    ctx.start()

    devices = ctx.devices
    users = ctx.users
    adapters = ctx.adapters

With the Connect object established, now you can use the API models.

Here's a simple example to get a report of all device assets matching a query that
shows all assets seen in the last 3 days. Also include the columns for AWS device type and OS Type:

.. code:: python

   query = '(specific_data.data.last_seen >= date("NOW - 3d"))'
   fields = ["aws:aws_device_type", "os.type"]

   assets = devices.get(query=query, fields=fields)

.. todo::

   The API reference docs are not done yet. The CLI usage docs will be finished first.
