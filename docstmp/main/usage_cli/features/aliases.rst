.. include:: /main/.special.rst

Command Group Aliases
###############################################

All command groups can be referenced using the most unique short name.

Single Matches
===============================================

.. code::

    $ # long names
    $ axonshell devices labels

    $ # short names
    $ axonshell d l

Multiple Matches
===============================================

.. code::

    $ # long names
    $ axonshell adapters cnx discover
    $ axonshell adapters cnx delete

    $ # short names that fail due to too many matches that start with "d"
    $ axonshell a c d

    $ # short names that will work
    $ axonshell a c di
    $ axonshell a c de
