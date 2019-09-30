.. include:: /main/.special.rst

Get Notes
==========================================

.. note::

   This example works the same for both the ``devices get`` command and the
   ``users get`` command.

.. note::

   When using CSV export, if a cells length goes beyond 32,000 characters it will
   be trimmed to 30,000 and the following text will be added at the end of the cell:
   ``...TRIMMED - 500 items over max cell length 30000``

.. note::

   If --query-file is supplied, it will override --query if that is also supplied.

.. seealso::

   :ref:`shellhell` for how to deal with quoting the --query value in various shells.
