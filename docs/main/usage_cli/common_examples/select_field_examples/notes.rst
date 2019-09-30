.. include:: /main/.special.rst

Notes
==========================================

.. note::

   This example uses the ``devices get`` command, but it will work for any
   ``get..`` command for the devices or users command groups with the exception of
   ``get-by-saved-query`` (which uses the fields built in to the saved query).

.. note::

   Selecting fields from a particular adapter is done by supplying an adapter name
   followed by a field name seperated by a colon, example:
   ``--field aws:aws_device_type``.

.. note::

   If no ``adapter:`` is included in the field, it is assumed you mean ``generic:``.

.. note::

   Generic fields are the fields that are under the ``General`` section in the GUI.
   These are the fields that contain all of the correlated data for an asset.
