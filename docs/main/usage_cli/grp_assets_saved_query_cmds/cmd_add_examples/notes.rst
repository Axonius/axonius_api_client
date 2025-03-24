.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Notes
==========================================

.. note::

   This example works the same for both the ``devices saved-query add`` and
   ``users saved-query add`` commands.

.. note::

   Creating a saved query this way does not build the expressions that are used
   by the Query Wizard in the GUI, so you will not be able to use the Query Wizard
   to modify saved queries created by this command.

.. note::

   The only required option is -n / --name, but all of the other options can control
   the creation of the saved query in multiple ways and you probably want to at least
   supply -q / --query.
