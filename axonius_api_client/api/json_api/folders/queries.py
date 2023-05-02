# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from ....data import BaseEnum
from ....exceptions import NotAllowedError
from ..base import BaseModel, BaseSchemaJson
from ..generic import Metadata, MetadataSchema
from ..saved_queries import QueryTypes, SavedQuery
from . import base


class FolderNames(BaseEnum):
    """Names of built-in folders used in Axonius."""

    public: str = "Shared Queries"
    private: str = "My Private Queries"
    asset_scope: str = "Asset Scope Queries"
    predefined: str = "Predefined Queries"
    untitled: str = "untitled folder"
    archive: str = "Archive"
    global_scope: str = "Global"


class FolderPaths(BaseEnum):
    """Paths of built-in folders used in Axonius."""

    public: str = base.Folder.join(FolderNames.public)
    private: str = base.Folder.join(FolderNames.private)
    asset_scope: str = base.Folder.join(FolderNames.asset_scope)
    predefined: str = base.Folder.join(FolderNames.public, FolderNames.predefined)
    archive: str = base.Folder.join(FolderNames.archive)
    global_scope: str = base.Folder.join(FolderNames.global_scope)


class RootTypes(BaseEnum):
    """Types of root folders used in Axonius."""

    public: str = "PUBLIC"
    private: str = "PRIVATE"
    asset_scope: str = "ASSET_SCOPE"
    archive: str = "ARCHIVE"
    current_scope: str = "CURRENT_SCOPE"


class Folder(base.Folder):
    """Mixins for folders for queries."""

    @classmethod
    def get_enum_names(cls) -> t.Type[BaseEnum]:
        """Pass."""
        return FolderNames

    @classmethod
    def get_enum_paths(cls) -> t.Type[BaseEnum]:
        """Pass."""
        return FolderPaths

    @classmethod
    def get_root_types(cls) -> t.Type[BaseEnum]:
        """Pass."""
        return RootTypes

    @classmethod
    def get_model_folder(cls) -> t.Type[base.FolderModel]:
        """Pass."""
        return FolderModel

    @classmethod
    def get_model_folders(cls) -> t.Type[base.FoldersModel]:
        """Pass."""
        return FoldersModel

    @classmethod
    def get_model_create_response(cls) -> t.Type[BaseModel]:
        """Pass."""
        return CreateFolderResponseModel

    @classmethod
    def get_models_objects(cls) -> t.Tuple[t.Type[BaseModel]]:
        """Pass."""
        return (SavedQuery,)

    @property
    def api_folders(self):
        """Get the folders API for this type of folders."""
        return self.client.folders.queries

    def _clear_objects_cache(self):
        """Clear any object specific cache being used."""
        super()._clear_objects_cache()
        self.client.devices.saved_query.get_cached.cache_clear()

    def _get_objects(
        self, full_objects: bool = base.FolderDefaults.full_objects
    ) -> t.List[SavedQuery]:
        """Pass."""
        return self.client.devices.saved_query.get_cached(
            include_usage=full_objects,
            get_view_data=full_objects,
            add_query_by_asset_type=False,
            as_dataclass=True,
        )

    def _create_object(
        self,
        query_type: t.Union[QueryTypes, str] = base.FolderDefaults.query_type,
        **kwargs,
    ) -> BaseModel:
        """Pass."""
        kwargs.setdefault("as_dataclass", True)
        query_type: str = QueryTypes.get_value_by_value(query_type)
        apiobj: object = getattr(self.client, query_type)
        created: SavedQuery = apiobj.saved_query.add(**kwargs)
        return created

    def get_default_folder(
        self, asset_scope: bool = False, private: bool = False, **kwargs
    ) -> "FolderModel":
        """Determine folder to use."""
        if asset_scope is True:
            return self.path_asset_scope
        if private is True:
            return self.path_private

        return self.path_public

    @property
    def path_public(self) -> "FolderModel":
        """Get the root of the public folders."""
        # hack to use /Global instead of /Shared Queries when data_scopes feature is enabled
        try:
            if self.HTTP.CLIENT.data_scopes.is_feature_enabled:
                return self.path_global_scope
        except Exception:
            pass
        return super().path_public

    def _check_resolved_folder(
        self,
        reason: str,
        fallback: t.Optional["Folder"] = None,
        asset_scope: bool = False,
        **kwargs,
    ) -> "Folder":
        """Check if resolved folder meets object type specific restrictions."""
        if asset_scope is True and self.root_type != str(RootTypes.asset_scope):
            msgs: t.List[str] = [
                f"Supplied path is not an asset scope folder but asset_scope={asset_scope}",
                f"Supplied path: {self!r}",
                f"Fallback path: {fallback!r}",
            ]
            if self.is_model_folder(fallback):
                self.spew(msgs, echo=True)
                return fallback
            raise NotAllowedError(msgs)

        return self

    @property
    def path_archive(self) -> "FolderModel":
        """Get the archive folder for saved queries."""
        return self.find(folder=self.get_enum_paths().archive)

    @property
    def path_predefined(self) -> "FolderModel":
        """Get the predefined folder for saved queries."""
        return self.find(folder=self.get_enum_paths().predefined)

    @property
    def path_asset_scope(self) -> "FolderModel":
        """Get the root of the asset scope folders."""
        return self.find(folder=self.get_enum_paths().asset_scope)

    @property
    def path_global_scope(self) -> "FolderModel":
        """Get the root of the global scope folders."""
        return self.find(folder=self.get_enum_paths().global_scope)


class CreateFolderRequestSchema(BaseSchemaJson, base.CreateFolderRequestSchema):
    """Marshmallow schema for request to create a folder."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return CreateFolderRequestModel

    class Meta:
        """Pass."""

        type_ = "folders_request_schema"


class CreateFolderResponseSchema(MetadataSchema):
    """Marshmallow schema for response to create a folder."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return CreateFolderResponseModel

    class Meta:
        """Pass."""

        type_ = "metadata_schema"


class RenameFolderRequestSchema(BaseSchemaJson, base.RenameFolderRequestSchema):
    """Marshmallow schema for request to rename a folder."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return RenameFolderRequestModel

    class Meta:
        """Pass."""

        type_ = "folder_rename_request_schema"


class RenameFolderResponseSchema(MetadataSchema):
    """Marshmallow schema for response to rename folder."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return RenameFolderResponseModel

    class Meta:
        """Pass."""

        type_ = "metadata_schema"


class MoveFolderRequestSchema(BaseSchemaJson, base.MoveFolderRequestSchema):
    """Marshmallow schema for request to move a folder."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return MoveFolderRequestModel

    class Meta:
        """Pass."""

        type_ = "folder_update_parent_request_schema"


class MoveFolderResponseSchema(MetadataSchema):
    """Marshmallow schema for response to move a folder."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return MoveFolderResponseModel

    class Meta:
        """Pass."""

        type_ = "metadata_schema"


class DeleteFolderResponseSchema(MetadataSchema):
    """Marshmallow schema for response to delete a folder."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return DeleteFolderResponseModel

    class Meta:
        """Pass."""

        type_ = "metadata_schema"


class FoldersSchema(BaseSchemaJson, base.FoldersSchema):
    """Marshmallow schema for response to get folders."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return FoldersModel

    class Meta:
        """Pass."""

        type_ = "folders_response_schema"


@dataclasses.dataclass(repr=False)
class CreateFolderRequestModel(BaseModel, base.CreateFolderRequestModel):
    """Dataclass model for request to create a folder."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return CreateFolderRequestSchema


@dataclasses.dataclass(repr=False)
class CreateFolderResponseModel(Metadata, base.CreateFolderResponseModel):
    """Dataclass model for response to create a folder."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return CreateFolderResponseSchema


@dataclasses.dataclass(repr=False)
class RenameFolderRequestModel(Metadata, base.RenameFolderRequestModel):
    """Dataclass model for request to rename a folder."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return RenameFolderRequestSchema


@dataclasses.dataclass(repr=False)
class RenameFolderResponseModel(Metadata, base.RenameFolderResponseModel):
    """Dataclass model for response to rename a folder."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return RenameFolderResponseSchema


@dataclasses.dataclass(repr=False)
class MoveFolderRequestModel(Metadata, base.MoveFolderRequestModel):
    """Dataclass model for request to rename a folder."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return MoveFolderRequestSchema


@dataclasses.dataclass(repr=False)
class MoveFolderResponseModel(Metadata, base.MoveFolderResponseModel):
    """Dataclass model for response to rename a folder."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return MoveFolderResponseSchema


@dataclasses.dataclass(repr=False)
class DeleteFolderResponseModel(Metadata, base.DeleteFolderResponseModel):
    """Dataclass model for response to delete a folder."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return DeleteFolderResponseSchema


@dataclasses.dataclass(repr=False, eq=False)
class FolderModel(Folder, BaseModel, base.FolderModel):
    """Dataclass model for unmodeled folder objects in FoldersModel."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


@dataclasses.dataclass(repr=False, eq=False)
class FoldersModel(Folder, BaseModel, base.FoldersModel):
    """Dataclass model for response to get folders."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return FoldersSchema
