.. include:: /main/.special.rst

Select Fields: Using Regular Expressions Case 1
###############################################

.. include:: /main/deprecation_banner.rst

.. note::
   :blue:`added in 2.1.4`

This does the following:

* Get device assets and include the generic field ``os.type``. Also include all fields
  that match ``hostname`` from adapters matching ``.`` (which would match all adapters).

.. code:: shell

   $ axonshell devices get \
     -f os.type \
     -fr '.:hostname'
     --export-file device.json \
     --export-overwrite

.. raw:: html

    <script id="asciicast-293193" src="https://asciinema.org/a/293193.js" async></script>

.. note::

    If no adapter is supplied (i.e. just ``hostname`` instead of
    ``adapter_regex:hostname``), the assumed default will be ``.`` (which would match
    all adapters).

.. include:: notes.rst
