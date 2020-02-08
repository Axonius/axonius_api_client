.. include:: /main/.special.rst

.. _export_options:
.. _fr_220_1:
.. _fr_220_2:

Export Options
###############################################

Commands return their data to STDOUT in JSON format by default. You can redirect
STDOUT to a file in order to save the data.

.. code::

    $ axonshell adapters get > /tmp/example.json

    $ # or pipe the STDOUT to another command
    $ axonshell adapters get | jq '. | length'

However, almost all commands have a set of common options for controlling
the export format and output of the data returned:

.. option:: -xt <csv|json|table>, --export-format <csv|json|table>

   Set the output format to JSON (the default), CSV or table.

   .. note::

      Only user/devices commands starting with ``get`` support table format.

   .. note::
      :blue:`added table as an option in 2.2.0`

.. option:: -xtf, --export-table-format

   .. note::
      :blue:`added in 2.2.0`

  When using -xt / --export-format ``table``, this controls the type of table that is
  produced.

  The default table format is ``fancy_grid``, but the `tabulate`_ package that provides
  this functionality exposes many different table formats:

  * fancy_grid
  * github
  * grid
  * html
  * jira
  * latex
  * latex_booktabs
  * latex_raw
  * mediawiki
  * moinmoin
  * orgtbl
  * pipe
  * plain
  * presto
  * psql
  * rst
  * simple
  * textile
  * tsv
  * youtrack

  Quick example:

  .. code:: console

     $ axonshell devices get --export-format table --export-table-format html

.. option:: -xf <FILENAME>, --export-file <FILENAME>

   Send the output to this file instead of STDOUT.

   .. note::
      If you supply just a filename, it will be created in the directory supplied
      to -ep / --export-path.

      Relative paths to a file will be resolved to an absolute path under
      -xp / --export-path.

      You can also supply an absolute path to the file here and ignore the
      -xp / --export-path option entirely.

.. option:: -xp <FILEPATH>, --export-path <FILEPATH>

   When using -xf / --export-file, save it in this directory.
   Defaults to the current working directory.

.. option:: -xo , --export-overwrite

   When using -xf / --export-file, overwrite the file if it exists.

   If a file exists and this flag is not supplied, the CLI will not overwrite the file and exit with an error.

.. option:: -xd , --export-delim

   When using -xt / --export-format ``csv`` or ``table``, change the default delimiter
   used for joining multi-value cells.

   The default delimiter for multi-value cells is ``\n``.

.. _tabulate: https://github.com/astanin/python-tabulate
