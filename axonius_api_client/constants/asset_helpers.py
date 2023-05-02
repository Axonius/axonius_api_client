"""Constants for helping translate."""
import dataclasses
import typing as t

from ..data import BaseData


def to_json_api(value: t.Any, schema: str) -> dict:
    """Return a JSON API object."""
    return {"data": {"attributes": value, "type": schema}}


@dataclasses.dataclass(frozen=True)
class Example(BaseData):
    """Example values."""

    arg: t.Optional[t.Union[str, t.List[str]]]
    value: t.Any = None


@dataclasses.dataclass(frozen=True)
class AssetsHelper(BaseData):
    """Helper for translating between GUI paths and API paths."""

    name: str
    description: str
    example_description: str

    gui_concept: Example
    rest_api_saved_query: Example
    rest_api_get_assets: Example
    api_client_get_assets: Example
    axonshell_get_assets: Example

    @staticmethod
    def join_path(values: t.List[str]) -> str:
        """Join a list of strings with ' => '"""
        from axonius_api_client.tools import listify

        return " => ".join(listify(values))

    @property
    def gui_path(self) -> str:
        """Return a string describing the GUI path."""
        return self.join_path(self.gui_concept.arg)

    @property
    def saved_query_path(self) -> str:
        """Return a string describing the Saved Query path."""
        return self.join_path(self.rest_api_saved_query.arg)

    def to_str_short(self) -> str:
        """Return a string describing this helper."""
        items = [
            f"GUI Path: {self.gui_path}",
            f"REST API Saved Query path: {self.saved_query_path}",
            f"REST API get assets argument: {self.rest_api_get_assets.arg}",
            f"API Client get assets argument: {self.api_client_get_assets.arg}",
            f"axonshell get assets argument: {self.axonshell_get_assets.arg}",
        ]
        return ", ".join(items)

    def to_str(self) -> str:
        """Return a string describing this helper."""
        from axonius_api_client.tools import json_dump

        value: str = f"""
## {self.name}

GUI Path:

{self.gui_path}

### Description for {self.name} 

{self.description.strip()}

### Description of examples for {self.name} 

{self.example_description.strip()}

### Example of attribute in REST API Saved Query object for {self.name} 

Path to attribute in REST API Saved Query object:
{self.saved_query_path}

```json
{json_dump(self.rest_api_saved_query.value)}
```

### Example of attribute in REST API get assets object for {self.name} 

Attribute in REST API get assets object:
{self.rest_api_get_assets.arg}

```json
{json_dump(to_json_api(self.rest_api_get_assets.value, "entity_request_schema"))}
```

### Example of argument in API Client get assets method for {self.name} 

Argument to API Client get assets method:
{self.api_client_get_assets.arg}

```python
import axonius_api_client as axonapi
connect_args: dict = axonapi.get_env_connect()
client: axonapi.Connect = axonapi.Connect(**connect_args)

{self.api_client_get_assets.value.strip()}

# or client.users.get(...)
# or client.vulnerabilities.get(...)
```

### Example of argument in axonshell get assets command for {self.name} 

Argument in axonshell get assets command:
{self.axonshell_get_assets.arg}

```console
{self.axonshell_get_assets.value.strip()}
```
"""
        return value

    def __str__(self) -> str:
        return self.to_str()


@dataclasses.dataclass(frozen=True)
class AssetsHelpers(BaseData):
    """Map of helpers."""

    query: AssetsHelper
    fields: AssetsHelper
    expressions: AssetsHelper
    field_filters: AssetsHelper
    asset_filters: AssetsHelper
    excluded_adapters: AssetsHelper
    asset_excluded_adapters: AssetsHelper

    def to_str(self) -> str:
        """Get a string that describes the helpers."""
        fields: t.Tuple[dataclasses.Field, ...] = dataclasses.fields(self)
        items: t.List[str] = ["# Concepts for getting assets from the API"]
        for field in fields:
            value: AssetsHelper = getattr(self, field.name)
            items.append(value.to_str().strip())
        value: str = "\n\n".join(items)
        return value

    def __str__(self) -> str:
        return self.to_str()


class TEMPLATES:
    """Example template values."""

    NOT_IMPLEMENTED = "NOT IMPLEMENTED (but is used in get-by-saved-query)"
    QUERY = "specific_data.data.name == 'myname'"

    FIELDS = ["specific_data.data.name", "specific_data.data.hostname"]
    FIELDS_LIBRARY = ["name", "hostname"]
    FIELDS_CLI = "-f name -f hostname"

    EXPRESSIONS = [
        {
            "logicOp": "",
            "not": False,
            "leftBracket": 0,
            "field": "specific_data.data.name",
            "compOp": "contains",
            "path": "test",
            "rightBracket": 0,
            "children": [
                {
                    "expression": {
                        "field": "",
                        "compOp": "",
                        "path": None,
                        "filteredAdapters": None,
                    },
                    "condition": "",
                    "i": 0,
                }
            ],
            "fieldType": "axonius",
            "filter": '("specific_data.data.name" == regex("test", "i"))',
            "bracketWeight": 0,
        }
    ]

    EXCLUDED_ADAPTERS = [
        {
            "fieldPath": "specific_data.data.name",
            "exclude": ["csv_adapter6430513283efc7336d1f9fb4", "active_directory_adapter"],
        }
    ]

    ASSET_EXCLUDED_ADAPTERS = [
        {
            "fieldPath": "specific_data.data.name",
            "exclude": {
                "csv_adapter": ["6430513283efc7336d1f9fb4"],
                "active_directory_adapter": [],
            },
        }
    ]

    ASSET_FILTERS = [
        {
            "fieldPath": "specific_data.data.name",
            "columnFilter": {
                "filterExpressions": [
                    {
                        "logicOp": "",
                        "not": False,
                        "leftBracket": 0,
                        "field": "specific_data.data.name",
                        "compOp": "refineDataContains",
                        "path": "test",
                        "rightBracket": 0,
                        "children": [],
                        "fieldType": "axonius",
                        "filter": '("specific_data.data.name" == regexMatch("test", "i"))',
                        "bracketWeight": 0,
                    }
                ],
                "aqlExpression": '("specific_data.data.name" == regexMatch("test", "i"))',
                "fieldPath": "specific_data.data.name",
                "fieldType": "string",
                "isComplexField": False,
                "isComplexNestedField": False,
                "arrayFields": [],
                "nestedFilteredFields": [],
                "complexParentToUnwind": None,
                "complexNestedFields": [],
            },
        },
    ]

    FIELD_FILTERS = [
        {
            "fieldPath": "specific_data.data.hostname",
            "columnFilter": {
                "filterExpressions": [
                    {
                        "logicOp": "",
                        "not": False,
                        "leftBracket": 0,
                        "field": "specific_data.data.hostname",
                        "compOp": "refineDataContains",
                        "path": "s",
                        "rightBracket": 0,
                        "children": [],
                        "fieldType": "axonius",
                        "filter": '("specific_data.data.hostname" == regexMatch("s", "i"))',
                        "bracketWeight": 0,
                    }
                ],
                "aqlExpression": '("specific_data.data.hostname" == regexMatch("s", "i"))',
                "fieldPath": "specific_data.data.hostname",
                "fieldType": "string",
                "isComplexField": False,
                "isComplexNestedField": False,
                "arrayFields": [],
                "nestedFilteredFields": [],
                "complexParentToUnwind": None,
                "complexNestedFields": [],
            },
        }
    ]


QUERY = AssetsHelper(
    name="query",
    description="""
Query to filter what assets get returned.

It is an extremely complex string built by query wizard in the GUI or 
in the API Client and it is not recommended to build this string manually. 
""",
    example_description="""
Only return assets where the Asset Name field equals 'myname'
""",
    gui_concept=Example(
        arg=["Assets Table", "Query"],
    ),
    rest_api_saved_query=Example(
        arg=["view", "query", "filter"],
        value={
            "view": {"query": {"filter": TEMPLATES.QUERY}},
        },
    ),
    rest_api_get_assets=Example(
        arg="filter",
        value={"filter": TEMPLATES.QUERY},
    ),
    api_client_get_assets=Example(
        arg="query: Optional[str] = None",
        value=f"""
query: str = {TEMPLATES.QUERY!r}
result: list[dict] = client.devices.get(query=query)
""",
    ),
    axonshell_get_assets=Example(
        arg="--query/-q",
        value=f"""
axonshell devices get --query {TEMPLATES.QUERY!r} --export-path assets.json
# or axonshell users get ... 
# or axonshell vulnerabilities get ...
""",
    ),
)


FIELDS = AssetsHelper(
    name="fields",
    description="""
This allows you to select with fields (aka columns) to return for each asset. 

It is a list of strings that are the fully qualified internal field name of 
each column title shown in the GUI.

If an asset has no path for that field, that field will not be returned 
for that asset. 
""",
    example_description="""
Return the Asset Name and Hostname fields for each asset.
""",
    gui_concept=Example(
        arg=["Assets Table", "Columns"],
    ),
    rest_api_saved_query=Example(
        arg=["view", "query", "fields"],
        value={
            "view": {"query": {"fields": TEMPLATES.FIELDS}},
        },
    ),
    rest_api_get_assets=Example(
        arg="fields",
        value={"fields": TEMPLATES.FIELDS},
    ),
    api_client_get_assets=Example(
        arg="fields: Optional[list[str]] = None",
        value=f"""
fields: list[str] = {TEMPLATES.FIELDS_LIBRARY!r}
result: list[dict] = client.devices.get(fields=fields)
""",
    ),
    axonshell_get_assets=Example(
        arg="--fields/-f",
        value=f"""
axonshell devices get {TEMPLATES.FIELDS_CLI} --export-path assets.json
# or axonshell users get ... 
# or axonshell vulnerabilities get ...
""",
    ),
)


EXCLUDED_ADAPTERS = AssetsHelper(
    name="column_filter_exclude_adapters",
    description="""
This allows you to filter values for a field that are sourced from a 
specific adapter or a specific adapter connection. 

It is a list of dictionaries where each dictionary has the keys:

- fieldPath: a string with the fully qualified internal field name of the
  column title in the GUI.
- exclude: a list of strings that are either the "adapter_name" to exclude
  all connections for an adapter or the "adapter_name+connection_id" to 
  exclude a specific connection for an adapter. 
""",
    example_description="""
Do not return any values for the Asset Name field that come from any connection 
for the active_directory_adapter or the csv_adapter connection with the id of 
"6430513283efc7336d1f9fb4".
""",
    gui_concept=Example(
        arg=[
            "Assets Table",
            "Columns",
            "Column Filters",
            "Field values - refine by adapter connection",
        ],
    ),
    rest_api_saved_query=Example(
        arg=["view", "colExcludeAdapters"],
        value={"view": {"colExcludeAdapters": TEMPLATES.EXCLUDED_ADAPTERS}},
    ),
    rest_api_get_assets=Example(
        arg="excluded_adapters",
        value={"excluded_adapters": TEMPLATES.EXCLUDED_ADAPTERS},
    ),
    api_client_get_assets=Example(
        arg="excluded_adapters: Optional[list[dict]] = None",
        value=f"""
excluded_adapters: list[dict] = {TEMPLATES.EXCLUDED_ADAPTERS!r}
result: list[dict] = client.devices.get(excluded_adapters=excluded_adapters)
""",
    ),
    axonshell_get_assets=Example(
        arg=TEMPLATES.NOT_IMPLEMENTED,
        value=f"# {TEMPLATES.NOT_IMPLEMENTED}",
    ),
)

ASSET_EXCLUDED_ADAPTERS = AssetsHelper(
    name="column_filter_asset_exclude_adapters",
    description="""
This allows you to filter out asset entities that are sourced from a specific 
adapter or a specific adapter connection.

It is a list of dictionaries where each dictionary has the keys:

- fieldPath: a string with the fully qualified internal field name of 
  the column title in the GUI
- exclude: a dictionary where the keys are the adapter name and the values 
  are a list of strings that are the connection ids to exclude. If it is an 
  empty list, all connections for that adapter will be excluded.
""",
    example_description="""
Do not return any asset entities that come from the active_directory_adapter or
the csv_adapter connection with the id of "6430513283efc7336d1f9fb4".
""",
    gui_concept=Example(
        arg=[
            "Assets Table",
            "Columns",
            "Column Filters",
            "Asset entities - refine by adapter connection",
        ],
    ),
    rest_api_saved_query=Example(
        arg=["view", "assetExcludeAdapters"],
        value={"view": {"assetExcludeAdapters": TEMPLATES.ASSET_EXCLUDED_ADAPTERS}},
    ),
    rest_api_get_assets=Example(
        arg="asset_excluded_adapters",
        value={"asset_excluded_adapters": TEMPLATES.ASSET_EXCLUDED_ADAPTERS},
    ),
    api_client_get_assets=Example(
        arg="asset_exclude_adapters: Optional[list[dict]] = None",
        value=f"""
asset_exclude_adapters: list[dict] = {TEMPLATES.ASSET_EXCLUDED_ADAPTERS!r}
result: list[dict] = client.devices.get(asset_exclude_adapters=asset_exclude_adapters)
""",
    ),
    axonshell_get_assets=Example(
        arg=TEMPLATES.NOT_IMPLEMENTED,
        value=f"# {TEMPLATES.NOT_IMPLEMENTED}",
    ),
)

ASSET_FILTERS = AssetsHelper(
    name="column_filter_asset_condition",
    description="""
This allows you to filter out asset entities based on operators evaluated
against the asset's fields. 

It is a list of dictionaries where each dictionary has the keys: 

- fieldPath: a string with the fully qualified internal field name of 
  the column title shown in the GUI.
- columnFilter: a dictionary that is extremely complex and must be built by 
  the Query Wizard in the GUI - the API Client Query Wizard does not yet 
  support this concept. 
""",
    example_description="""
Do not return any asset entities that have a path for the Asset Name field 
that does not match the regular expression 'test'.
""",
    gui_concept=Example(
        arg=[
            "Assets Table",
            "Columns",
            "Column Filters",
            "Asset entities - refine by condition",
        ],
    ),
    rest_api_saved_query=Example(
        arg=["view", "assetConditionExpressions"],
        value={"view": {"assetConditionExpressions": TEMPLATES.ASSET_FILTERS}},
    ),
    rest_api_get_assets=Example(
        arg="asset_filters",
        value={"asset_filters": TEMPLATES.ASSET_FILTERS},
    ),
    api_client_get_assets=Example(
        arg="asset_filters: Optional[list[dict] = None",
        value=f"""
asset_filters: list[dict] = {TEMPLATES.ASSET_FILTERS!r}
result: list[dict] = client.devices.get(asset_filters=asset_filters))
""",
    ),
    axonshell_get_assets=Example(
        arg=TEMPLATES.NOT_IMPLEMENTED,
        value=f"# {TEMPLATES.NOT_IMPLEMENTED}",
    ),
)


FIELD_FILTERS = AssetsHelper(
    name="column_filter_field_condition",
    description="""
This allows you to filter out values for a specific field based on 
operators evaluated against the field's values.

It is a list of dictionaries where each dictionary has two keys:

- fieldPath: is a string with the fully qualified internal field name of 
  the column title shown in the GUI.
- columnFilter: is a dictionary that is extremely complex and must be 
  built by the Query Wizard in the GUI - the API Client Query Wizard does not
  yet support this concept.
""",
    example_description="""
Do not return any values for the Asset Name field that do not contain the letter 's'.
""",
    gui_concept=Example(
        arg=[
            "Assets Table",
            "Columns",
            "Column Filters",
            "Field values - refine by condition",
        ],
    ),
    rest_api_saved_query=Example(
        arg=["view", "colFilters"],
        value={"view": {"colFilters": TEMPLATES.FIELD_FILTERS}},
    ),
    rest_api_get_assets=Example(
        arg="field_filters",
        value={"field_filters": TEMPLATES.FIELD_FILTERS},
    ),
    api_client_get_assets=Example(
        arg="field_filters: Optional[list[dict]] = None",
        value=f"""
field_filters: list[dict] = {TEMPLATES.FIELD_FILTERS!r}
result: list[dict] = client.devices.get(field_filters=field_filters)
""",
    ),
    axonshell_get_assets=Example(
        arg=TEMPLATES.NOT_IMPLEMENTED,
        value=f"# {TEMPLATES.NOT_IMPLEMENTED}",
    ),
)

EXPRESSIONS = AssetsHelper(
    name="expressions",
    description="""
This is the most complex attribute of them all.

It is a list of dictionaries containing the expressions that are built
by a Query Wizard in order to construct the query. 
""",
    example_description="""
Only return assets where the Asset Name field contains the letter 'test'.
""",
    gui_concept=Example(
        arg=["Assets Table", "Query Wizard"],
    ),
    rest_api_saved_query=Example(
        arg=["view", "query", "expressions"],
        value={"view": {"query": {"expressions": TEMPLATES.EXPRESSIONS}}},
    ),
    rest_api_get_assets=Example(
        arg="expressions",
        value={"expressions": TEMPLATES.EXPRESSIONS},
    ),
    api_client_get_assets=Example(
        arg="expressions: Optional[list[dict]] = None",
        value=f"""
expressions: list[dict] = {TEMPLATES.EXPRESSIONS!r}
result: list[dict] = client.devices.get(expressions=expressions)
""",
    ),
    axonshell_get_assets=Example(
        arg=TEMPLATES.NOT_IMPLEMENTED,
        value=f"# {TEMPLATES.NOT_IMPLEMENTED}",
    ),
)


ASSETS_HELPERS = AssetsHelpers(
    query=QUERY,
    fields=FIELDS,
    excluded_adapters=EXCLUDED_ADAPTERS,
    asset_excluded_adapters=ASSET_EXCLUDED_ADAPTERS,
    asset_filters=ASSET_FILTERS,
    field_filters=FIELD_FILTERS,
    expressions=EXPRESSIONS,
)
