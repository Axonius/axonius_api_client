.. include:: /main/.special.rst

Select Fields: Using Regular Expressions Case 2
###############################################

.. note::
   :blue:`added in 2.1.4`

This does the following:

* Get device assets and include the generic field ``os.type``. Also include all fields
  that contain ``name`` from adapters matching ``generic`` (aka the aggregated data).

.. code:: shell

   $ axonshell devices get \
     --field os.type \
     --field-regex 'generic:name' \
     --export-file device.json \
     --export-overwrite

.. raw:: html

    <script id="asciicast-293194" src="https://asciinema.org/a/293194.js" async></script>

.. note::

    If no adapter is supplied (i.e. just ``hostname`` instead of
    ``adapter_regex:hostname``), the assumed default will be ``.`` (which would match
    all adapters).

.. include:: notes.rst
