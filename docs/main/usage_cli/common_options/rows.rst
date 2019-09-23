.. include:: /main/.special.rst

.. _rows_option:

Rows Option
###############################################

Any command that has a "-r / --rows" option expects it's input to be from
another commands output.

Showing sources
----------------------------------------------

You can view the commands that can supply input to a command with a "-r / --rows"
option by using the "-ss / --show-sources" option.

.. raw:: html

   <script id="asciicast-270384" src="https://asciinema.org/a/270384.js" async></script>

Piped input
----------------------------------------------

If "-r / --rows" is supplied as "-" (the default) the input is expected to be piped
in from STDIN.

.. raw:: html

   <script id="asciicast-270380" src="https://asciinema.org/a/270380.js" async></script>

File input
----------------------------------------------

If "-r / --rows" is anything other than "-", it must be the path to a JSON file
containing the output of one of the source commands.

.. raw:: html

   <script id="asciicast-270383" src="https://asciinema.org/a/270383.js" async></script>
