.. include:: /main/.special.rst

.. _shellhell:

Shell Quoting Rules
###############################################

Different shells (powershell, cmd, bash, zsh) have their own nested quoting rules.

This becomes important when supplying queries built from the Query Wizard in the GUI,
as the queries contain double quotes (``"``).

You can avoid having to deal with nested quoting by supplying the name of a file
containing the query via ``-qf / --query-file`` instead of supplying the query on the
command line using ``-q / --query``.

Bash, zsh
===============================================

For bash and zsh, you just need to surround the query with single quotes (``'``).

.. code::

    $ axonshell devices get --query '(adapters == "aws_adapter")'


Powershell
===============================================

For powershell, it's a little more fun. You will need to do one of the following:

* Surround the --query value with single quotes and add a
  second double quote (``""``) next to every double quote (``"``).
* Surround the --query with single quotes and add a
  backslash (``\"``) before every double quote (``"``).

.. code::

    $ axonshell devices get --query '(adapters == ""aws_adapter"")'
    $ axonshell devices get --query '(adapters == \"aws_adapter\")'

Windows Command Prompt
===============================================

For the Windows Command prompt, it's like powershell, yet different!

You will need to do one of the following:

* Surround the --query value with double quotes and add a
  second double quote (``""``) next to every double quote (``"``).
* Surround the --query with double quotes and add a
  backslash (``\"``) before every double quote (``"``).

.. code::

    $ axonshell devices get --query "(adapters == ""aws_adapter"")"
    $ axonshell devices get --query "(adapters == \"aws_adapter\")"
