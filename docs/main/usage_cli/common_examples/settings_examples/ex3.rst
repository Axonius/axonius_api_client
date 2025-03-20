.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

Modifying Values
###############################################

Viewing settings is all well and good but modifying settings is even better.
You are able to modify full sections at once or individual sub-sections. In both cases they can
be updated via either command line parameters or using a json file. The related commands are ``update-section``,
``update-section-from-json``, ``update-sub-section`` and ``update-sub-section-from-json`` as seen here.

.. code:: shell

    $ axonshell system settings-global --help

    Usage: axonshell system settings-global [OPTIONS] COMMAND [ARGS]...

      Group: Global Settings.

    Options:
      --help  Show this message and exit.

    Commands:
      configure-destroy             Enable or disable dangerous API endpoints.
      get                           Get all settings.
      get-section                   Get settings for a section.
      get-sub-section               Get settings for a subsection.
      update-section                Update a section from arguments.
      update-section-from-json      Update a section from a JSON file.
      update-sub-section            Update a subsection from arguments.
      update-sub-section-from-json  Update a subsection from a JSON file.

If you are looking to update a section or sub-section using only command line parameters, one of the commands
you could use would be the ``update-sub-section`` command.

.. code:: shell

    $ axonshell system settings-global update-sub-section --help

    Usage: axonshell system settings-global update-sub-section
               [OPTIONS]

      Update a subsection from arguments.

    Options:
      -u, --url URL                   URL of an Axonius instance  [env var:
                                      AX_URL; required]
      -k, --key KEY                   API Key (or username if credentials=True) of
                                      user in an Axonius instance  [env var:
                                      AX_KEY; required]
      -s, --secret SECRET             API Secret (or password if credentials=True)
                                      of user in an Axonius instance  [env var:
                                      AX_SECRET; required]
      -xf, --export-format [json-full|json-config|str]
                                      Format of to export data in  [env var:
                                      AX_EXPORT_FORMAT; default: str]
      -se, --section TEXT             Settings section internal name (not title)
                                      [env var: AX_SECTION; required]
      -sb, --sub-section TEXT         Settings sub section internal name (not
                                      title)  [env var: AX_SUB_SECTION; required]
      -c, --config SPLIT_EQUALS       Configuration keys in the form of key=value
                                      (multiples)  [env var: AX_CONFIG]
      --help                          Show this message and exit.

Here is an example:

.. code:: shell

    $ axonshell system settings-global update-sub-section --section "email_settings" \
    --config "sender_address=no-reply@yourdomain.com"

To update a section or sub-section using json from a file you could use the ``update-sub-section-from-json`` command.

.. code:: shell

    $ axonshell system settings-global update-sub-section-from-json --help

    Usage: axonshell system settings-global update-sub-section-from-json
               [OPTIONS]

      Update a subsection from a JSON file.

    Options:
      -u, --url URL                   URL of an Axonius instance  [env var:
                                      AX_URL; required]
      -k, --key KEY                   API Key (or username if credentials=True) of
                                      user in an Axonius instance  [env var:
                                      AX_KEY; required]
      -s, --secret SECRET             API Secret (or password if credentials=True)
                                      of user in an Axonius instance  [env var:
                                      AX_SECRET; required]
      -xf, --export-format [json-full|json-config|str]
                                      Format of to export data in  [env var:
                                      AX_EXPORT_FORMAT; default: str]
      -se, --section TEXT             Settings section internal name (not title)
                                      [env var: AX_SECTION; required]
      -sb, --sub-section TEXT         Settings sub section internal name (not
                                      title)  [env var: AX_SUB_SECTION; required]
      -if, --input-file FILENAME      File to read (from path or piped via STDIN)
                                      [env var: AX_INPUT_FILE; default: -]
      --help                          Show this message and exit.

Using what you learned from the previous chapter, you could get the config for a sub-section in ``json-config`` format
and save it in a file. Then update that file to the desired configuration. So if you wanted to update the sub-section
``smtpAuth`` it would look something like this:

.. code:: shell

    $ axonshell system settings-global update-sub-section-from-json --section "email_settings" \
    --sub-section "smtpAuth" --input-file "./smtp_auth_settings.json"

Where ``smtp_auth_settings.json`` would be a file containing the json object you wanted to set that sub-section to
such as:

.. code:: shell

    {
      "smtpPassword": "example_password",
      "smtpUser": "example_user"
    }
