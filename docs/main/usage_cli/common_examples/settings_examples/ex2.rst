.. include:: /main/.special.rst

Viewing Section and Sub-Section Values
###############################################

.. include:: /main/deprecation_banner.rst

Now that we know how to see all the sections and sub-sections we can work with. Lets take a
look at one and see how it is currently configured. For this example, lets take a look at
``email_settings``. This section contains sub-sections for ``smtpAuth`` and oauthAuth``.

.. code:: shell

    $ axonshell system settings-global get | grep "Section Name"

    ...
    - Section Name: 'email_settings'
    --- Sub Section Name: 'smtpAuth'
    --- Sub Section Name: 'oauthAuth'
    ...

To take a look at how it is currently configured, we can run another simple command that will output
the current settings in ``text`` format.

.. code:: shell

    $ axonshell system settings-global get-section --section "email_settings"

    - Section Name: 'email_settings'
    - Section Title: Global Settings: Email Settings

        Name: enabled
        Title: Send emails
        Type: 'bool'
        Value: enabled=True

        Name: smtpHost
        Title: Email host
        Type: 'string'
        Value: smtpHost='services.axonius.lan'

        Name: smtpPort
        Title: Port
        Type: 'integer'
        Value: smtpPort=25

        Name: conditional
        Title: SMTP Authentication type
        Type: 'string'
        Value: conditional='smtpAuth'

        Name: smtpAuth
        Title: Smtpauth
        Type: 'array'
        Value: smtpAuth={'smtpPassword': None, 'smtpUser': None}

        Name: oauthAuth
        Title: Oauthauth
        Type: 'array'
        Value: oauthAuth={'smtpAuthEmail': None, 'smtpClientID': None, 'smtpClientSecret': None, 'smtpRefreshToken': None, 'smtpoAuthURL': None}

        Name: use_ssl
        Title: Use SSL for connection
        Type: 'string'
        Value: use_ssl='Unencrypted'

        Name: ca_file
        Title: CA file
        Type: 'file'
        Value: ca_file=None

        Name: cert_file
        Title: Certificate file
        Type: 'file'
        Value: cert_file=None

        Name: private_key
        Title: Private key file
        Type: 'file'
        Value: private_key=None

        Name: sender_address
        Title: Sender address
        Type: 'string'
        Value: sender_address=None

        Name: compress_email_attachments
        Title: Compress email attachments
        Type: 'bool'
        Value: compress_email_attachments=False

    --- Sub Section Name: 'smtpAuth'
    --- Sub Section Title: Global Settings: Email Settings: Smtpauth

          Name: smtpUser
          Title: User name
          Type: 'string'
          Value: smtpUser=None

          Name: smtpPassword
          Title: Password
          Type: 'string'
          Value: smtpPassword=None

    --- Sub Section Name: 'oauthAuth'
    --- Sub Section Title: Global Settings: Email Settings: Oauthauth

          Name: smtpAuthEmail
          Title: OAuth authentication email
          Type: 'string'
          Value: smtpAuthEmail=None

          Name: smtpClientID
          Title: OAuth client ID
          Type: 'string'
          Value: smtpClientID=None

          Name: smtpClientSecret
          Title: OAuth client secret
          Type: 'string'
          Value: smtpClientSecret=None

          Name: smtpRefreshToken
          Title: OAuth refresh token
          Type: 'string'
          Value: smtpRefreshToken=None

          Name: smtpoAuthURL
          Title: OAuth URL
          Type: 'string'
          Value: smtpoAuthURL=None

Like most of our commands, we provide multiple formats to work with the data in. By default viewing settings defaults
to ``text`` mode as stated above but we can easily change that.

.. code:: shell

    $ axonshell system settings-global get-section --section "email_settings" \
      --export-format json-config

    {
      "ca_file": null,
      "cert_file": null,
      "compress_email_attachments": false,
      "conditional": "smtpAuth",
      "enabled": false,
      "oauthAuth": {
        "smtpAuthEmail": null,
        "smtpClientID": null,
        "smtpClientSecret": null,
        "smtpRefreshToken": null,
        "smtpoAuthURL": null
      },
      "private_key": null,
      "sender_address": "system@axonius.com",
      "smtpAuth": {
        "smtpPassword": null,
        "smtpUser": null
      },
      "smtpHost": null,
      "smtpPort": null,
      "use_ssl": "Unencrypted"
    }
