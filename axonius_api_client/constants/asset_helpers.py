"""Constants for helping translate."""
import dataclasses
import typing as t
from ..data import BaseData


@dataclasses.dataclass(frozen=True)
class AssetsHelper(BaseData):
    """Helper for translating between GUI paths and API paths."""

    gui_path: t.List[str] = dataclasses.field(default_factory=list)
    saved_query_path: t.List[str] = dataclasses.field(default_factory=list)
    get_assets_path: t.List[str] = dataclasses.field(default_factory=list)
    complexity: str = ""
    description: str = ""
    example_description: str = ""
    example: t.Any = None

    @staticmethod
    def join_path(values: t.List[str]) -> str:
        """Join a list of strings with ' => '"""
        return " => ".join(values)

    def __str__(self) -> str:
        items: t.List[str] = [
            f"GUI_PATH='{self.join_path(self.gui_path)}'",
            f"SAVED_QUERY_PATH='{self.join_path(self.saved_query_path)}'",
            f"GET_ASSETS_PATH='{self.join_path(self.get_assets_path)}'",
        ]
        return ", ".join(items)


@dataclasses.dataclass(frozen=True)
class AssetsHelpers(BaseData):
    """Map of helpers."""

    fields: AssetsHelper = dataclasses.field(default_factory=AssetsHelper)
    excluded_adapters: AssetsHelper = dataclasses.field(default_factory=AssetsHelper)
    asset_excluded_adapters: AssetsHelper = dataclasses.field(default_factory=AssetsHelper)
    asset_filters: AssetsHelper = dataclasses.field(default_factory=AssetsHelper)
    field_filters: AssetsHelper = dataclasses.field(default_factory=AssetsHelper)


FIELDS = AssetsHelper(
    gui_path=["Assets Table", "Columns"],
    saved_query_path=["view", "query", "fields"],
    get_assets_path=["fields"],
    description="Fields (aka columns) to return in the results",
    complexity="dictionary that is unnecessarily complex",
    example_description="selecting 2 columns",
    example={"fields": {"devices": ["specific_data.data.name", "specific_data.data.hostname"]}},
)

EXCLUDED_ADAPTERS = AssetsHelper(
    gui_path=[
        "Assets Table",
        "Column Filters",
        "Field values - refine by adapter connection",
    ],
    saved_query_path=["view", "colExcludeAdapters"],
    get_assets_path=["excluded_adapters"],
    description="Sub-section in Column filters for a column in the Assets table",
    complexity="list of dictionaries that are moderately complex",
    example_description="selecting one adapter and one adapter connection",
    example={
        "excluded_adapters": [
            {
                "fieldPath": "specific_data.data.name",
                "exclude": ["csv_adapter6430513283efc7336d1f9fb4", "active_directory_adapter"],
            }
        ]
    },
)

ASSET_EXCLUDED_ADAPTERS = AssetsHelper(
    gui_path=[
        "Assets Table",
        "Column Filters",
        "Asset entities - refine by adapter connection",
    ],
    saved_query_path=["view", "assetExcludeAdapters"],
    get_assets_path=["asset_excluded_adapters"],
    description="Sub-section in Column filters for a column in the Assets table",
    complexity="list of dictionaries that are moderately complex",
    example_description="selecting one adapter and one adapter connection",
    example={
        "asset_excluded_adapters": [
            {
                "fieldPath": "specific_data.data.name",
                "exclude": {
                    "csv_adapter": ["6430513283efc7336d1f9fb4"],
                    "active_directory_adapter": [],
                },
            }
        ]
    },
)

ASSET_FILTERS = AssetsHelper(
    gui_path=["Assets Table", "Column Filters", "Asset entities - refine by condition"],
    saved_query_path=["view", "assetConditionExpressions"],
    get_assets_path=["asset_filters"],
    description="Sub-section in Column filters for a column in the Assets table",
    complexity="list of dictionaries that are extremely complex, query wizard",
    example_description="too complex for full example, see GUI via chrome devtools",
    example={"asset_filters": [{"fieldPath": "specific_data.data.name", "columnFilter": {}}]},
)

FIELD_FILTERS = AssetsHelper(
    gui_path=[
        "Assets Table",
        "Column Filters",
        "Field values - refine by condition",
    ],
    saved_query_path=["view", "colFilters"],
    get_assets_path=["field_filters"],
    description="Sub-section in Column filters for a column in the Assets table",
    complexity="list of dictionaries that are extremely complex, query wizard",
    example_description="too complex for full example, see GUI via chrome devtools",
    example={"field_filters": [{"fieldPath": "specific_data.data.name", "columnFilter": {}}]},
)

ASSETS_HELPERS = AssetsHelpers(
    fields=FIELDS,
    excluded_adapters=EXCLUDED_ADAPTERS,
    asset_excluded_adapters=ASSET_EXCLUDED_ADAPTERS,
    asset_filters=ASSET_FILTERS,
    field_filters=FIELD_FILTERS,
)
