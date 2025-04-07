.. include:: /main/.special.rst

Autocompletion
###############################################

.. include:: /main/deprecation_banner.rst

Since axonshell is built using `click`_, there is automatic support for bash and zsh `autocompletion`_.

Bash
===============================================

.. code::

    $ echo 'eval "$(_AXONSHELL_COMPLETE=source axonshell)"' >> ~/.bashrc

Zsh
===============================================

.. code::

    $ echo 'eval "$(_AXONSHELL_COMPLETE=source_zsh axonshell)"' >> ~/.zshrc

Example of setting up autocomplete in a single shell session:

.. raw:: html

    <script id="asciicast-270176" src="https://asciinema.org/a/270176.js" async></script>

.. _click: https://click.palletsprojects.com
.. _autocompletion: https://click.palletsprojects.com/bashcomplete
