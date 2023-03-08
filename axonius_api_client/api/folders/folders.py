# -*- coding: utf-8 -*-
"""API for working with folders."""
import abc
import typing as t

from cachetools import TTLCache, cached

from ..api_endpoints import ApiEndpoint, ApiEndpointGroup, ApiEndpoints
from ..json_api.folders.base import (
    CreateFolderRequestModel,
    CreateFolderResponseModel,
    DeleteFolderResponseModel,
    Folder,
    FolderDefaults,
    FolderModel,
    FoldersModel,
    MoveFolderRequestModel,
    MoveFolderResponseModel,
    RenameFolderRequestModel,
    RenameFolderResponseModel,
)
from ..mixins import ModelMixins


class Folders(ModelMixins):
    """Pass."""

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        self.queries: FoldersQueries = FoldersQueries(auth=self.auth, **kwargs)
        self.enforcements: FoldersEnforcements = FoldersEnforcements(auth=self.auth, **kwargs)


class FoldersMixins(ModelMixins, abc.ABC):
    """Pass."""

    # XXX .search_objects(path=path, values="~test")
    # XXX .search_objects_delete(path=path, searches="~test", target=target)
    # XXX .search_objects_copy(path=path, searches="~test", target=target)
    # XXX .search_objects_move(path=path, searches="~test", target=target)

    @abc.abstractproperty
    def api_endpoint_group(self) -> ApiEndpointGroup:
        """Pass."""
        raise NotImplementedError()

    @cached(cache=TTLCache(maxsize=1024, ttl=60))
    def get_cached(self, *args, **kwargs) -> t.Union[FoldersModel, FolderModel]:
        """Get the root folders for this object type using a 60 second cache."""
        return self.get(*args, **kwargs)

    def get(
        self,
        path: t.Optional[t.Union[str, Folder]] = None,
        create: bool = FolderDefaults.create,
        echo: bool = FolderDefaults.echo,
        minimum_depth: t.Optional[int] = None,
    ) -> t.Union[FoldersModel, FolderModel]:
        """Get the root folders for this object type.

        Args:
            path (t.Optional[t.Union[str, Folder]], optional): if supplied, folder to find
                and return
            create (bool, optional): if path supplied and does not exist, create it as necessary
            echo (bool, optional): echo output to console
            minimum_depth (t.Optional[int], optional): Description
        """
        data: FoldersModel = self._get()
        if data.is_findable(path):
            return data.find(value=path, create=create, echo=echo, minimum_depth=minimum_depth)
        return data

    def get_tree(
        self,
        path: t.Optional[t.Union[str, Folder]] = None,
        maximum_depth: t.Optional[int] = None,
        include_objects: bool = FolderDefaults.include_objects,
        include_details: bool = FolderDefaults.include_details,
        as_str: bool = False,
        **kwargs,
    ) -> t.Union[t.List[str], str]:
        """Get a tree view of all subfolders and their objects.

        Args:
            include_objects (bool, optional): include objects in output
            include_details (bool, optional): show summary or details in output
            maximum_depth (t.Optional[int], optional): print only recursive counts past this depth,
                not the actual subfolders and objects
            as_str (bool, optional): return as str instead of list of str
        """
        data: Folder = self.get(path=path, **kwargs)
        return data.get_tree(
            maximum_depth=maximum_depth,
            include_objects=include_objects,
            include_details=include_details,
            as_str=as_str,
        )

    def delete(
        self,
        path: t.Union[str, Folder],
        confirm: bool = FolderDefaults.confirm,
        include_subfolders: bool = FolderDefaults.include_subfolders,
        include_objects: bool = FolderDefaults.include_objects,
        echo: bool = FolderDefaults.echo,
        prompt: bool = FolderDefaults.prompt,
        prompt_default: bool = FolderDefaults.prompt_default,
    ) -> DeleteFolderResponseModel:
        """Pass."""
        path: FolderModel = self.get(path=path, echo=echo)
        return path.delete(
            confirm=confirm,
            include_subfolders=include_subfolders,
            include_objects=include_objects,
            echo=echo,
            prompt=prompt,
            prompt_default=prompt_default,
        )

    def create(
        self, path: t.Union[str, Folder], target: str, echo: bool = FolderDefaults.echo
    ) -> "FolderModel":
        """Create a subfolder.

        Args:
            value (str): Name of folder to create under this folder

        """
        path: FolderModel = self.get(path=path, echo=echo)
        return path.create(value=target, echo=echo)

    def rename(
        self, path: t.Union[str, Folder], target: str, echo: bool = FolderDefaults.echo
    ) -> "FolderModel":
        """Pass."""
        path: FolderModel = self.get(path=path, echo=echo)
        return path.rename(value=target, echo=echo)

    def move(
        self,
        path: t.Union[str, Folder],
        target: t.Union[str, Folder],
        create: bool = FolderDefaults.create_move,
        echo: bool = FolderDefaults.echo,
    ) -> "FolderModel":
        """Pass."""
        path: FolderModel = self.get(path=path, echo=echo)
        return path.move(value=target, create=create, echo=echo)

    def _get(self) -> FoldersModel:
        """Direct API method to get all folders.

        Returns:
            FoldersModel: API response model
        """
        endpoint: ApiEndpoint = self.api_endpoint_group.get
        response: FoldersModel = endpoint.perform_request(http=self.auth.http)
        return response

    def _rename(self, id: str, name: str) -> RenameFolderResponseModel:
        """Pass."""
        endpoint: ApiEndpoint = self.api_endpoint_group.rename
        request_obj: RenameFolderRequestModel = endpoint.load_request(name=name)
        response: RenameFolderResponseModel = endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, id=id
        )
        return response

    def _move(self, id: str, parent_id: str) -> MoveFolderResponseModel:
        """Pass."""
        endpoint: ApiEndpoint = self.api_endpoint_group.move
        request_obj: MoveFolderRequestModel = endpoint.load_request(parent_id=parent_id)
        response: MoveFolderResponseModel = endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            id=id,
        )
        return response

    def _create(self, name: str, parent_id: str) -> CreateFolderResponseModel:
        """Pass."""
        endpoint: ApiEndpoint = self.api_endpoint_group.create
        request_obj: CreateFolderRequestModel = endpoint.load_request(
            name=name, parent_id=parent_id
        )
        response: CreateFolderResponseModel = endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj
        )
        return response

    def _delete(self, id: str) -> DeleteFolderResponseModel:
        """Pass."""
        endpoint: ApiEndpoint = self.api_endpoint_group.delete
        response: DeleteFolderResponseModel = endpoint.perform_request(http=self.auth.http, id=id)
        return response


class FoldersQueries(FoldersMixins):
    """Pass."""

    @property
    def api_endpoint_group(self) -> ApiEndpointGroup:
        """Pass."""
        return ApiEndpoints.folders_queries


class FoldersEnforcements(FoldersMixins):
    """Pass."""

    @property
    def api_endpoint_group(self) -> ApiEndpointGroup:
        """Pass."""
        return ApiEndpoints.folders_enforcements
