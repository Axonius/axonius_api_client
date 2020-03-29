# Release notes

## 2.3.0

Release date: 2020-02-12

### Enhancements

* API Additions (CLI support coming in 2.4.0)
  * Get the discover status
  * Start a discover
  * Stop a discover
  * Get System Settings > About tab
  * Get and update System Settings > Lifecycle Settings tab
  * Get and update System Settings > GUI Settings tab
  * Get and update System Settings > Global Settings tab
  * Get, create, update, and remove System Settings > Users
  * Get, create, update, and remove System Settings > Roles
  * Get and update Adapter > Advanced Settings
  * Get, update, and remove Instances

## 2.2.0

Release date: 2020-02-08

### Enhancements

* Added `table` as a new choice for --export-format on all `get\*` commands for devices and users. References:
  * [Export Options](https://axonius-api-client.readthedocs.io/en/latest/main/usage_cli/common_options/export.html#fr-220-1)
* Added --export-table-format on all `get*` commands for devices and users. References:
  * [Export Options](https://axonius-api-client.readthedocs.io/en/latest/main/usage_cli/common_options/export.html#fr-220-2)
* Added offline install instructions. References:
  * [Offline installs using pip](https://axonius-api-client.readthedocs.io/en/latest/main/install.html#fr-220-3)
* Re-tested against all supported operating systems, removed 2.7.x from supported versions, and added 3.8.1 to supported versions. References:
  * [Supported Python versions](https://axonius-api-client.readthedocs.io/en/latest/main/contributing.html#fr-220-4)
*  Always use post instead of get for retrieving assets.
*  Fixed code paths that were not compatible with 3.5.x.
*  Added boolean argument `generator` (default: False) to all `get*` methods for devices and user objects.

## 2.1.4

Release date: 2020-01-12

### Bug fixes

* Fixed a minor issue with text string 'False' not being recognized as
  an alternative for boolean False.
* Fixed a minor issue with selecting an adapter connection by ID.

### Enhancements

* You can now specify fields to fetch in addition to the fields defined in a
  saved-query. References:
  * [Common Options for get-by-saved-query](https://axonius-api-client.readthedocs.io/en/latest/main/usage_cli/grp_assets_cmds/cmd_get_by_saved_query.html#fr-214-5)
* You can now specify fields using regular expressions whereever fields can
  be specified.
  * [Select Fields: Using Regular Expressions Case 1](https://axonius-api-client.readthedocs.io/en/latest/main/usage_cli/common_examples/select_field_examples/ex7.html#fr-214-3)
  * [Select Fields: Using Regular Expressions Case 2](https://axonius-api-client.readthedocs.io/en/latest/main/usage_cli/common_examples/select_field_examples/ex8.html#fr-214-4)
* You can use show-config when adding new connections to see the configuration without
  being prompted.
  * [Show the settings needed for a connection in text format](https://axonius-api-client.readthedocs.io/en/latest/main/usage_cli/grp_cnx_cmds/cmd_add_examples/ex3.html#fr-214-1)
