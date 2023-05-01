# -*- coding: utf-8 -*-
"""Containers for API Endpoint definitions."""
import dataclasses
import typing as t

from ..data import BaseData
from . import json_api
from .api_endpoint import ApiEndpoint


class ApiEndpointGroup(BaseData):
    """Container for API endpoint definitions."""

    @classmethod
    def get_subgroups(cls, recursive: bool = False) -> t.Dict[str, "ApiEndpointGroup"]:
        """Get all subgroups defined in this group."""
        groups: t.Dict[str, "ApiEndpointGroup"] = {
            x.name: x.default for x in cls.get_fields() if isinstance(x.default, ApiEndpointGroup)
        }
        if recursive:
            for group_name, group in list(groups.items()):
                for subgroup_name, subgroup in group.get_subgroups(recursive=recursive).items():
                    groups[f"{group_name}.{subgroup_name}"] = subgroup
        return groups

    @classmethod
    def get_endpoints(cls, recursive: bool = False) -> t.Dict[str, ApiEndpoint]:
        """Get all endpoints defined in this group."""
        endpoints: t.Dict[str, ApiEndpoint] = {
            x.name: x.default for x in cls.get_fields() if isinstance(x.default, ApiEndpoint)
        }
        if recursive:
            for group_name, group in cls.get_subgroups(recursive=recursive).items():
                for endpoint_name, endpoint in group.get_endpoints(recursive=recursive).items():
                    endpoints[f"{group_name}.{endpoint_name}"] = endpoint
        return endpoints

    def __str__(self):
        """Pass."""
        items: t.List[str] = [
            f"endpoints={list(self.get_endpoints())}",
            f"subgroups={list(self.get_subgroups())}",
        ]
        items: str = ", ".join(items)
        return f"{self.__class__.__name__}({items})"

    def __repr__(self):
        """Pass."""
        return self.__str__()


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class DashboardSpaces(ApiEndpointGroup):
    """Container for all API endpoints for working with dashboard spaces."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/dashboard",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.dashboard_spaces.SpacesDetailsSchema,
        response_model_cls=json_api.dashboard_spaces.SpacesDetails,
    )

    get_single: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/dashboard/{uuid}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.dashboard_spaces.SpaceChartsSchema,
        response_model_cls=json_api.dashboard_spaces.SpaceCharts,
    )

    export_chart_csv: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/dashboard/charts/{uuid}/csv?sort_by=&sort_order=",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )

    export_spaces: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/dashboard/export",
        request_schema_cls=json_api.dashboard_spaces.ExportSpacesRequestSchema,
        request_model_cls=json_api.dashboard_spaces.ExportSpacesRequest,
        response_schema_cls=None,
        response_model_cls=None,
    )

    import_spaces: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/dashboard/import",
        request_schema_cls=json_api.dashboard_spaces.ImportSpacesRequestSchema,
        request_model_cls=json_api.dashboard_spaces.ImportSpacesRequest,
        response_schema_cls=json_api.dashboard_spaces.ImportSpacesResponseSchema,
        response_model_cls=json_api.dashboard_spaces.ImportSpacesResponse,
    )

    get_exportable_space_names: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/dashboard/list_spaces",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.dashboard_spaces.ExportableSpacesResponseSchema,
        response_model_cls=json_api.dashboard_spaces.ExportableSpacesResponse,
    )


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class Assets(ApiEndpointGroup):
    """Container for all API endpoints for working with assets."""

    get: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/{asset_type}",
        request_schema_cls=json_api.assets.AssetRequestSchema,
        request_model_cls=json_api.assets.AssetRequest,
        response_schema_cls=None,
        response_model_cls=json_api.assets.AssetsPage,
    )
    # PBUG: include_notes=True ignored if fields are specified

    get_by_id: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/{asset_type}/{internal_axon_id}",
        request_schema_cls=json_api.assets.AssetByIdRequestSchema,
        request_model_cls=json_api.assets.AssetByIdRequest,
        response_schema_cls=json_api.assets.AssetByIdSchema,
        response_model_cls=json_api.assets.AssetById,
        request_as_none=True,
    )
    # loose model!

    count: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/{asset_type}/count",
        request_schema_cls=json_api.assets.CountRequestSchema,
        request_model_cls=json_api.assets.CountRequest,
        response_schema_cls=json_api.assets.CountSchema,
        response_model_cls=json_api.assets.Count,
    )
    # PBUG: returns None until celery finished, want a blocking return until celery returns

    fields: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/{asset_type}/fields",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.assets.FieldsSchema,
        response_model_cls=json_api.assets.Fields,
    )

    destroy: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/{asset_type}/destroy",
        request_schema_cls=json_api.assets.DestroyRequestSchema,
        request_model_cls=json_api.assets.DestroyRequest,
        response_schema_cls=json_api.assets.DestroySchema,
        response_model_cls=json_api.assets.Destroy,
    )
    # PBUG: returns 403 status code "You are lacking some permissions for this request"
    # PBUG: REST API0: historical_prefix hardcoded to 'historical_users_'
    # PBUG: request not modeled

    tags_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/{asset_type}/labels",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.StrValueSchema,
        response_model_cls=json_api.generic.StrValue,
    )

    tags_get_expirable_names: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/{asset_type}/expirable_tags_names",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.StrValueSchema,
        response_model_cls=json_api.generic.StrValue,
    )

    tags_add: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/{asset_type}/labels",
        request_schema_cls=json_api.assets.ModifyTagsRequestSchema,
        request_model_cls=json_api.assets.ModifyTagsRequest,
        response_schema_cls=json_api.assets.ModifyTagsSchema,
        response_model_cls=json_api.assets.ModifyTags,
    )

    tags_remove: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/{asset_type}/labels",
        request_schema_cls=json_api.assets.ModifyTagsRequestSchema,
        request_model_cls=json_api.assets.ModifyTagsRequest,
        response_schema_cls=json_api.assets.ModifyTagsSchema,
        response_model_cls=json_api.assets.ModifyTags,
    )

    history_dates: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/dashboard/get_allowed_dates",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.assets.HistoryDatesSchema,
        response_model_cls=json_api.assets.HistoryDates,
    )

    run_enforcement: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/{asset_type}/enforce",
        request_schema_cls=json_api.assets.RunEnforcementRequestSchema,
        request_model_cls=json_api.assets.RunEnforcementRequest,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class FoldersQueries(ApiEndpointGroup):
    """Container for all API endpoints for working with folders for saved queries."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/queries/folders",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.folders.queries.FoldersSchema,
        response_model_cls=json_api.folders.queries.FoldersModel,
    )

    create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/queries/folders",
        request_schema_cls=json_api.folders.queries.CreateFolderRequestSchema,
        request_model_cls=json_api.folders.queries.CreateFolderRequestModel,
        response_schema_cls=json_api.folders.queries.CreateFolderResponseSchema,
        response_model_cls=json_api.folders.queries.CreateFolderResponseModel,
    )

    delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/queries/folders/{id}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.folders.queries.DeleteFolderResponseSchema,
        response_model_cls=json_api.folders.queries.DeleteFolderResponseModel,
    )

    rename: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/queries/folders/{id}/rename",
        request_schema_cls=json_api.folders.queries.RenameFolderRequestSchema,
        request_model_cls=json_api.folders.queries.RenameFolderRequestModel,
        response_schema_cls=json_api.folders.queries.RenameFolderResponseSchema,
        response_model_cls=json_api.folders.queries.RenameFolderResponseModel,
    )

    move: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/queries/folders/{id}/parent",
        request_schema_cls=json_api.folders.queries.MoveFolderRequestSchema,
        request_model_cls=json_api.folders.queries.MoveFolderRequestModel,
        response_schema_cls=json_api.folders.queries.MoveFolderResponseSchema,
        response_model_cls=json_api.folders.queries.MoveFolderResponseModel,
    )


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class FoldersEnforcements(ApiEndpointGroup):
    """Container for all API endpoints for working with folders for enforcements."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/enforcements_folders",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.folders.enforcements.FoldersSchema,
        response_model_cls=json_api.folders.enforcements.FoldersModel,
    )

    create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/enforcements_folders",
        request_schema_cls=json_api.folders.enforcements.CreateFolderRequestSchema,
        request_model_cls=json_api.folders.enforcements.CreateFolderRequestModel,
        response_schema_cls=json_api.folders.enforcements.CreateFolderResponseSchema,
        response_model_cls=json_api.folders.enforcements.CreateFolderResponseModel,
    )

    delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/enforcements_folders/{id}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.folders.enforcements.DeleteFolderResponseSchema,
        response_model_cls=json_api.folders.enforcements.DeleteFolderResponseModel,
    )

    rename: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/enforcements_folders/{id}/rename",
        request_schema_cls=json_api.folders.enforcements.RenameFolderRequestSchema,
        request_model_cls=json_api.folders.enforcements.RenameFolderRequestModel,
        response_schema_cls=json_api.folders.enforcements.RenameFolderResponseSchema,
        response_model_cls=json_api.folders.enforcements.RenameFolderResponseModel,
    )

    move: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/enforcements_folders/{id}/parent",
        request_schema_cls=json_api.folders.enforcements.MoveFolderRequestSchema,
        request_model_cls=json_api.folders.enforcements.MoveFolderRequestModel,
        response_schema_cls=json_api.folders.enforcements.MoveFolderResponseSchema,
        response_model_cls=json_api.folders.enforcements.MoveFolderResponseModel,
    )


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class SavedQueries(ApiEndpointGroup):
    """Container for all API endpoints for working with saved queries."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/queries/saved",
        request_schema_cls=json_api.saved_queries.SavedQueryGetSchema,
        request_model_cls=json_api.saved_queries.SavedQueryGet,
        response_schema_cls=json_api.saved_queries.SavedQuerySchema,
        response_model_cls=json_api.saved_queries.SavedQuery,
    )

    get_count: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/queries/saved/count",
        request_schema_cls=json_api.saved_queries.SavedQueryGetSchema,
        request_model_cls=json_api.saved_queries.SavedQueryGet,
        response_schema_cls=json_api.generic.IntValueSchema,
        response_model_cls=json_api.generic.IntValue,
    )

    get_tags: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/{asset_type}/views/tags",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.ListValueSchema,
        response_model_cls=json_api.generic.ListValue,
    )

    get_query_history: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/queries/history",
        request_schema_cls=json_api.saved_queries.QueryHistoryRequestSchema,
        request_model_cls=json_api.saved_queries.QueryHistoryRequest,
        response_schema_cls=json_api.saved_queries.QueryHistorySchema,
        response_model_cls=json_api.saved_queries.QueryHistory,
    )
    # PBUG: response not properly modeled

    get_run_by: ApiEndpoint = ApiEndpoint(
        method="get",
        path="/api/queries/history/run_by_options",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.ListValueSchema,
        response_model_cls=json_api.generic.ListValue,
    )

    get_run_from: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/queries/history/run_from_options",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.ListValueSchema,
        response_model_cls=json_api.generic.ListValue,
    )

    create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/queries/{asset_type}",
        request_schema_cls=json_api.saved_queries.SavedQueryCreateSchema,
        request_model_cls=json_api.saved_queries.SavedQueryCreate,
        response_schema_cls=json_api.saved_queries.SavedQuerySchema,
        response_model_cls=json_api.saved_queries.SavedQuery,
    )

    delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/queries/query/{uuid}",
        request_schema_cls=json_api.generic.PrivateRequestSchema,
        request_model_cls=json_api.generic.PrivateRequest,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
    )

    update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/queries/{uuid}",
        request_schema_cls=json_api.saved_queries.SavedQueryCreateSchema,
        request_model_cls=json_api.saved_queries.SavedQueryCreate,
        response_schema_cls=json_api.saved_queries.SavedQuerySchema,
        response_model_cls=json_api.saved_queries.SavedQuery,
    )


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class Instances(ApiEndpointGroup):
    """Container for all API endpoints for working with Axonius instances."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/instances",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.instances.InstanceSchema,
        response_model_cls=json_api.instances.Instance,
    )

    delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/instances",
        request_schema_cls=None,
        request_model_cls=json_api.instances.InstanceDeleteRequest,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model
    # TBUG: need testrail integration to automate tests

    update_attrs: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/instances",
        request_schema_cls=None,
        request_model_cls=json_api.instances.InstanceUpdateAttributesRequest,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model

    update_active: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/instances",
        request_schema_cls=None,
        request_model_cls=json_api.instances.InstanceUpdateActiveRequest,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model
    # TBUG: need testrail integration to automate tests

    factory_reset: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/factory_reset",
        request_schema_cls=json_api.instances.FactoryResetRequestSchema,
        request_model_cls=json_api.instances.FactoryResetRequest,
        response_schema_cls=json_api.instances.FactoryResetSchema,
        response_model_cls=json_api.instances.FactoryReset,
    )

    admin_script_upload_start: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/settings/configuration/upload_file",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )

    admin_script_upload_chunk: ApiEndpoint = ApiEndpoint(
        method="patch",
        path="api/settings/configuration/upload_file?patch={uuid}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )

    admin_script_execute: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/settings/configuration/execute/{uuid}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )

    get_api_version: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/api",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.StrValueSchema,
        response_model_cls=json_api.generic.StrValue,
    )

    get_api_versions: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/supported_versions",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.StrValueSchema,
        response_model_cls=json_api.generic.StrValue,
    )

    get_tunnels: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/tunnel/get_status",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=json_api.instances.Tunnel,
        response_json_error=False,
    )
    # PBUG: not modeled in any way shape or form
    # PBUG: returns string 'Tunnel is not enabled on system' if FF: enable_saas is False


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class CentralCore(ApiEndpointGroup):
    """Container for all API endpoints for working with Axonius Central Cores."""

    settings_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/central_core",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    settings_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/settings/central_core",
        request_schema_cls=json_api.central_core.CentralCoreSettingsUpdateSchema,
        request_model_cls=json_api.central_core.CentralCoreSettingsUpdate,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    restore_aws: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/settings/central_core/restore",
        request_schema_cls=json_api.central_core.CentralCoreRestoreAwsRequestSchema,
        request_model_cls=json_api.central_core.CentralCoreRestoreAwsRequest,
        response_schema_cls=json_api.central_core.CentralCoreRestoreSchema,
        response_model_cls=json_api.central_core.CentralCoreRestore,
        http_args={"response_timeout": 3600},
    )
    # PBUG: need other restore types added eventually
    # TBUG: need testrail integration to automate tests


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class SystemSettings(ApiEndpointGroup):
    """Container for all API endpoints for working with Axonius system settings."""

    # PBUG: schema differences between settings update and get
    # PBUG: no configName returned in get
    # PBUG: update request expects configName and pluginId, which is not returned by get
    # PBUG: update response returns config_name and pluginId, which are not returned by get
    settings_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/plugins/{plugin_name}/{config_name}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    settings_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/settings/plugins/{plugin_name}/{config_name}",
        request_schema_cls=json_api.system_settings.SystemSettingsUpdateSchema,
        request_model_cls=json_api.system_settings.SystemSettingsUpdate,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    feature_flags_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/plugins/gui/FeatureFlags",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.FeatureFlagsSchema,
        response_model_cls=json_api.system_settings.FeatureFlags,
    )

    meta_about: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/meta/about",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_meta.SystemMetaSchema,
        response_model_cls=None,
    )
    meta_about2: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/metadata",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
    )
    # PBUG: meta/about should return no spaces/all lowercase keys
    get_constants: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/get_constants",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
    )

    historical_sizes: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/historical_sizes",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
    )
    # PBUG: response is not jsonapi model

    file_upload: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/settings/plugins/{plugin}/upload_file",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.ApiBaseSchema,
        response_model_cls=json_api.generic.ApiBase,
        http_args_required=["files", "data"],
    )

    cert_uploaded: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/certificate/global_ssl",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
    )

    gui_cert_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/certificate/global_ssl",
        request_schema_cls=None,
        request_model_cls=json_api.system_settings.CertificateUpdateRequest,
        response_schema_cls=None,
        response_model_cls=None,
    )
    # PBUG: not modeled (not even anything, just returns "True")

    gui_cert_info: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/certificate/details",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.CertificateDetailsSchema,
        response_model_cls=json_api.system_settings.CertificateDetails,
    )

    gui_cert_reset: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/certificate/reset_to_defaults",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.BoolValueSchema,
        response_model_cls=json_api.generic.BoolValue,
    )
    # PBUG: bool value useless to return here, return cert details or something at least

    cert_settings: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/certificate/certificate_settings",
        request_schema_cls=json_api.system_settings.CertificateConfigSchema,
        request_model_cls=json_api.system_settings.CertificateConfig,
        response_schema_cls=json_api.generic.BoolValueSchema,
        response_model_cls=json_api.generic.BoolValue,
    )
    # PBUG: dicts not modeled
    # PBUG: bool value useless

    csr_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/certificate/csr",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    csr_create: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/certificate/csr",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.BoolValueSchema,
        response_model_cls=json_api.generic.BoolValue,
        http_args_required=["json"],
    )

    csr_cancel: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/certificate/cancel_csr",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.BoolValueSchema,
        response_model_cls=json_api.generic.BoolValue,
    )


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class RemoteSupport(ApiEndpointGroup):
    """Container for all API endpoints for working with remote support."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/maintenance",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.remote_support.RemoteSupportSchema,
        response_model_cls=json_api.remote_support.RemoteSupport,
    )
    # PBUG: response is not jsonapi model

    temporary_enable: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/settings/maintenance",
        request_schema_cls=json_api.remote_support.UpdateTemporaryRequestSchema,
        request_model_cls=json_api.remote_support.UpdateTemporaryRequest,
        response_schema_cls=None,
        response_model_cls=json_api.remote_support.UpdateTemporaryResponse,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model

    temporary_disable: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/settings/maintenance",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: response is not jsonapi model

    permanent_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/settings/maintenance",
        request_schema_cls=json_api.remote_support.UpdatePermanentRequestSchema,
        request_model_cls=json_api.remote_support.UpdatePermanentRequest,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model

    analytics_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/settings/maintenance",
        request_schema_cls=json_api.remote_support.UpdateAnalyticsRequestSchema,
        request_model_cls=json_api.remote_support.UpdateAnalyticsRequest,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model

    troubleshooting_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/settings/maintenance",
        request_schema_cls=json_api.remote_support.UpdateTroubleshootingRequestSchema,
        request_model_cls=json_api.remote_support.UpdateTroubleshootingRequest,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class SystemUsers(ApiEndpointGroup):
    """Container for all API endpoints for working with Axonius user accounts."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/users",
        request_schema_cls=json_api.resources.ResourcesGetSchema,
        request_model_cls=json_api.resources.ResourcesGet,
        response_schema_cls=json_api.system_users.SystemUserSchema,
        response_model_cls=json_api.system_users.SystemUser,
    )

    create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/settings/users",
        request_schema_cls=json_api.system_users.SystemUserCreateSchema,
        request_model_cls=json_api.system_users.SystemUserCreate,
        response_schema_cls=json_api.system_users.SystemUserSchema,
        response_model_cls=json_api.system_users.SystemUser,
    )

    delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/settings/users/{uuid}",
        request_schema_cls=json_api.resources.ResourceDeleteSchema,
        request_model_cls=json_api.resources.ResourceDelete,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
    )

    update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/settings/users/{uuid}",
        request_schema_cls=json_api.system_users.SystemUserUpdateSchema,
        request_model_cls=json_api.system_users.SystemUserUpdate,
        response_schema_cls=json_api.system_users.SystemUserSchema,
        response_model_cls=json_api.system_users.SystemUser,
    )


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class PasswordReset(ApiEndpointGroup):
    """Container for all API endpoints for working with password resets."""

    create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/settings/users/tokens/generate",
        request_schema_cls=None,
        request_model_cls=json_api.password_reset.CreateRequest,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model

    send: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/settings/users/tokens/notify",
        request_schema_cls=None,
        request_model_cls=json_api.password_reset.SendRequest,
        response_schema_cls=None,
        response_model_cls=json_api.password_reset.SendResponse,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model

    validate: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/users/tokens/validate/{token}",
        request_schema_cls=None,
        request_model_cls=json_api.password_reset.ValidateRequest,
        response_schema_cls=None,
        response_model_cls=json_api.password_reset.ValidateResponse,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model

    use: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/settings/users/tokens/reset",
        request_schema_cls=None,
        request_model_cls=json_api.password_reset.UseRequest,
        response_schema_cls=None,
        response_model_cls=json_api.password_reset.UseResponse,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class Tasks(ApiEndpointGroup):
    """Container for all API endpoints for working with enforcement tasks."""

    count: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/enforcements/tasks/count",
        request_schema_cls=json_api.tasks.GetTasksSchema,
        request_model_cls=json_api.tasks.GetTasks,
        response_schema_cls=json_api.generic.IntValueSchema,
        response_model_cls=json_api.generic.IntValue,
    )

    get_basic: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/enforcements/tasks",
        request_schema_cls=json_api.tasks.GetTasksSchema,
        request_model_cls=json_api.tasks.GetTasks,
        response_schema_cls=json_api.tasks.TaskBasicSchema,
        response_model_cls=json_api.tasks.TaskBasic,
    )

    get_full: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/enforcements/tasks/{uuid}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.tasks.TaskFullSchema,
        response_model_cls=json_api.tasks.TaskFull,
    )

    get_filters: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/enforcements/tasks/filters",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.tasks.TaskFiltersSchema,
        response_model_cls=json_api.tasks.TaskFilters,
    )


# PBUG: so many things wrong with this
@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class Enforcements(ApiEndpointGroup):
    """Container for all API endpoints for working with enforcements."""

    tasks: Tasks = Tasks()

    get_sets: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/enforcements",
        request_schema_cls=json_api.resources.ResourcesGetSchema,
        request_model_cls=json_api.resources.ResourcesGet,
        response_schema_cls=json_api.enforcements.EnforcementBasicSchema,
        response_model_cls=json_api.enforcements.EnforcementBasicModel,
    )

    update_description: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/enforcements/{uuid}/description",
        request_schema_cls=json_api.enforcements.UpdateDescriptionRequestSchema,
        request_model_cls=json_api.enforcements.UpdateDescriptionRequestModel,
        response_schema_cls=None,
        response_model_cls=None,
    )

    get_set: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/enforcements/{uuid}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.enforcements.EnforcementFullSchema,
        response_model_cls=json_api.enforcements.EnforcementFullModel,
    )

    delete_set: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/enforcements",
        request_schema_cls=json_api.generic.DictValueSchema,
        request_model_cls=json_api.generic.DictValue,
        response_schema_cls=json_api.generic.DeletedSchema,
        response_model_cls=json_api.generic.Deleted,
    )

    create_set: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/enforcements",
        request_schema_cls=json_api.enforcements.CreateEnforcementSchema,
        request_model_cls=json_api.enforcements.CreateEnforcementModel,
        response_schema_cls=json_api.enforcements.EnforcementFullSchema,
        response_model_cls=json_api.enforcements.EnforcementFullModel,
    )

    update_set: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/enforcements/{uuid}",
        request_schema_cls=json_api.enforcements.UpdateEnforcementRequestSchema,
        request_model_cls=json_api.enforcements.UpdateEnforcementRequestModel,
        response_schema_cls=json_api.enforcements.UpdateEnforcementResponseSchema,
        response_model_cls=json_api.enforcements.UpdateEnforcementResponseModel,
    )

    move_sets: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/enforcements/move_to_folder",
        request_schema_cls=json_api.enforcements.MoveEnforcementsRequestSchema,
        request_model_cls=json_api.enforcements.MoveEnforcementsRequestModel,
        response_schema_cls=json_api.enforcements.MoveEnforcementsResponseSchema,
        response_model_cls=json_api.enforcements.MoveEnforcementsResponseModel,
    )

    copy_set: ApiEndpoint = ApiEndpoint(
        method="POST",
        path="api/enforcements/duplicate/{uuid}",
        request_schema_cls=json_api.enforcements.CopyEnforcementSchema,
        request_model_cls=json_api.enforcements.CopyEnforcementModel,
        response_schema_cls=json_api.enforcements.EnforcementFullSchema,
        response_model_cls=json_api.enforcements.EnforcementFullModel,
    )

    get_action_types: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/enforcements/actions",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.enforcements.ActionTypeSchema,
        response_model_cls=json_api.enforcements.ActionType,
    )
    run_set_against_trigger: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/enforcements/{uuid}/trigger",
        request_schema_cls=json_api.enforcements.RunEnforcementAgainstTriggerRequestSchema,
        request_model_cls=json_api.enforcements.RunEnforcementAgainstTriggerRequestModel,
        response_schema_cls=json_api.generic.NameSchema,
        response_model_cls=json_api.generic.Name,
    )
    run_sets_against_trigger: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/enforcements/trigger",
        request_schema_cls=json_api.enforcements.RunEnforcementsAgainstTriggerRequestSchema,
        request_model_cls=json_api.enforcements.RunEnforcementsAgainstTriggerRequestModel,
        response_schema_cls=json_api.generic.ListDictValueSchema,
        response_model_cls=json_api.generic.ListDictValue,
    )


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class SystemRoles(ApiEndpointGroup):
    """Container for all API endpoints for working with Axonius roles."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/roles",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_roles.SystemRoleSchema,
        response_model_cls=json_api.system_roles.SystemRole,
    )
    # PBUG: SystemRoleSchema should return permissions schema in meta

    create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/settings/roles",
        request_schema_cls=json_api.system_roles.SystemRoleCreateSchema,
        request_model_cls=json_api.system_roles.SystemRoleCreate,
        response_schema_cls=json_api.system_roles.SystemRoleSchema,
        response_model_cls=json_api.system_roles.SystemRole,
    )

    delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/settings/roles/{uuid}",
        request_schema_cls=json_api.resources.ResourceDeleteSchema,
        request_model_cls=json_api.resources.ResourceDelete,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
        request_as_none=True,
    )

    update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/settings/roles/{uuid}",
        request_schema_cls=json_api.system_roles.SystemRoleUpdateSchema,
        request_model_cls=json_api.system_roles.SystemRoleUpdate,
        response_schema_cls=json_api.system_roles.SystemRoleSchema,
        response_model_cls=json_api.system_roles.SystemRole,
    )

    perms: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/labels",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
    )
    # PBUG: response is not jsonapi model


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class Lifecycle(ApiEndpointGroup):
    """Container for all API endpoints for working with the discover lifecycle."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/dashboard/lifecycle",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.lifecycle.LifecycleSchema,
        response_model_cls=json_api.lifecycle.Lifecycle,
    )

    start: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/settings/run_manual_discovery",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: response is not jsonapi model

    stop: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/settings/stop_research_phase",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: response is not jsonapi model


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class Adapters(ApiEndpointGroup):
    """Container for all API endpoints for working with adapters."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/adapters",
        request_schema_cls=json_api.adapters.AdaptersRequestSchema,
        request_model_cls=json_api.adapters.AdaptersRequest,
        response_schema_cls=json_api.adapters.AdapterSchema,
        response_model_cls=json_api.adapters.Adapter,
        http_args={"response_timeout": 3600},
    )
    # PBUG: REST API0: this can take forever to return with get_clients=True

    get_basic: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/adapters/list",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.adapters.AdaptersListSchema,
        response_model_cls=json_api.adapters.AdaptersList,
    )

    get_fetch_history_filters: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/adapters/history/filters",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.adapters.AdapterFetchHistoryFiltersSchema,
        response_model_cls=json_api.adapters.AdapterFetchHistoryFilters,
    )

    get_fetch_history: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/adapters/history",
        request_schema_cls=json_api.adapters.AdapterFetchHistoryRequestSchema,
        request_model_cls=json_api.adapters.AdapterFetchHistoryRequest,
        response_schema_cls=json_api.adapters.AdapterFetchHistorySchema,
        response_model_cls=json_api.adapters.AdapterFetchHistory,
        # response_schema_cls=None,
        # response_model_cls=None,
    )

    settings_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/adapters/{adapter_name}/advanced_settings",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.adapters.AdapterSettingsSchema,
        response_model_cls=json_api.adapters.AdapterSettings,
    )

    settings_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/adapters/{adapter_name}/{config_name}",
        request_schema_cls=json_api.adapters.AdapterSettingsUpdateUpdateSchema,
        request_model_cls=json_api.adapters.AdapterSettingsUpdate,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    file_upload: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/adapters/{adapter_name}/{node_id}/upload_file",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        http_args_required=["files", "data"],
    )
    # PBUG: if Content-Type is not multipart, server returns a 401/unauthorized
    # PBUG: response not modeled correctly!
    # PBUG: can get filename returned in response?

    cnx_get_labels: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/adapters/labels",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.adapters.CnxLabelsSchema,
        response_model_cls=json_api.adapters.CnxLabels,
    )

    cnx_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/adapters/{adapter_name}/connections",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=json_api.adapters.Cnxs,
    )

    cnx_create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/adapters/{adapter_name}/connections",
        request_schema_cls=json_api.adapters.CnxCreateRequestSchema,
        request_model_cls=json_api.adapters.CnxCreateRequest,
        response_schema_cls=json_api.adapters.CnxCreateSchema,
        response_model_cls=json_api.adapters.CnxCreate,
    )

    cnx_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/adapters/{adapter_name}/connections/{uuid}",
        request_schema_cls=json_api.adapters.CnxUpdateRequestSchema,
        request_model_cls=json_api.adapters.CnxUpdateRequest,
        response_schema_cls=json_api.adapters.CnxUpdateSchema,
        response_model_cls=json_api.adapters.CnxUpdate,
    )

    cnx_test: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/adapters/{adapter_name}/connections/test",
        request_schema_cls=json_api.adapters.CnxTestRequestSchema,
        request_model_cls=json_api.adapters.CnxTestRequest,
        response_schema_cls=None,
        response_model_cls=None,
    )

    cnx_delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/adapters/{adapter_name}/connections/{uuid}",
        request_schema_cls=json_api.adapters.CnxDeleteRequestSchema,
        request_model_cls=json_api.adapters.CnxDeleteRequest,
        response_schema_cls=json_api.adapters.CnxDeleteSchema,
        response_model_cls=json_api.adapters.CnxDelete,
    )
    # PBUG: returns non-conformant json str in 'client_id' key i.e.:
    # "{'client_id': 'https://10.0.0.111_test1'}"


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class Signup(ApiEndpointGroup):
    """Container for all API endpoints for working with initial signup."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/signup",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.BoolValueSchema,
        response_model_cls=json_api.generic.BoolValue,
    )

    expired: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/system/expired",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.BoolValueSchema,
        response_model_cls=json_api.generic.BoolValue,
    )

    license_status: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/license_status",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.BoolValueSchema,
        response_model_cls=json_api.generic.BoolValue,
    )

    get_indication_color: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/get_master_indication_color",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.StrValueSchema,
        response_model_cls=json_api.generic.StrValue,
    )

    get_login_options: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/get_login_options",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
    )

    perform: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/signup",
        request_schema_cls=json_api.signup.SignupRequestSchema,
        request_model_cls=json_api.signup.SignupRequest,
        response_schema_cls=json_api.signup.SignupResponseSchema,
        response_model_cls=json_api.signup.SignupResponse,
    )

    status: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/status",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.signup.SystemStatusSchema,
        response_model_cls=json_api.signup.SystemStatus,
    )


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class AuditLogs(ApiEndpointGroup):
    """Container for all API endpoints for working with audit logs."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/audit",
        request_schema_cls=json_api.audit_logs.AuditLogRequestSchema,
        request_model_cls=json_api.audit_logs.AuditLogRequest,
        response_schema_cls=json_api.audit_logs.AuditLogSchema,
        response_model_cls=json_api.audit_logs.AuditLog,
    )


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class OpenAPISpec(ApiEndpointGroup):
    """Container for all API endpoints for working with OPENAPI."""

    get_spec: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/open_api_yaml",
        request_schema_cls=None,
        request_model_cls=None,
        response_as_text=True,
        response_schema_cls=None,
        response_model_cls=None,
    )


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class DataScopes(ApiEndpointGroup):
    """Container for all API endpoints for working with data scopes."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/data_scope",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.data_scopes.DataScopeDetailsSchema,
        response_model_cls=json_api.data_scopes.DataScopeDetails,
    )

    create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/settings/data_scope",
        request_schema_cls=json_api.data_scopes.DataScopeCreateSchema,
        request_model_cls=json_api.data_scopes.DataScopeCreate,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
    )

    delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/settings/data_scope/{uuid}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
    )

    update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/settings/data_scope/{uuid}",
        request_schema_cls=json_api.data_scopes.DataScopeUpdateSchema,
        request_model_cls=json_api.data_scopes.DataScopeUpdate,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
    )


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class Account(ApiEndpointGroup):
    """Container for all API endpoints for working with Axonius accounts."""

    login: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/login",
        request_schema_cls=json_api.account.LoginRequestSchema,
        request_model_cls=json_api.account.LoginRequest,
        response_schema_cls=json_api.account.LoginResponseSchema,
        response_model_cls=json_api.account.LoginResponse,
    )

    get_current_user: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/login",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.account.CurrentUserSchema,
        response_model_cls=json_api.account.CurrentUser,
    )

    get_api_keys: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/settings/api_key",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
    )

    validate: ApiEndpoint = SystemSettings.get_constants


@dataclasses.dataclass(eq=True, frozen=True, repr=False)
class ApiEndpointsGroups(ApiEndpointGroup):
    """Container for all API endpoint groups."""

    instances: Instances = Instances()
    central_core: CentralCore = CentralCore()
    system_settings: SystemSettings = SystemSettings()
    remote_support: RemoteSupport = RemoteSupport()
    system_users: SystemUsers = SystemUsers()
    system_roles: SystemRoles = SystemRoles()
    lifecycle: Lifecycle = Lifecycle()
    adapters: Adapters = Adapters()
    signup: Signup = Signup()
    password_reset: PasswordReset = PasswordReset()
    audit_logs: AuditLogs = AuditLogs()
    enforcements: Enforcements = Enforcements()
    saved_queries: SavedQueries = SavedQueries()
    assets: Assets = Assets()
    openapi: OpenAPISpec = OpenAPISpec()
    data_scopes: DataScopes = DataScopes()
    dashboard_spaces: DashboardSpaces = DashboardSpaces()
    folders_queries: FoldersQueries = FoldersQueries()
    folders_enforcements: FoldersEnforcements = FoldersEnforcements()
    account: Account = Account()


ApiEndpoints = ApiEndpointsGroups()
