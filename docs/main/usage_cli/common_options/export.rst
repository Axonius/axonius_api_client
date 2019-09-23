.. include:: /main/.special.rst

.. _common_export_options:

Export Options
###############################################

Commands return their data to STDOUT in JSON format by default. You can redirect
this STDOUT to a file to save it:

.. code::

    $ axonshell adapters get > /tmp/example.json

However, almost all commands have a set of common options for controlling
the export format and output of the data returned:

.. option:: -xt <csv|json>, --export-format <csv|json>

   Set the output format to JSON (the default) or CSV.

.. option:: -xf <FILENAME>, --export-file <FILENAME>

   Send the output to this file instead of STDERR.

   If you supply just a filename, it will be created in the directory supplied to -ep / --export-path.

   You can also supply an absolute path to the file and ignore the -xp / --export-path option.

.. option:: -xp <FILEPATH>, --export-path <FILEPATH>

   When using -xf / --export-file, save it in this directory.
   Defaults to the current working directory.

.. option:: -xo , --export-overwrite

   Overwrite -xf / --export-file if it exists.

   If a file exists and this flag is not supplied, the CLI will not overwrite the file and exit with an error.
