# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses

from ..data import BaseData
from . import json_api
from .api_endpoint import ApiEndpoint


@dataclasses.dataclass
class Assets(BaseData):
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
        response_schema_cls=json_api.generic.DictValueSchema,
        response_model_cls=json_api.generic.DictValue,
    )


@dataclasses.dataclass
class SavedQueries(BaseData):
    """Pass."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/{asset_type}/views/saved",
        request_schema_cls=json_api.resources.ResourcesGetSchema,
        request_model_cls=json_api.resources.ResourcesGet,
        response_schema_cls=json_api.saved_queries.SavedQuerySchema,
        response_model_cls=json_api.saved_queries.SavedQuery,
    )

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


@dataclasses.dataclass
class Instances(BaseData):
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


@dataclasses.dataclass
class CentralCore(BaseData):
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


@dataclasses.dataclass
class SystemSettings(BaseData):
    """Pass."""

    # PBUG: schema differences between settings update and get
    # PBUG: no configName returned in get
    # PBUG: update request expects configName and pluginId, which is not returned by get
    # PBUG: update response returns config_name and pluginId, which are not returned by get
    feature_flags_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/plugins/gui/FeatureFlags",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.FeatureFlagsSchema,
        response_model_cls=json_api.system_settings.FeatureFlags,
    )

    global_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/plugins/core/CoreService",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    global_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/plugins/core/CoreService",
        request_schema_cls=json_api.system_settings.SystemSettingsUpdateSchema,
        request_model_cls=json_api.system_settings.SystemSettingsGlobalUpdate,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    lifecycle_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/plugins/system_scheduler/SystemSchedulerService",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    lifecycle_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/plugins/system_scheduler/SystemSchedulerService",
        request_schema_cls=json_api.system_settings.SystemSettingsUpdateSchema,
        request_model_cls=json_api.system_settings.SystemSettingsLifecycleUpdate,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    gui_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/plugins/gui/GuiService",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    gui_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/plugins/gui/GuiService",
        request_schema_cls=json_api.system_settings.SystemSettingsUpdateSchema,
        request_model_cls=json_api.system_settings.SystemSettingsGuiUpdate,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    identity_providers_get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/plugins/gui/IdentityProviders",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    identity_providers_update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/plugins/gui/IdentityProviders",
        request_schema_cls=json_api.system_settings.SystemSettingsUpdateSchema,
        request_model_cls=json_api.system_settings.SystemSettingsIdentityProvidersUpdate,
        response_schema_cls=json_api.system_settings.SystemSettingsSchema,
        response_model_cls=json_api.system_settings.SystemSettings,
    )

    meta_about: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/meta/about",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_meta.SystemMetaSchema,
        response_model_cls=dict,
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


@dataclasses.dataclass
class RemoteSupport(BaseData):
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


@dataclasses.dataclass
class SystemUsers(BaseData):
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
        request_model_cls=json_api.system_users.SystemUser,
        response_schema_cls=json_api.system_users.SystemUserSchema,
        response_model_cls=json_api.system_users.SystemUser,
    )


@dataclasses.dataclass
class PasswordReset(BaseData):
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


@dataclasses.dataclass
class Enforcements(BaseData):
    """Pass."""

    # PBUG: so many things wrong with this

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/enforcements",
        request_schema_cls=json_api.resources.ResourcesGetSchema,
        request_model_cls=json_api.resources.ResourcesGet,
        response_schema_cls=json_api.enforcements.EnforcementDetailsSchema,
        response_model_cls=json_api.enforcements.EnforcementDetails,
    )

    get_full: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/enforcements/{uuid}",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.enforcements.EnforcementSchema,
        response_model_cls=json_api.enforcements.Enforcement,
    )

    delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/V4.0/enforcements",
        request_schema_cls=json_api.generic.DictValueSchema,
        request_model_cls=json_api.generic.DictValue,
        response_schema_cls=json_api.generic.DeletedSchema,
        response_model_cls=json_api.generic.Deleted,
    )

    create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/enforcements",
        request_schema_cls=json_api.enforcements.EnforcementCreateSchema,
        request_model_cls=json_api.enforcements.EnforcementCreate,
        response_schema_cls=json_api.enforcements.EnforcementSchema,
        response_model_cls=json_api.enforcements.Enforcement,
    )

    get_actions: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/enforcements/actions",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.enforcements.ActionSchema,
        response_model_cls=json_api.enforcements.Action,
    )


@dataclasses.dataclass
class SystemRoles(BaseData):
    """Pass."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/roles",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=json_api.system_roles.SystemRoleSchema,
        response_model_cls=json_api.system_roles.SystemRole,
    )
    # PBUG: SystemRoleSchema should return permissions schema in meta

    create: ApiEndpoint = ApiEndpoint(
        method="post",
        path="api/V4.0/settings/roles",
        request_schema_cls=json_api.system_roles.SystemRoleCreateSchema,
        request_model_cls=json_api.system_roles.SystemRoleCreate,
        response_schema_cls=json_api.system_roles.SystemRoleSchema,
        response_model_cls=json_api.system_roles.SystemRole,
    )

    delete: ApiEndpoint = ApiEndpoint(
        method="delete",
        path="api/V4.0/settings/roles/{uuid}",
        request_schema_cls=None,
        request_model_cls=json_api.resources.ResourceDelete,
        response_schema_cls=json_api.generic.MetadataSchema,
        response_model_cls=json_api.generic.Metadata,
        request_as_none=True,
    )

    update: ApiEndpoint = ApiEndpoint(
        method="put",
        path="api/V4.0/settings/roles/{uuid}",
        request_schema_cls=json_api.system_roles.SystemRoleUpdateSchema,
        request_model_cls=json_api.system_roles.SystemRole,
        response_schema_cls=json_api.system_roles.SystemRoleSchema,
        response_model_cls=json_api.system_roles.SystemRole,
    )

    perms: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/labels",
        request_schema_cls=None,
        request_model_cls=None,
        response_schema_cls=None,
        response_model_cls=None,
    )
    # PBUG: response is not jsonapi model


@dataclasses.dataclass
class Lifecycle(BaseData):
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


@dataclasses.dataclass
class Adapters(BaseData):
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
        request_schema_cls=json_api.system_settings.SystemSettingsUpdateSchema,
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


@dataclasses.dataclass
class Signup(BaseData):
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


@dataclasses.dataclass
class AuditLogs(BaseData):
    """Pass."""

    get: ApiEndpoint = ApiEndpoint(
        method="get",
        path="api/V4.0/settings/audit",
        request_schema_cls=json_api.audit_logs.AuditLogRequestSchema,
        request_model_cls=json_api.audit_logs.AuditLogRequest,
        response_schema_cls=json_api.audit_logs.AuditLogSchema,
        response_model_cls=json_api.audit_logs.AuditLog,
    )


@dataclasses.dataclass
class ApiEndpoints(BaseData):
    """Pass."""

    instances = Instances
    central_core = CentralCore
    system_settings = SystemSettings
    remote_support = RemoteSupport
    system_users = SystemUsers
    system_roles = SystemRoles
    lifecycle = Lifecycle
    adapters = Adapters
    signup = Signup
    password_reset = PasswordReset
    audit_logs = AuditLogs
    enforcements = Enforcements
    saved_queries = SavedQueries
    assets = Assets
