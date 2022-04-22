# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import Dict

from ..data import BaseData
from . import json_api
from .api_endpoint import ApiEndpoint


class ApiEndpointGroup(BaseData):
    """Pass."""

    @classmethod
    def get_endpoints(cls) -> Dict[str, ApiEndpoint]:
        """Pass."""
        return {x.name: x.default for x in cls.get_fields()}

    def __str__(self):
        """Pass."""
        names = [x.name for x in self.get_fields()]
        return f"{self.__class__.__name__}(endpoints={names})"

    def __repr__(self):
        """Pass."""
        return self.__str__()


@dataclasses.dataclass(repr=False)
class Assets(ApiEndpointGroup):
    """Pass."""

    get: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/{asset_type}",
        request_schema_cls=json_api.assets.AssetRequestSchema,
        request_model_cls=json_api.assets.AssetRequest,
        response_schema_cls=None,
        response_model_cls=json_api.assets.AssetsPage,
    )
    # PBUG: include_notes=True ignored if fields are specified

    get_by_id: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/{asset_type}/{internal_axon_id}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=json_api.assets.AssetById,
    )
    # loose model!

    count: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/{asset_type}/count",
        request_schema_cls=json_api.assets.CountRequestSchema,
        request_model_cls=json_api.assets.CountRequest,
        response_schema_cls=None,
        response_model_cls=json_api.assets.Count,
    )
    # PBUG: returns None until celery finished, want a blocking return until celery returns

    fields: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/{asset_type}/fields",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
    )

    destroy: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/{asset_type}/destroy",
        request_schema_cls=None,
        request_model_cls=json_api.assets.DestroyRequest,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
    )
    # PBUG: returns 403 status code "You are lacking some permissions for this request"
    # PBUG: REST API0: historical_prefix hardcoded to 'historical_users_'
    # PBUG: request not modeled

    tags_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/{asset_type}/labels",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.StrValueSchema,
        response_model_cls=json_api.generic.StrValue,
    )

    tags_add: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/{asset_type}/labels",
        request_schema_cls=json_api.assets.ModifyTagsSchema,
        request_model_cls=json_api.assets.ModifyTags,
        response_schema_cls=json_api.generic.IntValueSchema,
        response_model_cls=json_api.generic.IntValue,
    )

    tags_remove: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/V4.0/{asset_type}/labels",
        request_schema_cls=json_api.assets.ModifyTagsSchema,
        request_model_cls=json_api.assets.ModifyTags,
        response_schema_cls=json_api.generic.IntValueSchema,
        response_model_cls=json_api.generic.IntValue,
    )

    history_dates: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/dashboard/get_allowed_dates",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.assets.HistoryDatesSchema,
        response_model_cls=json_api.assets.HistoryDates,
    )


@dataclasses.dataclass(repr=False)
class SavedQueries(ApiEndpointGroup):
    """Pass."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/{asset_type}/views/saved",
        request_schema_cls=json_api.resources.ResourcesGetSchema,
        request_model_cls=json_api.resources.ResourcesGet,
        response_schema_cls=json_api.saved_queries.SavedQuerySchema,
        response_model_cls=json_api.saved_queries.SavedQuery,
    )

    # WIP: folders
    get_folders: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.5/queries/folders",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.saved_queries.FoldersResponseSchema,
        response_model_cls=json_api.saved_queries.FoldersResponse,
    )
    # PBUG: response not properly modeled

    create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/{asset_type}/views",
        request_schema_cls=json_api.saved_queries.SavedQueryCreateSchema,
        request_model_cls=json_api.saved_queries.SavedQueryCreate,
        response_schema_cls=json_api.saved_queries.SavedQuerySchema,
        response_model_cls=json_api.saved_queries.SavedQuery,
    )

    delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/V4.0/{asset_type}/views/view/{uuid}",
        request_schema_cls=json_api.generic.PrivateRequestSchema,
        request_model_cls=json_api.generic.PrivateRequest,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
    )

    delete_4_3: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/V4.0/{asset_type}/views/view/{uuid}",
        request_schema_cls=json_api.saved_queries.SavedQueryDeleteSchema,
        request_model_cls=json_api.saved_queries.SavedQueryDelete,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
    )

    update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/{asset_type}/views/{uuid}",
        request_schema_cls=json_api.saved_queries.SavedQueryCreateSchema,
        request_model_cls=json_api.saved_queries.SavedQueryCreate,
        response_schema_cls=json_api.saved_queries.SavedQuerySchema,
        response_model_cls=json_api.saved_queries.SavedQuery,
    )


@dataclasses.dataclass(repr=False)
class Instances(ApiEndpointGroup):
    """Pass."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/instances",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.instances.InstanceSchema,
        response_model_cls=json_api.instances.Instance,
    )

    delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/V4.0/instances",
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
        path="api/V4.0/instances",
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
        path="api/V4.0/instances",
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
        path="api/V4.0/factory_reset",
        request_schema_cls=json_api.instances.FactoryResetRequestSchema,
        request_model_cls=json_api.instances.FactoryResetRequest,
        response_schema_cls=json_api.instances.FactoryResetSchema,
        response_model_cls=json_api.instances.FactoryReset,
    )

    admin_script_upload_start: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/configuration/upload_file",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )

    admin_script_upload_chunk: ApiEndpoint = ApiEndpoint(
        method="patch",
        path="api/V4.0/settings/configuration/upload_file?patch={uuid}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )

    admin_script_execute: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/configuration/execute/{uuid}",
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


@dataclasses.dataclass(repr=False)
class CentralCore(ApiEndpointGroup):
    """Pass."""

    settings_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/central_core",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    settings_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/central_core",
        request_schema_cls=json_api.central_core.CentralCoreSettingsUpdateSchema,
        request_model_cls=json_api.central_core.CentralCoreSettingsUpdate,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    restore_aws: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/settings/central_core/restore",
        request_schema_cls=json_api.central_core.CentralCoreRestoreAwsRequestSchema,
        request_model_cls=json_api.central_core.CentralCoreRestoreAwsRequest,
        response_schema_cls=json_api.central_core.CentralCoreRestoreSchema,
        response_model_cls=json_api.central_core.CentralCoreRestore,
        http_args={"response_timeout": 3600},
    )
    # PBUG: need other restore types added eventually
    # TBUG: need testrail integration to automate tests


@dataclasses.dataclass(repr=False)
class SystemSettings(ApiEndpointGroup):
    """Pass."""

    # PBUG: schema differences between settings update and get
    # PBUG: no configName returned in get
    # PBUG: update request expects configName and pluginId, which is not returned by get
    # PBUG: update response returns config_name and pluginId, which are not returned by get
    settings_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/plugins/{plugin_name}/{config_name}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    settings_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/plugins/{plugin_name}/{config_name}",
        request_schema_cls=json_api.system_settings.SystemSettingsUpdateSchema,
        request_model_cls=json_api.system_settings.SystemSettingsUpdate,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    feature_flags_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/plugins/gui/FeatureFlags",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.FeatureFlagsSchema,
        response_model_cls=json_api.system_settings.FeatureFlags,
    )

    meta_about: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/meta/about",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_meta.SystemMetaSchema,
        response_model_cls=None,
    )
    # PBUG: meta/about should return no spaces/all lowercase keys

    historical_sizes: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/historical_sizes",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
    )
    # PBUG: response is not jsonapi model

    file_upload: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/plugins/{plugin}/upload_file",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.ApiBaseSchema,
        response_model_cls=json_api.generic.ApiBase,
        http_args_required=["files", "data"],
    )

    cert_uploaded: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/certificate/global_ssl",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
    )

    gui_cert_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/certificate/global_ssl",
        request_schema_cls=None,
        request_model_cls=json_api.system_settings.CertificateUpdateRequest,
        response_schema_cls=None,
        response_model_cls=None,
    )
    # PBUG: not modeled (not even anything, just returns "True")

    gui_cert_info: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/certificate/details",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.CertificateDetailsSchema,
        response_model_cls=json_api.system_settings.CertificateDetails,
    )

    gui_cert_reset: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/certificate/reset_to_defaults",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.BoolValueSchema,
        response_model_cls=json_api.generic.BoolValue,
    )
    # PBUG: bool value useless to return here, return cert details or something at least

    cert_settings: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/certificate/certificate_settings",
        request_schema_cls=json_api.system_settings.CertificateConfigSchema,
        request_model_cls=json_api.system_settings.CertificateConfig,
        response_schema_cls=json_api.generic.BoolValueSchema,
        response_model_cls=json_api.generic.BoolValue,
    )
    # PBUG: dict's not modeled
    # PBUG: bool value useless

    csr_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/certificate/csr",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    csr_create: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/certificate/csr",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.BoolValueSchema,
        response_model_cls=json_api.generic.BoolValue,
        http_args_required=["json"],
    )

    csr_cancel: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/certificate/cancel_csr",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.BoolValueSchema,
        response_model_cls=json_api.generic.BoolValue,
    )


@dataclasses.dataclass(repr=False)
class RemoteSupport(ApiEndpointGroup):
    """Pass."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/maintenance",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.remote_support.RemoteSupportSchema,
        response_model_cls=json_api.remote_support.RemoteSupport,
    )
    # PBUG: response is not jsonapi model

    temporary_enable: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/settings/maintenance",
        request_schema_cls=json_api.remote_support.UpdateTemporaryRequestSchema,
        request_model_cls=json_api.remote_support.UpdateTemporaryRequest,
        response_schema_cls=None,
        response_model_cls=json_api.remote_support.UpdateTemporaryResponse,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model

    temporary_disable: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/V4.0/settings/maintenance",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: response is not jsonapi model

    permanent_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/maintenance",
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
        path="api/V4.0/settings/maintenance",
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
        path="api/V4.0/settings/maintenance",
        request_schema_cls=json_api.remote_support.UpdateTroubleshootingRequestSchema,
        request_model_cls=json_api.remote_support.UpdateTroubleshootingRequest,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model


@dataclasses.dataclass(repr=False)
class SystemUsers(ApiEndpointGroup):
    """Pass."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/users",
        request_schema_cls=json_api.resources.ResourcesGetSchema,
        request_model_cls=json_api.resources.ResourcesGet,
        response_schema_cls=json_api.system_users.SystemUserSchema,
        response_model_cls=json_api.system_users.SystemUser,
    )

    create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/settings/users",
        request_schema_cls=json_api.system_users.SystemUserCreateSchema,
        request_model_cls=json_api.system_users.SystemUserCreate,
        response_schema_cls=json_api.system_users.SystemUserSchema,
        response_model_cls=json_api.system_users.SystemUser,
    )

    delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/V4.0/settings/users/{uuid}",
        request_schema_cls=None,
        request_model_cls=json_api.resources.ResourceDelete,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
    )

    update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/users/{uuid}",
        request_schema_cls=json_api.system_users.SystemUserUpdateSchema,
        request_model_cls=json_api.system_users.SystemUserUpdate,
        response_schema_cls=json_api.system_users.SystemUserSchema,
        response_model_cls=json_api.system_users.SystemUser,
    )


@dataclasses.dataclass(repr=False)
class PasswordReset(ApiEndpointGroup):
    """Pass."""

    create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/settings/users/tokens/generate",
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
        path="api/V4.0/settings/users/tokens/notify",
        request_schema_cls=None,
        request_model_cls=json_api.password_reset.SendRequest,
        response_schema_cls=None,
        response_model_cls=json_api.password_reset.SendResponse,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model

    validate: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/users/tokens/validate/{token}",
        request_schema_cls=None,
        request_model_cls=json_api.password_reset.ValidateRequest,
        response_schema_cls=None,
        response_model_cls=json_api.password_reset.ValidateResponse,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model

    use: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/users/tokens/reset",
        request_schema_cls=None,
        request_model_cls=json_api.password_reset.UseRequest,
        response_schema_cls=None,
        response_model_cls=json_api.password_reset.UseResponse,
    )
    # PBUG: request is not jsonapi model
    # PBUG: response is not jsonapi model


@dataclasses.dataclass(repr=False)
class Enforcements(ApiEndpointGroup):
    """Pass."""

    # PBUG: so many things wrong with this

    get_sets: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.5/enforcements",
        request_schema_cls=json_api.resources.ResourcesGetSchema,
        request_model_cls=json_api.resources.ResourcesGet,
        response_schema_cls=json_api.enforcements.SetBasicSchema,
        response_model_cls=json_api.enforcements.SetBasic,
    )

    get_set: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.5/enforcements/{uuid}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.enforcements.SetFullSchema,
        response_model_cls=json_api.enforcements.SetFull,
    )

    delete_set: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/V4.5/enforcements",
        request_schema_cls=json_api.generic.DictValueSchema,
        request_model_cls=json_api.generic.DictValue,
        response_schema_cls=json_api.generic.DeletedSchema,
        response_model_cls=json_api.generic.Deleted,
    )

    create_set: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.5/enforcements",
        request_schema_cls=json_api.enforcements.CreateSchema,
        request_model_cls=json_api.enforcements.Create,
        response_schema_cls=json_api.enforcements.SetFullSchema,
        response_model_cls=json_api.enforcements.SetFull,
    )

    update_set: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.5/enforcements/{uuid}",
        request_schema_cls=json_api.enforcements.UpdateRequestSchema,
        request_model_cls=json_api.enforcements.UpdateRequest,
        response_schema_cls=json_api.enforcements.UpdateResponseSchema,
        response_model_cls=json_api.enforcements.UpdateResponse,
    )

    copy_set: ApiEndpoint = ApiEndpoint(
        method="POST",
        path="api/V4.5/enforcements/duplicate/{uuid}",
        request_schema_cls=json_api.enforcements.DuplicateSchema,
        request_model_cls=json_api.enforcements.Duplicate,
        response_schema_cls=json_api.enforcements.SetFullSchema,
        response_model_cls=json_api.enforcements.SetFull,
    )

    get_action_types: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.5/enforcements/actions",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.enforcements.ActionTypeSchema,
        response_model_cls=json_api.enforcements.ActionType,
    )


@dataclasses.dataclass(repr=False)
class SystemRoles(ApiEndpointGroup):
    """Pass."""

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
        request_schema_cls=None,
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


@dataclasses.dataclass(repr=False)
class Lifecycle(ApiEndpointGroup):
    """Pass."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/dashboard/lifecycle",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.lifecycle.LifecycleSchema,
        response_model_cls=json_api.lifecycle.Lifecycle,
    )

    start: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/settings/run_manual_discovery",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: response is not jsonapi model

    stop: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/settings/stop_research_phase",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        response_as_text=True,
    )
    # PBUG: response is not jsonapi model


@dataclasses.dataclass(repr=False)
class Adapters(ApiEndpointGroup):
    """Pass."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/adapters",
        request_schema_cls=json_api.adapters.AdaptersRequestSchema,
        request_model_cls=json_api.adapters.AdaptersRequest,
        response_schema_cls=json_api.adapters.AdapterSchema,
        response_model_cls=json_api.adapters.Adapter,
        http_args={"response_timeout": 3600},
    )
    # PBUG: REST API0: this can take forever to return with get_clients=True

    get_basic: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/adapters/list",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.adapters.AdaptersListSchema,
        response_model_cls=json_api.adapters.AdaptersList,
    )

    settings_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/adapters/{adapter_name}/advanced_settings",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.adapters.AdapterSettingsSchema,
        response_model_cls=json_api.adapters.AdapterSettings,
    )

    settings_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/adapters/{adapter_name}/{config_name}",
        request_schema_cls=json_api.adapters.AdapterSettingsUpdateSchema,
        request_model_cls=json_api.adapters.AdapterSettingsUpdate,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    file_upload: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/adapters/{adapter_name}/{node_id}/upload_file",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
        http_args_required=["files", "data"],
    )
    # PBUG: if Content-Type is not multipart, server returns a 401/unauthorized
    # PBUG: response not modeled correctly!
    # PBUG: can get filename returned in response?

    labels_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/adapters/labels",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.adapters.CnxLabelsSchema,
        response_model_cls=json_api.adapters.CnxLabels,
    )

    cnx_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/adapters/{adapter_name}/connections",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=json_api.adapters.Cnxs,
    )

    cnx_create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/adapters/{adapter_name}/connections",
        request_schema_cls=json_api.adapters.CnxCreateRequestSchema,
        request_model_cls=json_api.adapters.CnxCreateRequest,
        response_schema_cls=json_api.adapters.CnxModifyResponseSchema,
        response_model_cls=json_api.adapters.CnxModifyResponse,
    )

    cnx_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/adapters/{adapter_name}/connections/{uuid}",
        request_schema_cls=json_api.adapters.CnxUpdateRequestSchema,
        request_model_cls=json_api.adapters.CnxUpdateRequest,
        response_schema_cls=json_api.adapters.CnxModifyResponseSchema,
        response_model_cls=json_api.adapters.CnxModifyResponse,
    )

    cnx_test: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/adapters/{adapter_name}/connections/test",
        request_schema_cls=json_api.adapters.CnxTestRequestSchema,
        request_model_cls=json_api.adapters.CnxTestRequest,
        response_schema_cls=None,
        response_model_cls=None,
    )

    cnx_delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/V4.0/adapters/{adapter_name}/connections/{uuid}",
        request_schema_cls=json_api.adapters.CnxDeleteRequestSchema,
        request_model_cls=json_api.adapters.CnxDeleteRequest,
        response_schema_cls=json_api.adapters.CnxDeleteSchema,
        response_model_cls=json_api.adapters.CnxDelete,
    )
    # PBUG: returns non-conformant json str in 'client_id' key i.e.:
    # "{'client_id': 'https://10.0.0.111_test1'}"


@dataclasses.dataclass(repr=False)
class Signup(ApiEndpointGroup):
    """Pass."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/signup",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.generic.BoolValueSchema,
        response_model_cls=json_api.generic.BoolValue,
    )

    perform: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/signup",
        request_schema_cls=json_api.signup.SignupRequestSchema,
        request_model_cls=json_api.signup.SignupRequest,
        response_schema_cls=json_api.signup.SignupResponseSchema,
        response_model_cls=json_api.signup.SignupResponse,
    )

    status: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/status",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.signup.SystemStatusSchema,
        response_model_cls=json_api.signup.SystemStatus,
    )


@dataclasses.dataclass(repr=False)
class AuditLogs(ApiEndpointGroup):
    """Pass."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/audit",
        request_schema_cls=json_api.audit_logs.AuditLogRequestSchema,
        request_model_cls=json_api.audit_logs.AuditLogRequest,
        response_schema_cls=json_api.audit_logs.AuditLogSchema,
        response_model_cls=json_api.audit_logs.AuditLog,
    )


@dataclasses.dataclass(repr=False)
class OpenAPISpec(ApiEndpointGroup):
    """Pass."""

    get_spec: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/open_api_yaml",
        request_schema_cls=None,
        request_model_cls=None,
        response_as_text=True,
        response_schema_cls=None,
        response_model_cls=None,
    )


@dataclasses.dataclass(repr=False)
class DataScopes(ApiEndpointGroup):
    """Pass."""

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


@dataclasses.dataclass(repr=False)
class ApiEndpoints(BaseData):
    """Pass."""

    instances: ApiEndpointGroup = Instances()
    central_core: ApiEndpointGroup = CentralCore()
    system_settings: ApiEndpointGroup = SystemSettings()
    remote_support: ApiEndpointGroup = RemoteSupport()
    system_users: ApiEndpointGroup = SystemUsers()
    system_roles: ApiEndpointGroup = SystemRoles()
    lifecycle: ApiEndpointGroup = Lifecycle()
    adapters: ApiEndpointGroup = Adapters()
    signup: ApiEndpointGroup = Signup()
    password_reset: ApiEndpointGroup = PasswordReset()
    audit_logs: ApiEndpointGroup = AuditLogs()
    enforcements: ApiEndpointGroup = Enforcements()
    saved_queries: ApiEndpointGroup = SavedQueries()
    assets: ApiEndpointGroup = Assets()
    openapi: ApiEndpointGroup = OpenAPISpec()
    data_scopes: ApiEndpointGroup = DataScopes()

    @classmethod
    def get_groups(cls) -> Dict[str, ApiEndpointGroup]:
        """Pass."""
        return {x.name: x.default for x in cls.get_fields()}

    def __str__(self):
        """Pass."""
        names = [x.name for x in self.get_fields()]
        return f"{self.__class__.__name__}(groups={names})"

    def __repr__(self):
        """Pass."""
        return self.__str__()


ApiEndpoints = ApiEndpoints()
