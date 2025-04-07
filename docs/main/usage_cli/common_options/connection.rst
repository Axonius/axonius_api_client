.. include:: /main/.special.rst

.. _connection_options:

Connection Options
###############################################

.. include:: /main/deprecation_banner.rst

All commands have a standard set of required options for connecting to an
instance of Axonius:

.. envvar:: AX_URL="<URL>"

   The URL of the Axonius instance set as an environment variable.

.. envvar:: AX_KEY="<KEY>"

   The API key of an Axonius user set as an environment variable.

.. envvar:: AX_SECRET="<SECRET>"

   The API secret of an Axonius user set as an environment variable.

.. option:: -u <URL>, --url <URL>

   The URL of the Axonius instance supplied as command line arguments.

.. option:: -k <KEY>, --key <KEY>

   The API key of an Axonius user supplied as command line arguments.

.. option:: -s <SECRET>, --secret <SECRET>

   The API secret of an Axonius user supplied as command line arguments.

.. seealso::

   :ref:`axtokens` to get the values for AX_KEY and AX_SECRET.

Using .env
===============================================

This is the preferred method for supplying these options. There is even a
:ref:`tools_write_config` command that writes this file for you.

Since axonshell uses the `dotenv`_ package, if a :magenta:`.env` file exists in the
current working directory, axonshell will load that file and treat the
variables defined there-in as if they were set as environment variables in the
current shell session.

All options used by all commands are able to be stored in this file.

If you define the URL, API key, and API secret options in this file,
you won't have to supply them on the command line or as environment variables
in the current shell session:

.. code::

    $ echo "AX_URL=x" >> .env
    $ echo "AX_KEY=x" >> .env
    $ echo "AX_SECRET=x" >> .env
    $ chmod 600 .env

You can also override the location of the :magenta:`.env` file by setting the
:blue:`AX_ENV` environment variable:

.. code::

    $ AX_ENV=/path/to/.env axonshell devices labels get

Using Environment Variables
===============================================

This is not the safest practice as the API key and secret will be stored in your
command line history and people looking over your shoulder can see the values.

Using inline variables:

.. code::

    $ AX_URL="x" AX_KEY="x" AX_SECRET="x" axonshell devices labels get

Using exported variables:

.. code::

    $ export AX_URL="x" AX_KEY="x" AX_SECRET="x"
    $ axonshell devices labels get

Using shell profile (similar to using .env file):

.. code::

    $ echo 'export AX_URL="x" AX_KEY="x" AX_SECRET="x"' >> ~/.zshrc

    $ # reload the zsh profile or open a new shell session
    $ . ~/.zshrc

    $ axonshell devices labels get

Using Command Line Arguments
===============================================

This is not the safest practice as the API key and secret will be stored in your
command line history and people looking over your shoulder can see the values.

.. code::

    $ axonshell devices labels get --url "x" --key "x" --secret "x"

Using Prompts
===============================================

This is the most secure way to provide the API key and API secret as the input you
provide will not be echoed to the terminal.

Using this method has a number of downsides:

* It will prompt you every time you run axonshell for these values (which is annoying).
* You won't be able to automate running axonshell using a shell script.
* You won't be able to pipe output from one sub-command to another.

Example of prompts:

.. raw:: html

    <script id="asciicast-270180" src="https://asciinema.org/a/270180.js" async></script>

.. _dotenv: https://github.com/theskumar/python-dotenv
