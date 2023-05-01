# -*- coding: utf-8 -*-
"""API for working with folders."""
import abc
import typing as t

from cachetools import TTLCache, cached

from ..api_endpoints import ApiEndpoint, ApiEndpointGroup, ApiEndpoints
from ..json_api.folders.base import (
    BaseModel,
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
    """Container for folders for different object types in Axonius."""

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        self.queries: FoldersQueries = FoldersQueries(auth=self.auth, **kwargs)
        self.enforcements: FoldersEnforcements = FoldersEnforcements(auth=self.auth, **kwargs)


class FoldersMixins(ModelMixins, abc.ABC):
    """Base model for folders API."""

    @abc.abstractproperty
    def api_endpoint_group(self) -> ApiEndpointGroup:
        """Endpoint group to use for this folders object type."""
        raise NotImplementedError()

    def get(self) -> FoldersModel:
        """Get the root for this folders object type."""
        root: FoldersModel = self._get()
        return root

    @cached(cache=TTLCache(maxsize=1024, ttl=60))
    def get_cached(self) -> t.Union[FoldersModel, FolderModel]:
        """Get the root for this folders object type using a cache with a TTL of 60."""
        return self.get()

    def get_tree(
        self,
        folder: t.Optional[t.Union[str, Folder]] = None,
        maximum_depth: t.Optional[int] = None,
        include_objects: bool = FolderDefaults.include_objects,
        include_details: bool = FolderDefaults.include_details,
        as_str: bool = False,
    ) -> t.Union[t.List[str], str]:
        """Get a tree view of all subfolders and their objects.

        Args:
            folder (t.Optional[t.Union[str, Folder]], optional): folder to get tree of, defaults to
                / if not supplied
            maximum_depth (t.Optional[int], optional): Stop printing folders & objects past this
                depth
            include_objects (bool, optional): include objects in output
            include_details (bool, optional): show summary or details in output
            as_str (bool, optional): return as str instead of list of str
        """
        if folder is None:
            folder = "/"
        folder: Folder = self.find(folder=folder, create=False, echo=False)
        return folder.get_tree(
            maximum_depth=maximum_depth,
            include_objects=include_objects,
            include_details=include_details,
            as_str=as_str,
        )

    def find(
        self,
        folder: t.Union[str, Folder],
        create: bool = FolderDefaults.create,
        echo: bool = FolderDefaults.echo,
    ) -> Folder:
        """Get a folder by path, id, or folder model for this folders object type.

        Args:
            folder (t.Union[str, Folder]): if supplied, folder to find
                and return
            create (bool, optional): if folder supplied and does not exist, create it as necessary
            echo (bool, optional): echo output to console

        """
        root: FoldersModel = self.get()
        return root.find(folder=folder, create=create, refresh=False, echo=echo)

    @cached(cache=TTLCache(maxsize=1024, ttl=60))
    def find_cached(self, *args, **kwargs) -> t.Union[FoldersModel, FolderModel]:
        """Find a folder for this folders object type using a cache with a TTL of 60."""
        return self.find(*args, **kwargs)

    def search_objects(
        self,
        folder: t.Union[str, Folder],
        searches: t.List[str],
        pattern_prefix: t.Optional[str] = FolderDefaults.pattern_prefix,
        ignore_case: bool = FolderDefaults.ignore_case,
        error_unmatched: bool = FolderDefaults.error_unmatched,
        error_no_matches: bool = FolderDefaults.error_no_matches,
        error_no_objects: bool = FolderDefaults.error_no_objects,
        recursive: bool = FolderDefaults.recursive,
        all_objects: bool = FolderDefaults.all_objects,
        full_objects: bool = FolderDefaults.full_objects_search,
        echo: bool = FolderDefaults.echo,
    ) -> t.Tuple["Folder", t.List[BaseModel]]:
        """Search for objects in a folder.

        Args:
            folder (t.Union[str, Folder]): Folder to search objects for
            searches (t.List[str]): List of object names to search for
            pattern_prefix (t.Optional[str], optional): Treat any searches that start with this
                prefix as a regex
            ignore_case (bool, optional): ignore case when building patterns
            error_unmatched (bool, optional): Throw a fit if any searches supplied have no
                matches
            error_no_matches (bool, optional): Throw a fit if no searches match objects
            error_no_objects (bool, optional): Throw a fit if no objects exist in folder
            recursive (bool, optional): search all objects under folder
            all_objects (bool, optional): search all objects in the entire system
            full_objects (bool, optional): return objects with their full data
            echo (bool, optional): echo output to console

        """
        folder: Folder = self.find(folder=folder, create=False, echo=echo)
        objs: t.List[BaseModel] = folder.search_objects(
            searches=searches,
            pattern_prefix=pattern_prefix,
            ignore_case=ignore_case,
            error_unmatched=error_unmatched,
            error_no_matches=error_no_matches,
            error_no_objects=error_no_objects,
            recursive=recursive,
            all_objects=all_objects,
            full_objects=full_objects,
            echo=echo,
        )
        return folder, objs

    def search_objects_copy(
        self,
        folder: t.Union[str, Folder],
        searches: t.List[str],
        target: t.Optional[t.Union[str, Folder]] = None,
        copy_prefix: str = FolderDefaults.copy_prefix,
        create: bool = FolderDefaults.create_action,
        pattern_prefix: t.Optional[str] = FolderDefaults.pattern_prefix,
        ignore_case: bool = FolderDefaults.ignore_case,
        error_unmatched: bool = FolderDefaults.error_unmatched,
        error_no_matches: bool = FolderDefaults.error_no_matches,
        error_no_objects: bool = FolderDefaults.error_no_objects,
        recursive: bool = FolderDefaults.recursive,
        all_objects: bool = FolderDefaults.all_objects,
        full_objects: bool = FolderDefaults.full_objects_search,
        echo: bool = FolderDefaults.echo_action,
    ) -> t.Tuple["Folder", t.List[BaseModel]]:
        """Search for objects in a folder and copy them, optionally to a different folder.

        Args:
            folder (t.Union[str, Folder]): Folder to search objects for
            searches (t.List[str]): List of object names to search for
            target (t.Optional[t.Union[str, Folder]], optional): optional folder to copy
                objects to
            copy_prefix (str, optional): value to prepend to each objects name
            create (bool, optional): if target is supplied and does not exist, create it
            pattern_prefix (t.Optional[str], optional): Treat any searches that start with this
                prefix as a regex
            ignore_case (bool, optional): ignore case when building patterns
            error_unmatched (bool, optional): Throw a fit if any searches supplied have no
                matches
            error_no_matches (bool, optional): Throw a fit if no searches match objects
            error_no_objects (bool, optional): Throw a fit if no objects exist in folder
            recursive (bool, optional): search all objects under folder
            all_objects (bool, optional): search all objects in the entire system
            full_objects (bool, optional): return objects with their full data
            echo (bool, optional): echo output to console
        """
        folder: Folder = self.find(folder=folder, create=False, echo=echo)
        return folder.search_objects_copy(
            searches=searches,
            folder=target,
            copy_prefix=copy_prefix,
            create=create,
            pattern_prefix=pattern_prefix,
            ignore_case=ignore_case,
            error_unmatched=error_unmatched,
            error_no_matches=error_no_matches,
            error_no_objects=error_no_objects,
            recursive=recursive,
            all_objects=all_objects,
            full_objects=full_objects,
            echo=echo,
        )

    def search_objects_move(
        self,
        folder: t.Union[str, Folder],
        searches: t.List[str],
        target: t.Union[str, Folder],
        create: bool = FolderDefaults.create_action,
        pattern_prefix: t.Optional[str] = FolderDefaults.pattern_prefix,
        ignore_case: bool = FolderDefaults.ignore_case,
        error_unmatched: bool = FolderDefaults.error_unmatched,
        error_no_matches: bool = FolderDefaults.error_no_matches,
        error_no_objects: bool = FolderDefaults.error_no_objects,
        recursive: bool = FolderDefaults.recursive,
        all_objects: bool = FolderDefaults.all_objects,
        full_objects: bool = FolderDefaults.full_objects_search,
        echo: bool = FolderDefaults.echo_action,
    ) -> t.Tuple["Folder", t.List[BaseModel]]:
        """Search for objects in a folder and move themto a different folder.

        Args:
            folder (t.Union[str, Folder]): Folder to search objects for
            searches (t.List[str]): List of object names to search for
            target (t.Union[str, Folder]): optional folder to copy
                objects to
            create (bool, optional): if target is supplied and does not exist, create it
            pattern_prefix (t.Optional[str], optional): Treat any searches that start with this
                prefix as a regex
            ignore_case (bool, optional): ignore case when building patterns
                that start with pattern_prefix
            error_unmatched (bool, optional): Throw a fit if any searches supplied have no
                matches
            error_no_matches (bool, optional): Throw a fit if no searches match objects
            error_no_objects (bool, optional): Throw a fit if no objects exist in folder
            recursive (bool, optional): search all objects under folder
            all_objects (bool, optional): search all objects in the entire system
            full_objects (bool, optional): return objects with their full data
            echo (bool, optional): echo output to console
        """
        folder: Folder = self.find(folder=folder, create=False, echo=echo)
        return folder.search_objects_move(
            searches=searches,
            folder=target,
            create=create,
            pattern_prefix=pattern_prefix,
            ignore_case=ignore_case,
            error_unmatched=error_unmatched,
            error_no_matches=error_no_matches,
            error_no_objects=error_no_objects,
            recursive=recursive,
            all_objects=all_objects,
            full_objects=full_objects,
            echo=echo,
        )

    def search_objects_delete(
        self,
        folder: t.Union[str, Folder],
        searches: t.List[str],
        confirm: bool = FolderDefaults.confirm,
        prompt: bool = FolderDefaults.prompt,
        prompt_default: bool = FolderDefaults.prompt_default,
        pattern_prefix: t.Optional[str] = FolderDefaults.pattern_prefix,
        ignore_case: bool = FolderDefaults.ignore_case,
        error_unmatched: bool = FolderDefaults.error_unmatched,
        error_no_matches: bool = FolderDefaults.error_no_matches,
        error_no_objects: bool = FolderDefaults.error_no_objects,
        recursive: bool = FolderDefaults.recursive,
        all_objects: bool = FolderDefaults.all_objects,
        full_objects: bool = FolderDefaults.full_objects_search,
        echo: bool = FolderDefaults.echo_action,
    ) -> t.Tuple["Folder", t.List[BaseModel], t.List[BaseModel]]:
        """Search for objects in a folder and move themto a different folder.

        Args:
            folder (t.Union[str, Folder]): Folder to search objects for
            searches (t.List[str]): List of object names to search for
            confirm (bool, optional): Throw a fit if neither confirm nor prompt is True
            prompt (bool, optional): If confirm is not True and prompt is True, prompt user
                to delete each object
            prompt_default (bool, optional): if prompt is True, default choice to use in prompt
            pattern_prefix (t.Optional[str], optional): Treat any searches that start with this
                prefix as a regex
            ignore_case (bool, optional): ignore case when building patterns
            error_unmatched (bool, optional): Throw a fit if any searches supplied have no
                matches
            error_no_matches (bool, optional): Throw a fit if no searches match objects
            error_no_objects (bool, optional): Throw a fit if no objects exist in folder
            recursive (bool, optional): search all objects under folder
            all_objects (bool, optional): search all objects in the entire system
            full_objects (bool, optional): return objects with their full data
            echo (bool, optional): echo output to console
        """
        folder: Folder = self.find(folder=folder, create=False, echo=echo)
        results: t.Tuple[t.List[BaseModel], t.List[BaseModel]] = folder.search_objects_delete(
            searches=searches,
            confirm=confirm,
            prompt=prompt,
            prompt_default=prompt_default,
            pattern_prefix=pattern_prefix,
            ignore_case=ignore_case,
            error_unmatched=error_unmatched,
            error_no_matches=error_no_matches,
            error_no_objects=error_no_objects,
            recursive=recursive,
            all_objects=all_objects,
            full_objects=full_objects,
            echo=echo,
        )
        return (folder, *results)

    def create(
        self,
        folder: t.Union[str, Folder],
        echo: bool = FolderDefaults.echo_action,
    ) -> FolderModel:
        """Create a folder.

        Args:
            folder (t.Union[str, Folder]): folder to create
            echo (bool, optional): echo output to console

        """
        folder: Folder = self.find(folder=folder, create=True, echo=echo)
        return folder

    def rename(
        self,
        folder: t.Union[str, Folder],
        target: str,
        echo: bool = FolderDefaults.echo_action,
    ) -> FolderModel:
        """Rename a folder.

        Args:
            folder (t.Union[str, Folder]): folder to rename
            target (str): new name to give folder
            echo (bool, optional): echo output to console
        """
        folder: Folder = self.find(folder=folder, create=False, echo=echo)
        return folder.rename(folder=target, echo=echo)

    def move(
        self,
        folder: t.Union[str, Folder],
        target: t.Union[str, Folder],
        create: bool = FolderDefaults.create_action,
        echo: bool = FolderDefaults.echo_action,
    ) -> FolderModel:
        """Move a folder.

        Args:
            folder (t.Union[str, Folder]): path of folder to move
            target (t.Union[str, Folder]): path to move folder to
            create (bool, optional): create target if it does not exist
            echo (bool, optional): echo output to console
        """
        folder: Folder = self.find(folder=folder, create=False, echo=echo)
        return folder.move(folder=target, create=create, echo=echo)

    def delete(
        self,
        folder: t.Union[str, Folder],
        confirm: bool = FolderDefaults.confirm,
        delete_subfolders: bool = FolderDefaults.delete_subfolders,
        delete_objects: bool = FolderDefaults.delete_objects,
        echo: bool = FolderDefaults.echo_action,
        prompt: bool = FolderDefaults.prompt,
        prompt_default: bool = FolderDefaults.prompt_default,
    ) -> t.Tuple[FolderModel, DeleteFolderResponseModel]:
        """Delete a folder and all of its subfolders and objects recursively.

        Args:
            folder (t.Union[str, Folder]): folder to delete
            confirm (bool, optional): Throw a fit if neither confirm nor prompt is True
            delete_subfolders (bool, optional): Throw a fit if subfolders exist and this is not True
            delete_objects (bool, optional): Throw a fit if objects exist recursively and this is
                not True
            echo (bool, optional): echo output to console
            prompt (bool, optional): If confirm is not True and prompt is True, prompt user
                to delete each object
            prompt_default (bool, optional): if prompt is True, default choice to use in prompt
        """
        folder: Folder = self.find(folder=folder, create=False, echo=echo)
        response: DeleteFolderResponseModel = folder.delete(
            confirm=confirm,
            delete_subfolders=delete_subfolders,
            delete_objects=delete_objects,
            echo=echo,
            prompt=prompt,
            prompt_default=prompt_default,
        )
        return folder, response

    def _get(self) -> FoldersModel:
        """Direct API method to get all folders.

        Returns:
            FoldersModel: response model
        """
        endpoint: ApiEndpoint = self.api_endpoint_group.get
        response: FoldersModel = endpoint.perform_request(http=self.auth.http)
        return response

    def _rename(self, id: str, name: str) -> RenameFolderResponseModel:
        """Direct API method to rename a folder.

        Args:
            id (str): ID of folder to rename
            name (str): new name to assign to folder

        Returns:
            RenameFolderResponseModel: response model
        """
        endpoint: ApiEndpoint = self.api_endpoint_group.rename
        request_obj: RenameFolderRequestModel = endpoint.load_request(name=name)
        response: RenameFolderResponseModel = endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, id=id
        )
        return response

    def _move(self, id: str, parent_id: str) -> MoveFolderResponseModel:
        """Direct API method to move a folder.

        Args:
            id (str): ID of folder to move
            parent_id (str): ID of new parent folder

        Returns:
            MoveFolderResponseModel: response model
        """
        endpoint: ApiEndpoint = self.api_endpoint_group.move
        request_obj: MoveFolderRequestModel = endpoint.load_request(parent_id=parent_id)
        response: MoveFolderResponseModel = endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            id=id,
        )
        return response

    def _create(self, name: str, parent_id: str) -> CreateFolderResponseModel:
        """Direct API method to create a folder.

        Args:
            name (str): name to assign to folder
            parent_id (str): ID of folder to create folder under

        Returns:
            CreateFolderResponseModel: response model
        """
        endpoint: ApiEndpoint = self.api_endpoint_group.create
        request_obj: CreateFolderRequestModel = endpoint.load_request(
            name=name, parent_id=parent_id
        )
        response: CreateFolderResponseModel = endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj
        )
        return response

    def _delete(self, id: str) -> DeleteFolderResponseModel:
        """Direct API method to delete a folder.

        Args:
            id (str): ID of folder to delete

        Returns:
            DeleteFolderResponseModel: response model
        """
        endpoint: ApiEndpoint = self.api_endpoint_group.delete
        response: DeleteFolderResponseModel = endpoint.perform_request(http=self.auth.http, id=id)
        return response


class FoldersQueries(FoldersMixins):
    """Model for folders for Saved Query objects."""

    TYPE: str = "queries"

    @property
    def api_endpoint_group(self) -> ApiEndpointGroup:
        """Pass."""
        return ApiEndpoints.folders_queries


class FoldersEnforcements(FoldersMixins):
    """Model for folders for Enforcement objects."""

    TYPE: str = "enforcements"

    @property
    def api_endpoint_group(self) -> ApiEndpointGroup:
        """Pass."""
        return ApiEndpoints.folders_enforcements
