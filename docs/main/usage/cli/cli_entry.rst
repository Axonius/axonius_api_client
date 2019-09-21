CLI Entry Point
###############################################

The entry point for the command line interface provides a number of options that allow you to control:
* The logging levels for each component of the API client.
* Enabling logging output to console or file.
* Enabling logging of the HTTP request and response bodies and attributes.
* Defining a proxy to use when connecting to the Axonius instance.
* Defining a certificate file to use in order to verify the SSL certificate offered by the Axonius instance.
* Enabling certificate verification.
* Disabling certificate verification warnings.
* Disabling the error wrapping performed by the CLI by default, which will expose the underlying exception tracebacks.

Ordering of options
===============================================

All of the options in the entry point must be supplied before any command or group.

Good Ordering

.. code::

    $ axonshell --proxy "https://proxy:443" devices get

Bad Ordering

.. code::

    $ axonshell devices get --proxy "https://proxy:443"

Help Output
###############################################

.. click:: axonius_api_client.cli:cli
   :prog: axonshell
