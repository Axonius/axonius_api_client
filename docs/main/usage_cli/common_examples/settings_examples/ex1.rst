.. include:: /main/.special.rst

Viewing Sections and Sub-Sections
###############################################

.. include:: /main/deprecation_banner.rst

There are a lot of settings that can be configured for the Axonius platform.
These are seperated into three groups: ``settings-global``, ``settings-gui`` and `settings-lifecycle``.
Inside of each group, settings are split further into sections and sub-sections. So before we can work
with settings, we have to know what sections and sub-sections there are.

In this example we are going to take a look at how to find the sections and sub-sections contained in
the ``settings-global`` group.

The simplest way to view all sections and sub-sections is to ask for everything and use a program to
filter down what is returned.

.. code:: shell

    $ axonshell system settings-global get | grep "Section Name"

    - Section Name: 'global_ssl'
    - Section Name: 'certificate_verify_settings'
    - Section Name: 'ssl_trust_settings'
    - Section Name: 'csr_settings'
    - Section Name: 'proxy_settings'
    - Section Name: 'external_system_url_settings'
    - Section Name: 'password_policy_settings'
    - Section Name: 'password_reset_password'
    - Section Name: 'password_brute_force_protection'
    - Section Name: 'password_expiration_settings'
    - Section Name: 'vault_settings'
    --- Sub Section Name: 'akeyless_vault'
    --- Sub Section Name: 'aws_secrets_manager_vault'
    --- Sub Section Name: 'azure_key_vault'
    --- Sub Section Name: 'beyond_trust_vault'
    --- Sub Section Name: 'beyond_trust_password_safe_vault'
    --- Sub Section Name: 'clickstudios_passwordstate_vault'
    --- Sub Section Name: 'cyberark_vault'
    --- Sub Section Name: 'gcp_secret_manager'
    --- Sub Section Name: 'hashicorp_vault'
    --- Sub Section Name: 'manageengine_pam360_vault'
    --- Sub Section Name: 'thycotic_secret_server_vault'
    - Section Name: 'email_settings'
    --- Sub Section Name: 'smtpAuth'
    --- Sub Section Name: 'oauthAuth'
    - Section Name: 'syslog_settings'
    - Section Name: 'https_log_settings'
    - Section Name: 'opsgenie_settings'
    - Section Name: 'jira_settings'
    - Section Name: 'notifications_settings'
    --- Sub Section Name: 'notifications_disk_space_percentage'
    --- Sub Section Name: 'notifications_disk_space_gb'
    - Section Name: 'correlation_settings'
    --- Sub Section Name: 'correlation_devices_global_config'
    --- Sub Section Name: 'correlation_devices_adapters_config'
    --- Sub Section Name: 'correlation_users_global_config'
    - Section Name: 'correlation_schedule'
    - Section Name: 'reports_scheduler'
    - Section Name: 'static_analysis_settings'
    --- Sub Section Name: 'nvd_proxy_settings'
    --- Sub Section Name: 'device_location_mapping'
    --- Sub Section Name: 'mac_address_enrichment'
    --- Sub Section Name: 'enrichment_settings'
    - Section Name: 'aggregation_settings'
    - Section Name: 'vulnerabilities_settings'
    - Section Name: 'cache_settings'
    - Section Name: 'refresh_rate'
    - Section Name: 'getting_started_checklist'
    - Section Name: 'data_sync_settings'
    --- Sub Section Name: 'aws_s3_settings'
    --- Sub Section Name: 'azure_storage_settings'
    --- Sub Section Name: 'smb_settings'
    --- Sub Section Name: 'ssh_settings'
    - Section Name: 'api_settings'
    - Section Name: 'restrict_permission_assignment'
    - Section Name: 'export_csv_settings'
