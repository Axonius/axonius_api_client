# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from ....data import BaseEnum
from ..base import BaseModel, BaseSchemaJson
from ..enforcements import Enforcement
from ..generic import Metadata, MetadataSchema
from . import base


class FolderNames(BaseEnum):
    """Names of built-in folders used in Axonius."""

    public: str = "Shared Enforcements"
    private: str = "Drafts"
    untitled: str = "untitled folder"


class FolderPaths(BaseEnum):
    """Paths of built-in folders used in Axonius."""

    public: str = base.Folder.join(FolderNames.public)
    private: str = base.Folder.join(FolderNames.private)


class Folder(base.Folder):
    """Mixins for folders for queries."""

    @classmethod
    def get_enum_names(cls) -> BaseEnum:
        """Pass."""
        return FolderNames

    @classmethod
    def get_enum_paths(cls) -> BaseEnum:
        """Pass."""
        return FolderPaths

    @classmethod
    def get_model_folder(cls) -> t.Type[base.FolderModel]:
        """Pass."""
        return FolderModel

    @classmethod
    def get_model_folders(cls) -> t.Type[base.FoldersModel]:
        """Pass."""
        return FoldersModel

    @classmethod
    def get_models_objects(cls) -> t.Tuple[t.Type[BaseModel]]:
        """Pass."""
        return (Enforcement,)

    @classmethod
    def get_model_create_response(cls) -> t.Type[BaseModel]:
        """Pass."""
        return CreateFolderResponseModel

    @property
    def api_folders(self):
        """Get the folders API for this type of folders."""
        return self.client.folders.enforcements

    def _clear_objects_cache(self):
        """Clear any object specific cache being used."""
        super()._clear_objects_cache()
        self.client.enforcements.get_sets_cached.cache_clear()

    def _get_objects(
        self,
        full_objects: bool = base.FolderDefaults.full_objects,
    ) -> t.List[Enforcement]:
        """Get all objects in current folder."""
        return self.client.enforcements.get_sets_cached(full=full_objects)

    def _create_object(self, **kwargs) -> Enforcement:
        """Pass."""
        created: Enforcement = self.client.enforcements.create(**kwargs)
        return created


class CreateFolderRequestSchema(BaseSchemaJson, base.CreateFolderRequestSchema):
    """Marshmallow schema for request to create folder."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return CreateFolderRequestModel

    class Meta:
        """Pass."""

        type_ = "folders_request_schema"


class CreateFolderResponseSchema(MetadataSchema):
    """Marshmallow schema for response to create folder."""

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
    """Marshmallow schema  for response to delete folder."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return DeleteFolderResponseModel

    class Meta:
        """Pass."""

        type_ = "metadata_schema"


class FoldersSchema(base.FoldersSchema, BaseSchemaJson):
    """Marshmallow schema for response to get folders."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return FoldersModel

    class Meta:
        """Pass."""

        type_ = "folders_response_schema"


@dataclasses.dataclass(repr=False)
class CreateFolderRequestModel(base.CreateFolderRequestModel, BaseModel):
    """Dataclass model for request to create folder."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return CreateFolderRequestSchema


@dataclasses.dataclass(repr=False)
class CreateFolderResponseModel(base.CreateFolderResponseModel, Metadata):
    """Dataclass model for response to create folder."""

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
class DeleteFolderResponseModel(base.DeleteFolderResponseModel, Metadata):
    """Dataclass model for response to delete folder."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return DeleteFolderResponseSchema


@dataclasses.dataclass(repr=False, eq=False)
class FolderModel(Folder, BaseModel, base.FolderModel):
    """Dataclass model for unmodeled folder objects in RootFolders."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


@dataclasses.dataclass(repr=False, eq=False)
class FoldersModel(Folder, BaseModel, base.FoldersModel):
    """Dataclass model for unmodeled folder objects in RootFolders."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return FoldersSchema
