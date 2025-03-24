.. include:: /main/.special.rst
.. include:: /main/deprecation_banner.rst

.. _api_quickstart:

API Quickstart
###############################################

* Follow the :ref:`Installation` steps
* Setup the connection arguments using axonshell :ref:`tools_write_config`
* Create a baseline script using :obj:`axonius_api_client.connect.Connect`

Quick Get Assets Example
==============================================

Here's a simple example to get all device assets matching a query of:

* assets that have NOT been seen in the last 3 days
* assets seen by AWS
* assets with an OS Type of Windows

Include extra fields in addition to the default fields specified in the API:

* AWS: AWS Device Type
* OS: Type
* OS: Full OS String

.. code:: python

  >>> entries = [
  ...   {'type': 'simple', 'value': '! last_seen last_days 3'},
  ...   {'type': 'simple', 'value': 'os.type equals windows'},
  ...   {'type': 'simple', 'value': 'aws:id exists'},
  ... ]
  >>> fields = ["aws:aws_device_type", "os.type", "os.os_str"]
  >>> assets = devices.get(wiz_entries=entries, fields=fields, field_null=True)
  >>> print(devices.LAST_GET['filter'])
  not (specific_data.data.last_seen >= date("NOW - 3d")) and (specific_data.data.os.type == "Windows") and ((adapters_data.aws_adapter.id == ({"$exists":true,"$ne":""})))
  >>> len(assets)
  5
  >>> j(list(assets[0]))
  [
    "adapter_list_length",
    "adapters",
    "adapters_data.aws_adapter.aws_device_type",
    "internal_axon_id",
    "labels",
    "specific_data.data.hostname",
    "specific_data.data.name",
    "specific_data.data.network_interfaces.ips",
    "specific_data.data.network_interfaces.mac",
    "specific_data.data.os.os_str",
    "specific_data.data.os.type",
    "specific_data.data.last_seen"
  ]

More examples
==============================================

.. note::
   Look in the ``axonius_api_client.examples`` directory for proof of concept example scripts

Adapters
----------------------------------------------

* Adapters: :obj:`axonius_api_client.api.adapters.adapters.Adapters`
* Adapter connections: :obj:`axonius_api_client.api.adapters.cnx.Cnx`

Assets
----------------------------------------------

* Device assets: :obj:`axonius_api_client.api.assets.devices.Devices`
* User assets: :obj:`axonius_api_client.api.assets.users.Users`
* Saved queries: :obj:`axonius_api_client.api.assets.saved_query.SavedQuery`
* Fields: :obj:`axonius_api_client.api.assets.fields.Fields`
* Tags: :obj:`axonius_api_client.api.assets.labels.Labels`

* Export callbacks for :meth:`axonius_api_client.api.assets.devices.Devices.get` and :meth:`axonius_api_client.api.assets.users.Users.get`:

  * If ``export`` is not supplied, see :meth:`axonius_api_client.api.asset_callbacks.base.Base.args_map`.
  * If ``export`` equals ``json``, see :meth:`axonius_api_client.api.asset_callbacks.base_json.Json.args_map`.
  * If ``export`` equals ``csv``, see :meth:`axonius_api_client.api.asset_callbacks.base_csv.Csv.args_map`.
  * If ``export`` equals ``json_to_csv``, see :meth:`axonius_api_client.api.asset_callbacks.base_json_to_csv.JsonToCsv.args_map`.
  * If ``export`` equals ``table``, see :meth:`axonius_api_client.api.asset_callbacks.base_table.Table.args_map`.
  * If ``export`` equals ``xlsx``, see :meth:`axonius_api_client.api.asset_callbacks.base_xlsx.Xlsx.args_map`.

* Query wizards:

  * For python objects: :obj:`axonius_api_client.api.wizards.wizard.Wizard`
  * For CSV files: :obj:`axonius_api_client.api.wizards.wizard_csv.WizardCsv`
  * For text files: :obj:`axonius_api_client.api.wizards.wizard_text.WizardText`

Enforcements and Actions
----------------------------------------------

* Enforcements: :obj:`axonius_api_client.api.enforcements.enforcements.Enforcements`
* Enforcement Actions: :obj:`axonius_api_client.api.enforcements.actions.RunAction`

System
----------------------------------------------

* Dashboards and discovery cycles: :obj:`axonius_api_client.api.system.dashboard.Dashboard`
* Initial Signup: :obj:`axonius_api_client.api.system.signup.Signup`
* Instances: :obj:`axonius_api_client.api.system.instances.Instances`
* Meta Data: :obj:`axonius_api_client.api.system.meta.Meta`
* System Roles: :obj:`axonius_api_client.api.system.system_roles.SystemRoles`
* System Settings - Global Settings: :obj:`axonius_api_client.api.system.settings_global.SettingsGlobal`
* System Settings - GUI Settings: :obj:`axonius_api_client.api.system.settings_gui.SettingsGui`
* System Settings - Lifecyle Settings: :obj:`axonius_api_client.api.system.settings_lifecycle.SettingsLifecycle`
* System Users: :obj:`axonius_api_client.api.system.system_users.SystemUsers`
