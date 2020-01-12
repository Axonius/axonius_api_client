# Release notes

## 2.1.4

Release date: 2020-01-12

### Bug fixes

* Fixed a minor issue with text string 'False' not being recognized as
  an alternative for boolean False.
* Fixed a minor issue with selecting an adapter connection by ID.

### Enhancements

* You can now specify fields to fetch in addition to the fields defined in a
  saved-query. References:
  * [Common Options for get-by-saved-query](https://axonius-api-client.readthedocs.io/en/latest/main/usage_cli/grp_objects_cmds/cmd_get_by_saved_query.html#fr-214-5)
* You can now specify fields using regular expressions whereever fields can
  be specified.
  * [Select Fields: Using Regular Expressions Case 1](https://axonius-api-client.readthedocs.io/en/latest/main/usage_cli/common_examples/select_field_examples/ex7.html#fr-214-3)
  * [Select Fields: Using Regular Expressions Case 2](https://axonius-api-client.readthedocs.io/en/latest/main/usage_cli/common_examples/select_field_examples/ex8.html#fr-214-4)
* You can use show-config when adding new connections to see the configuration without
  being prompted.
  * [Show the settings needed for a connection in text format](https://axonius-api-client.readthedocs.io/en/latest/main/usage_cli/grp_cnx_cmds/cmd_add_examples/ex3.html#fr-214-1)
