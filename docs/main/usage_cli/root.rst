.. include:: /main/.special.rst

root
###############################################

This is the root group of axonshell (aka running the script with no arguments).

Command Groups
===============================================

The entry point for axonshell has the following command groups:

* :doc:`grp_adapters` Commands to work with adapters and connections.
* :doc:`grp_devices`: Commands to work with device assets.
* :doc:`grp_tools`: Commands that provide extra functionality for the CLI.
* :doc:`grp_users`: Commands to work with user assets.

Options
===============================================

The entry point for the command line interface provides a number of options, all of
which must be supplied before any other arguments.

Example of proper ordering:

.. code::

    $ axonshell --proxy "https://proxy:443" devices get

Example of improper ordering:

.. code::

    $ axonshell devices get --proxy "https://proxy:443"

SSL Certificate Validation Options
------------------------------------------------

* Define a certificate file or CA bundle to use to verify the SSL certicate offered
  by the Axonius instance:
  :option:`axonshell -cp / --certpath PATH <axonshell --certpath>`
* Enable validation of the SSL certificate offered by the Axonius instance:
  :option:`axonshell -cv / --certverify PATH <axonshell --certverify>`
* Disable certificate validation warnings:
  :option:`axonshell -ncw / --no-certwarn PATH <axonshell --no-certwarn>`

.. note::

   If --certpath is supplied, --certverify is automatically set to True.

   If --certverify is supplied and --certpath is not and the certificate of the Axonius
   instance is self-signed, axonshell will exit with an error when attempting to connect.

   If you want to turn off the warnings that are shown for self-signed certificates,
   use --no-certwarn.

Proxy Options
------------------------------------------------

* Define a proxy to use when connecting to the Axonius instance:
  :option:`axonshell -p / --proxy PROXY <axonshell --proxy>`

.. note::

    A proxy can be supplied numerous ways as per the `requests documentation`_

    Examples:

    .. code::

       $ # proxy that does not require authentication
       $ axonshell --proxy https://host:port

       $ # proxy that requires authentication
       $ axonshell --proxy https://username:password@host:port

       $ # socks proxy
       $ axonshell --proxy socks5://username:password@host:port

Logging Options
------------------------------------------------

Logging to the Console
************************************************

* Enable logging to the console using STDERR:
  :option:`axonshell -c / --log-console <axonshell --log-console>`
* Console logging level:
  :option:`axonshell -lvlcon / --log-level-console LEVEL <axonshell --log-level-console>`

.. note::

  --log-level-console controls the overall level of logs displayed on the console.

  For instance:

  .. code::

     $ # This will only display INFO log entries and above
     $ # DEBUG log entries will not show up in the console log
     $ axonshell --log-console --log-level-console info --log-level-package debug

Logging to a File
************************************************

* Enable logging to a file:
  :option:`axonshell -f / --log-file <axonshell --log-file>`
* Control the file logging is sent to:
  :option:`axonshell -fn / --log-file-name <axonshell --log-file-name>`
* Control the directory file logging is sent to:
  :option:`axonshell -fp / --log-file-path <axonshell --log-file-path>`
* Control the size in MB that will cause a log to roll over:
  :option:`axonshell -fmb / --log-file-max-mb <axonshell --log-file-max-mb>`
* Control how many rolled over logs are saved:
  :option:`axonshell -fmf / --log-file-max-files <axonshell --log-file-max-files>`
* File logging level:
  :option:`axonshell -lvlfile / --log-level-file LEVEL <axonshell --log-level-file>`

.. note::

   --log-level-file controls the overall level of logs sent to --log-file-name.

   For instance:

   .. code::

      $ # This will only display INFO log entries and above
      $ # DEBUG log entries will not show up in the log file
      $ axonshell --log-file \
                  --log-level-file info \
                  --log-level-package debug

      $ # only send WARNING and above to console and DEBUG and above to file
      $ axonshell --log-console \
                  --log-console-level warning \
                  --log-file \
                  --log-level-file debug

Logging Levels
-----------------------------------------------

Control the logging levels for each component of the API client.

* Package logging level:
  :option:`axonshell -lvlpkg / --log-level-package LEVEL <axonshell --log-level-package>`
* API logging level:
  :option:`axonshell -lvlapi / --log-level-api LEVEL <axonshell --log-level-api>`
* Authentication logging level:
  :option:`axonshell -lvlauth / --log-level-auth LEVEL <axonshell --log-level-auth>`
* HTTP client logging level:
  :option:`axonshell -lvlhttp / --log-level-http LEVEL <axonshell --log-level-http>`

.. note::

   --log-level-package will override the levels for all other settings.
   It's best to leave this at the lowest level (DEBUG) and set other logging levels higher.

   --log-level-api controls the level of logs displayed from Users, Devices, Adapters,
   and Enforcement API objects.

Controlling HTTP Client Debug Messages
-----------------------------------------------

Enable more verbose logging of the HTTP client requests and responses.
These options are useful for debugging purposes.

* Log request bodies at DEBUG level:
  :option:`axonshell -reqbody / --log-request-body <axonshell --log-request-body>`
* Log request attributes in brief form at DEBUG level:
  :option:`axonshell -reqb / --log-request-attrs-brief <axonshell --log-request-attrs-verbose>`
* Log request attributes in verbose form at DEBUG level:
  :option:`axonshell -reqv --log-request-attrs-verbose <axonshell --log-request-attrs-verbose>`
* Log response bodies at DEBUG level:
  :option:`axonshell -respbody / --log-response-body <axonshell --log-response-body>`
* Log response attributes in brief form at DEBUG level:
  :option:`axonshell -respb / --log-response-attrs-brief <axonshell --log-response-attrs-verbose>`
* Log response attributes in verbose form at DEBUG level:
  :option:`axonshell -respv --log-response-attrs-verbose <axonshell --log-response-attrs-verbose>`

.. note::

   None of these will show if the overall logging level of
   --log-level-console, --log-level-file, --log-level-http, or --log-level-package
   is set to higher than DEBUG.

   By default, attributes or bodies for requests or responses are logged.

Controlling Error Wrapping
----------------------------------------------

* Disable the error wrapping performed by the CLI by default:
  :option:`axonshell -nw / --no-wraperror <axonshell --no-wraperror>`

.. note::

   This is useful for debugging as it allows you to see the full traceback of the
   exception, instead of just the string representation of the exception.

Help Page
==============================================

.. click:: axonius_api_client.cli:cli
   :prog: axonshell


.. _requests documentation: https://2.python-requests.org/en/master/user/advanced/#proxies


