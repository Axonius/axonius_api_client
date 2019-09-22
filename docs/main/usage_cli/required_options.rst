.. include:: /main/.special.rst

Required Options For All Commands
###############################################

All commands require the same options:

* -u/--url: The URL of the Axonius instance to connect to.
* -k/--key: The API key of a user in the Axonius instance at --url.
* -s/--secret: The API secret of a user in the Axonius instance at --url.

Supplying Required Options Using .env
===============================================

This is the preferred method for supplying these options.

Since axonshell includes the `dotenv`_ package, if a :magenta:`.env` file exists,
axonshell will load that file and treat the variables defined there-in as if they
were set as environment variables in the current shell session.

All options are able to be stored in this file, but most importantly you can
define :blue:`AX_URL`, :blue:`AX_KEY`, and :blue:`AX_SECRET` so that you do not have
to supply them in the command line arguments or as environment variables
in the current shell session:

.. code::

    $ echo "AX_URL=x" >> .env
    $ echo "AX_KEY=x" >> .env
    $ echo "AX_SECRET=x" >> .env

You can also override the location of the :magenta:`.env` file by setting the
:blue:`AX_ENV` environment variable:

.. code::

    $ AX_ENV=/path/to/.env axonshell devices labels get

.. todo::

    Create page for getting key and secret

Supplying Required Options Using Environment Variables
======================================================

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

Supplying Required Options Using Command Line Arguments
=======================================================

This is not the safest practice as the API key and secret will be stored in your
command line history and people looking over your shoulder can see the values.

.. code::

    $ axonshell devices labels get --url "x" --key "x" --secret "x"

Supplying Required Options Via Prompting
=======================================================

This is the most secure way to provide the API key and secret as the input you provide
will not be echoed to the terminal.

This method has a number of fallbacks:

* It will prompt you every time you run axonshell for these values (which is annoying).
* You won't be able to automate running axonshell using a shell script.
* You won't be able to pipe output from one sub-command to another.

Example of prompts:

.. raw:: html

    <script id="asciicast-270177" src="https://asciinema.org/a/270177.js" async></script>

.. todo::

    Refer to axonshell tools write-config


.. _dotenv: https://github.com/theskumar/python-dotenv
