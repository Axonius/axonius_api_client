# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import abc
import dataclasses
import datetime
import enum
import typing as t

import click
import marshmallow
import marshmallow_jsonapi

from ....constants.api import FolderDefaults
from ....constants.ctypes import FolderBase, Refreshables
from ....data import BaseEnum
from ....exceptions import (
    AxonTypeError,
    FolderAlreadyExistsError,
    FolderNotFoundError,
    NotAllowedError,
    SearchNoMatchesError,
    SearchNoObjectsError,
    SearchUnmatchedError,
)
from ....logs import get_echoer
from ....parsers.searchers import Search, Searches
from ....tools import (
    bytes_to_str,
    check_confirm_prompt,
    coerce_bool,
    coerce_int_float,
    combo_dicts,
    is_str,
    listify,
)
from ..base import BaseModel
from ..custom_fields import SchemaDatetime, get_field_dc_mm
from ..system_users import SystemUser


class CreateFolderRequestSchema:
    """Marshmallow schema for request to create a folder."""

    name = marshmallow_jsonapi.fields.Str()
    parent_id = marshmallow_jsonapi.fields.Str()


class RenameFolderRequestSchema:
    """Marshmallow schema for request to rename a folder."""

    name = marshmallow_jsonapi.fields.Str()


class MoveFolderRequestSchema:
    """Marshmallow schema for request to move a folder."""

    parent_id = marshmallow_jsonapi.fields.Str()


class FoldersSchema:
    """Marshmallow schema for response to get folders."""

    folders = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())


class FolderDataMixin:
    """Mixins for Metadata responses with 'folder_data' as dict."""

    @property
    def folder_data(self) -> dict:
        """Get the folder_data dict from the create response metadata."""
        return self.document_meta.get("folder_data") or {}

    @property
    def id(self) -> t.Optional[str]:
        """Get the ID of the created folder."""
        return self.folder_data.get("_id")

    @property
    def parent_id(self) -> t.Optional[str]:
        """Get the parent ID of the created folder."""
        return self.folder_data.get("parent_id")

    @property
    def name(self) -> t.Optional[str]:
        """Get the name of the created folder."""
        return self.folder_data.get("name")

    @property
    def message(self) -> str:
        """Get the status message."""
        return self.document_meta["message"]

    def __str__(self) -> str:
        """Get a string."""
        items: t.List[str] = [
            f"id={self.id!r}",
            f"parent_id={self.parent_id!r}",
            f"name={self.name!r}",
            f"message={self.message!r}",
        ]
        items: str = ", ".join(items)
        return f"{self.__class__.__name__}({items})"

    def __repr__(self) -> str:
        """Get a string."""
        return self.__str__()


@dataclasses.dataclass(repr=False)
class CreateFolderRequestModel:
    """Dataclass model for request to create a folder."""

    name: str
    parent_id: str


@dataclasses.dataclass(repr=False)
class CreateFolderResponseModel(FolderDataMixin):
    """Dataclass model for response to create a folder."""

    pass


@dataclasses.dataclass(repr=False)
class RenameFolderRequestModel:
    """Dataclass model for request to create a folder."""

    name: str


@dataclasses.dataclass(repr=False)
class RenameFolderResponseModel(FolderDataMixin):
    """Dataclass model for response to rename a folder."""

    pass


@dataclasses.dataclass(repr=False)
class MoveFolderRequestModel:
    """Dataclass model for request to move a folder."""

    parent_id: str


@dataclasses.dataclass(repr=False)
class MoveFolderResponseModel(FolderDataMixin):
    """Dataclass model for response to move a folder."""

    pass


@dataclasses.dataclass(repr=False)
class DeleteFolderResponseModel:
    """Dataclass model for response to delete a folder."""

    @property
    def id(self) -> str:
        """Get the ID of the created folder."""
        return self.document_meta["folder_id"]

    @property
    def message(self) -> str:
        """Get the status message."""
        return self.document_meta["message"]

    def __str__(self) -> str:
        """Pass."""
        items: t.List[str] = [
            f"id={self.id!r}",
            f"message={self.message!r}",
        ]
        items: str = ", ".join(items)
        return f"{self.__class__.__name__}({items})"


class Folder(abc.ABC, FolderBase):
    """Container of mixins used by Folder objects."""

    folder_defaults: t.ClassVar[FolderDefaults] = FolderDefaults
    sep: t.ClassVar[str] = FolderDefaults.sep
    mark_folder: t.ClassVar[str] = f"{sep} "
    mark_object: t.ClassVar[str] = "@ "
    mark_indent: t.ClassVar[str] = "| "

    def refresh(
        self, value: Refreshables = FolderDefaults.refresh, force: bool = False
    ) -> "Folder":
        """Refresh the root folders data.

        Args:
            value (Refreshables, optional): only perform if refresh is True or is
                int/float and elapsed >= refresh.
            force (bool, optional): perform a refresh if force is True

        """
        check: bool = self._parse_refresh(value=value)
        if check is True or force is True:
            return self._refresh()
        return self

    @property
    def refreshed(self) -> datetime.datetime:
        """Get the refreshed status of the root folders."""
        if self.is_model_folders(self):
            return self._refreshed
        return self.root_folders._refreshed

    @refreshed.setter
    def refreshed(self, value: t.Any) -> None:
        """Set the refreshed status of the root folders."""
        if self.is_model_folders(self):
            self._refreshed = value
        self.root_folders._refreshed = value

    @property
    def refresh_dt(self) -> datetime.datetime:
        """Get the datetime of last time the root folders were fetched."""
        if self.is_model_folders(self):
            return self._refresh_dt
        return self.root_folders._refresh_dt

    @refresh_dt.setter
    def refresh_dt(self, value: t.Any) -> None:
        """Set the datetime of last time the root folders were fetched."""
        if self.is_model_folders(self):
            self._refresh_dt = value
        self.root_folders._refresh_dt = value

    @property
    def refresh_elapsed(self) -> float:
        """Get the number of seconds since the last time the root folders were fetched."""
        if self.is_model_folders(self):
            return (datetime.datetime.now() - self._refresh_dt).total_seconds()
        return self.root_folders.refresh_elapsed

    @abc.abstractclassmethod
    def get_enum_names(cls) -> BaseEnum:
        """Get the enum containing folder names for this folders object type."""
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_enum_paths(cls) -> BaseEnum:
        """Get the enum containing folder paths for this folders object type."""
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_model_folder(cls) -> t.Type["FolderModel"]:
        """Get the folder model for this folders object type."""
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_model_folders(cls) -> t.Type["FoldersModel"]:
        """Get the folders model for this folders object type."""
        raise NotImplementedError()

    @classmethod
    def get_models_folders(cls) -> t.Tuple[t.Type["Folder"]]:
        """Get all folder models for this folders object type."""
        return (cls.get_model_folder(), cls.get_model_folders())

    @abc.abstractclassmethod
    def get_models_objects(cls) -> t.Tuple[t.Type[BaseModel]]:
        """Get the object models for this folders object type."""
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_model_create_response(cls) -> t.Type[BaseModel]:
        """Get the folder create model for this folders object type."""
        raise NotImplementedError()

    @abc.abstractproperty
    def api_folders(self):
        """Get the folders API for this type of folders."""
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_objects(self, full_objects: bool = FolderDefaults.full_objects):
        """Get the objects for this folders object type."""
        raise NotImplementedError()

    @abc.abstractmethod
    def _create_object(self, **kwargs) -> BaseModel:
        """Create passthru for the object type in question."""
        raise NotImplementedError()

    @classmethod
    def get_types_findable(cls) -> t.Tuple[type]:
        """Get the types that are allowed for `value` in find."""
        return (str, *cls._get_types_findable())

    @classmethod
    def _get_types_findable(cls) -> t.Tuple[type]:
        """Get the types that are allowed for `value` in find."""
        return (cls.get_model_create_response(), *cls.get_models_folders())

    @classmethod
    def is_findable(cls, value: t.Any) -> bool:
        """Get the types that are allowed for `value` in find."""
        return is_str(value) or isinstance(value, cls._get_types_findable())

    @classmethod
    def is_model_folders(cls, value: t.Any) -> bool:
        """Pass."""
        return isinstance(value, cls.get_model_folders())

    @classmethod
    def is_model_folder(cls, value: t.Any) -> bool:
        """Pass."""
        return isinstance(value, cls.get_model_folder())

    @classmethod
    def is_models_objects(cls, value: t.Any) -> bool:
        """Pass."""
        return isinstance(value, cls.get_models_objects())

    @classmethod
    def is_models_folders(cls, value: t.Any) -> bool:
        """Pass."""
        return isinstance(value, cls.get_models_folders())

    # XXX
    """

    FOLDERS API TODO:
        ENSURE SQ/ESET move/copy/delete/rename methods tested

    """

    def get_tree(
        self,
        include_objects: bool = FolderDefaults.include_objects,
        include_details: bool = FolderDefaults.include_details,
        maximum_depth: t.Optional[int] = None,
        as_str: bool = False,
    ) -> t.Union[t.List[str], str]:
        """Get a tree view of all subfolders and their objects.

        Args:
            include_objects (bool, optional): include objects in output
            include_details (bool, optional): show summary or details in output
            maximum_depth (t.Optional[int], optional): print only recursive counts past this depth,
                not the actual subfolders and objects
            as_str (bool, optional): return as str instead of list of str
        """
        items: t.List[str] = [
            self.get_tree_entry(maximum_depth=maximum_depth, include_details=include_details)
        ]
        if not self._is_past_maximum_depth(maximum_depth=maximum_depth):
            if include_objects:
                objs: t.List[BaseModel] = self.get_objects(full_objects=include_details)
                items += self._get_tree_entries_objects_prefix(
                    objs=objs, include_details=include_details
                )
            for folder in self.subfolders:
                items += folder.get_tree(
                    maximum_depth=maximum_depth,
                    include_details=include_details,
                    include_objects=include_objects,
                )
        return "\n".join(items) if as_str else items

    def find(
        self,
        value: t.Union[str, enum.Enum, "Folder", "CreateFolderResponseModel"],
        create: bool = FolderDefaults.create,
        refresh: Refreshables = FolderDefaults.refresh,
        echo: bool = FolderDefaults.echo,
        minimum_depth: t.Optional[int] = None,
        reason: str = "",
    ) -> "Folder":
        """Find a folder.

        Args:
            value (t.Union[str, "Folder", "CreateFolderResponseModel"]): folder to search for
                as str can be: ID, absolute path, or relative path
            create (bool, optional): create folders that do not exist
            refresh (Refreshables, optional): refresh logic, see :meth:`refresh`
            echo (bool, optional): echo output to console
            minimum_depth (t.Optional[int], optional): minimum depth of resolved path
            reason (str, optional): reason for the find
        """
        self = self.refresh(value=refresh)

        if isinstance(value, enum.Enum):
            ret: Folder = self.find_subfolder(value=value, create=create, echo=echo)
        elif is_str(value):
            # try to find by ID of any folder in system
            folder: t.Optional[Folder] = self._get_by_id(value=value)

            if self.is_models_folders(folder):
                ret: Folder = folder
            else:
                # try to find absolute path of any folder OR relative path of subfolder
                ret: Folder = self.find_subfolder(value=value, create=create, echo=echo)
        else:
            # try to find folder by value.id or value
            ret: Folder = self.find_by_id(value=value)

        ret._check_minimum_depth(reason=reason, minimum_depth=minimum_depth)
        return ret

    def get_objects(
        self,
        full_objects: bool = FolderDefaults.full_objects,
        all_objects: bool = FolderDefaults.all_objects,
        recursive: bool = FolderDefaults.recursive,
        refresh: Refreshables = FolderDefaults.refresh,
        **kwargs,
    ) -> t.List[BaseModel]:
        """Get all objects in current folder."""
        refresh = self._parse_refresh(value=refresh)
        if refresh is True:
            self._clear_objects_cache()

        if all_objects:
            return self._get_objects(full_objects=full_objects)

        ret: t.List[BaseModel] = []
        if self.is_model_folder(self):
            ret += [
                x for x in self._get_objects(full_objects=full_objects) if x.folder_id == self.id
            ]

        if recursive:
            for folder in self.subfolders:
                ret += folder.get_objects(
                    full_objects=full_objects,
                    recursive=True,
                    all_objects=False,
                    refresh=False,
                    **kwargs,
                )
        return ret

    def search_objects(
        self,
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
        refresh: Refreshables = FolderDefaults.refresh,
    ) -> t.List[BaseModel]:
        """Pass."""
        # TBD: model out the rest of parsers.search_wip to support this:
        """
        - "test" == obj.name == "test"
        - "name:test" == obj.name == "test"
        - "tags:beta" == any of obj.tags equals "beta"
        - "~test$" == obj.name matches "test$"
        - "name:~test[0-9]demo" == obj.name matches "test[0-9]demo"
        - "name:~test && tags:~^beta" == obj.name matches regex AND any of obj.tags matches "^beta"
        """
        objs: t.List[BaseModel] = self.get_objects(
            all_objects=all_objects, full_objects=full_objects, recursive=recursive, refresh=refresh
        )
        objs_cnt: str = f"{len(objs)} objects"
        objs_args: t.List[str] = [
            f"recursive={recursive}",
            f"all_objects={all_objects}",
            f"error_no_objects={error_no_objects}",
        ]
        objs_args_txt: str = ", ".join(objs_args)
        objs_txt: str = f"Fetched {objs_cnt} from {self._str_under} ({objs_args_txt})"

        if not objs:
            if error_no_objects:
                raise SearchNoObjectsError(f"{objs_txt}")
            self.spew(objs_txt, echo=echo, level="warning")
        else:
            self.spew(objs_txt, echo=echo)

        searches: Searches = Searches(
            objects=objs, values=searches, ignore_case=ignore_case, pattern_prefix=pattern_prefix
        )
        self.spew([f"Loaded {searches}"], echo=echo)

        matches: t.List[BaseModel] = searches.matches
        matches_txt: str = f"{searches.str_matches} (error_no_matches={error_no_matches})"
        matches_errs: t.List[str] = [matches_txt, f"{searches}"]
        self.spew(matches_txt, echo=echo, level="info" if matches else "warning")

        unmatched: t.List[Search] = searches.unmatched
        unmatched_txts: t.List[str] = [
            f"{searches.str_unmatched} (error_unmatched={error_unmatched})",
            *[f" - {x}" for x in unmatched],
        ]
        unmatched_errs: t.List[str] = unmatched_txts
        self.spew(unmatched_txts, echo=echo, level="warning" if searches.unmatched else "debug")

        tree: t.List[str] = [
            "",
            f"{searches.count_objects}:",
            *self._get_tree_entries_objects_prefix(objs=objs),
            "",
        ]

        if not matches:
            if error_no_matches:
                raise SearchNoMatchesError([*matches_errs, *tree, *matches_errs])

        if unmatched:
            if error_unmatched:
                raise SearchUnmatchedError([*unmatched_errs, *tree, *unmatched_errs])

        return matches

    def search_objects_copy(
        self,
        searches: t.List[str],
        path: t.Optional[t.Union[str, FolderBase]] = None,
        copy_prefix: str = FolderDefaults.copy_prefix,
        create: bool = FolderDefaults.create_copy,
        echo: bool = FolderDefaults.echo,
        **kwargs,
    ) -> t.Tuple["Folder", t.List[BaseModel]]:
        """Pass."""
        matches: t.List[BaseModel] = self.search_objects(searches=searches, echo=echo, **kwargs)
        reason: str = f"copy {len(matches)} {self._desc} to {path!r}"
        if path is None:
            path: Folder = self.path_public if self.read_only else self
        else:
            path: Folder = self.find(value=path, create=create, echo=echo, reason=reason)
        results: t.List[BaseModel] = []

        msgs: t.List[str] = [
            f"Starting copy of {len(matches)} from {self._str_under} to {path._str_under}",
        ]
        self.spew(msgs, echo=echo, level="info")
        for idx, match in enumerate(matches):
            old_name: str = match.name
            result: BaseModel = match.copy(path=path, copy_prefix=copy_prefix, refresh=False)
            self.spew(f"Copied {old_name!r} to {result.name!r}", echo=echo)
            results.append(result)
        path.refresh(force=True)
        self.refresh(force=True)
        return path, results

    def search_objects_move(
        self,
        searches: t.List[str],
        path: t.Union[str, enum.Enum, "Folder"],
        create: bool = FolderDefaults.create_move,
        echo: bool = FolderDefaults.echo,
        **kwargs,
    ) -> t.Tuple["Folder", t.List[BaseModel]]:
        """Pass."""
        matches: t.List[BaseModel] = self.search_objects(searches=searches, echo=echo, **kwargs)
        reason: str = f"move {len(matches)} {self._desc} to {path!r}"
        path: Folder = self.find(value=path, create=create, echo=echo, reason=reason)
        results: t.List[BaseModel] = []

        msgs: t.List[str] = [
            f"Starting move of {len(matches)} from {self._str_under} to {path._str_under}",
        ]
        self.spew(msgs, echo=echo, level="info")
        for idx, match in enumerate(matches):
            old_name: str = match.name
            result: BaseModel = match.move(path=path, create=create, echo=echo, refresh=False)
            self.spew(f"Moved {old_name!r} to {result.path!r}", echo=echo)
            results.append(result)
        path.refresh(force=True)
        return path, results

    def search_objects_delete(
        self,
        searches: t.List[str],
        confirm: bool = FolderDefaults.confirm,
        echo: bool = FolderDefaults.echo,
        prompt: bool = FolderDefaults.prompt,
        prompt_default: bool = FolderDefaults.prompt_default,
        **kwargs,
    ) -> t.List[BaseModel]:
        """Pass."""
        matches: t.List[BaseModel] = self.search_objects(searches=searches, echo=echo, **kwargs)
        results: t.List[BaseModel] = []

        msgs: t.List[str] = [
            f"Starting delete of {len(matches)} from {self._str_under}",
            f"confirm={confirm!r}, prompt={prompt!r}, prompt_default={prompt_default!r}",
        ]
        self.spew(msgs, echo=echo, level="info")
        for idx, match in enumerate(matches):
            old_name: str = match.name
            result: BaseModel = match.delete(
                confirm=confirm, echo=echo, prompt=prompt, prompt_default=prompt_default
            )
            self.spew(f"Deleted {old_name!r}", echo=echo)
            results.append(result)

        self.refresh(force=True)
        return results

    def create_object(self, echo: bool = FolderDefaults.echo, **kwargs) -> BaseModel:
        """Create passthru for the object type for this type of folders."""
        if self.is_model_folder(self):
            kwargs.update(dict(folder_id=self.id, path=self))
        created: bool = self._create_object(**kwargs)
        self.spew(msg=f"Created a {created.get_tree_type()}:\n{created}", level="info", echo=echo)
        self.refresh(force=True)
        return created

    def resolve_folder(
        self,
        path: t.Optional[t.Union[str, enum.Enum, "Folder"]] = None,
        create: bool = FolderDefaults.create_path,
        refresh: Refreshables = FolderDefaults.refresh,
        echo: bool = FolderDefaults.echo,
        echo_resolve: bool = FolderDefaults.echo_resolve,
        reason: t.Optional[str] = "",
        minimum_depth: t.Optional[int] = 1,
        default: t.Optional["Folder"] = None,
        fallback: t.Optional["Folder"] = None,
        folder_id: t.Optional[str] = None,
        **kwargs,
    ) -> "FolderModel":
        """Resolve a folder object to use.

        Args:
            path (t.Optional[t.Union[str, "Folder"]], optional): path to resolve
            create (bool, optional): create path if not found
            minimum_depth (t.Optional[int], optional): minimum depth of resolved path
            reason (t.Optional[str], optional): reason for resolve call
            echo (bool, optional): echo output to console
            default_self (bool, optional): default to self if path is not supplied
            folder_id: (t.Optional[str], optional): id of folder to resolve
            kwargs: if path not supplied and default_self is False, determine default
                from private:bool, public:bool, and object type specific traits like
                asset_scope:bool
        """
        attrs: t.List[str] = [
            f"path={path!r}",
            f"fallback={fallback!r}",
            f"default={default!r}",
            f"folder_id={folder_id!r}",
        ]
        # path is a FolderModel, use it
        if self.is_model_folder(path):
            folder: Folder = path
        # folder_id is str, find it
        elif is_str(folder_id):
            folder: Folder = self.find_by_id(value=folder_id)
        # path is a str, find it as a path or uuid
        elif is_str(path) or isinstance(path, enum.Enum):
            folder: Folder = self.find(
                value=path,
                create=create,
                echo=echo,
                reason=reason,
                refresh=refresh,
                minimum_depth=minimum_depth,
            )
        # default supplied
        elif self.is_model_folder(default):
            folder: Folder = default
        # pick a default folder based on kwargs
        else:
            folder: Folder = self.get_default_folder(**kwargs)

        if echo_resolve:
            attrs: str = ", ".join(attrs)
            msgs: t.List[str] = [
                f"Resolved folder from {attrs}",
                f"{folder!r}",
                f"Reason: {reason}",
            ]
            self.spew(msgs, echo=echo)

        # check folder.depth > minimum_depth
        folder._check_minimum_depth(reason=reason, minimum_depth=minimum_depth)

        # do object type specific checks as necessary
        folder = folder._check_resolved_folder(reason=reason, fallback=fallback, **kwargs)

        return folder

    def get_default_folder(self, private: bool = False, **kwargs) -> "FolderModel":
        """Determine default folder to use."""
        if private is True:
            return self.path_private
        return self.path_public

    def move(
        self,
        value: t.Union[str, enum.Enum, "Folder"],
        create: bool = FolderDefaults.create_move,
        refresh: Refreshables = FolderDefaults.refresh,
        echo: bool = FolderDefaults.echo,
    ) -> "FolderModel":
        """Move this folder under some other path.

        Args:
            value (t.Union[str, "Folder"]): path to move this folder to
            create (bool, optional): create value if it does not exist
            refresh (Refreshables, optional): refresh logic, see :meth:`refresh`
            echo (bool, optional): echo output to console
        """
        reason: str = f"move a {self._desc} to {value!r}"

        # check self is not deleted and is not read only
        self._check_update_ok(reason=reason)

        # check self is not /, /Public, /Private
        self._check_minimum_depth(reason=reason, minimum_depth=2)

        # find the value path, creating it if necessary
        value: Folder = self.find(
            value=value, create=create, refresh=refresh, reason=reason, echo=echo
        )

        # check self is not under value
        self._check_under_folder(reason=reason, value=value)

        # check value not deleted and is not read only
        value._check_update_ok(reason=reason)

        # check value is not /
        value._check_minimum_depth(reason=reason, minimum_depth=1)

        # check value does not have a subfolder with same name as this folder
        value._check_subfolder_exists(reason=reason, value=self.name)

        self.spew(f"Issuing an API request to {reason}", echo=False)
        response: MoveFolderResponseModel = self.api_folders._move(id=self.id, parent_id=value.id)
        self.spew([f"Received an API response to {reason}", f"Response: {response}"], echo=echo)

        # refresh self
        self = self.refresh(force=True)
        return self

    def rename(
        self,
        value: str,
        echo: bool = FolderDefaults.echo,
    ) -> "FolderModel":
        """Rename this folder.

        Args:
            value (t.Union[str, "Folder"]): new name for folder
            echo (bool, optional): echo output to console
        """
        reason: str = f"rename a {self._desc} to {value!r}"

        # check value is str
        value: str = self._check_str(value=value, src=self.rename)

        if self.sep in value:
            raise NotAllowedError(
                [
                    f"You can not use {self.sep!r} in a folder name to {reason}",
                    "Please use the move command instead",
                ]
            )

        # check self is not deleted and not read only
        self._check_update_ok(reason=reason)

        # check self is not /, /Public, /Private
        self._check_minimum_depth(reason=reason, minimum_depth=2)

        # check if subfolder exists under parent with same name already
        self.parent._check_subfolder_exists(reason=reason, value=value)

        self.spew(f"Issuing an API request to {reason}", echo=False)
        response: RenameFolderResponseModel = self.api_folders._rename(id=self.id, name=value)
        self.spew([f"Received an API response to {reason}", f"Response: {response}"], echo=echo)

        # refresh self
        self = self.refresh(force=True)
        return self

    def delete(
        self,
        confirm: bool = FolderDefaults.confirm,
        include_subfolders: bool = FolderDefaults.include_subfolders,
        include_objects: bool = FolderDefaults.include_objects_delete,
        echo: bool = FolderDefaults.echo,
        prompt: bool = FolderDefaults.prompt,
        prompt_default: bool = FolderDefaults.prompt_default,
    ) -> DeleteFolderResponseModel:
        """Delete this folder.

        Args:
            confirm (bool, optional): if not True and prompt=False, raise exc
            include_subfolders (bool, optional): if any subfolders exist under this folder,
                if True: delete them, else: raise exc
            include_objects (bool, optional): if any objects exist in this folder,
                if True: delete them, else: raise exc
            echo (bool, optional): echo output to console
            prompt (bool, optional): if confirm is not True, prompt user on console before action
            prompt_default (bool, optional): default value to offer user when prompt is True
        """
        reason: str = f"delete a {self._desc}"

        # check confirm = True
        self._check_confirm(reason=reason, confirm=confirm, prompt=prompt, default=prompt_default)

        # check self is not deleted and not read only
        self._check_update_ok(reason=reason)

        # check self is not /, /Public, /Private
        self._check_minimum_depth(reason=reason, minimum_depth=2)

        # force a refresh of self just to make sure we have the latest data about this folder
        self = self.refresh(force=True)

        # get all objects in this folder
        objs: t.List[BaseModel] = self.get_objects(
            all_objects=False, full_objects=False, recursive=True, refresh=True
        )
        cnt_subs: int = self.count_recursive_subfolders
        cnt_objs: int = len(objs)
        errs: t.List = []

        # if any recursive subfolders, check include_subfolders is True
        if cnt_subs > 0 and include_subfolders is not True:
            errs.append(f"include_subfolders is {include_subfolders} and must be {True}")

        # if any recursive objects exist, check include_objects is True
        if cnt_objs > 0 and include_objects is not True:
            errs.append(f"include_objects is {include_objects} and must be {True}")

        if errs:
            tree: t.List[str] = self.get_tree(include_objects=False, include_details=True)
            errs: t.List[str] = [
                f"Unable to {reason}",
                f"{cnt_subs} subfolders exist recursively under this folder",
                f"{cnt_objs} objects exist recursively under this folder",
                *errs,
            ]
            raise NotAllowedError([*errs, "", *tree, "", *errs])

        self.spew(f"Issuing an API request to {reason}", echo=False)
        response: DeleteFolderResponseModel = self.api_folders._delete(id=self.id)
        self.deleted = True
        self.spew([f"Received an API response to {reason}", f"Response: {response}"], echo=echo)

        # refresh self
        self = self.refresh(force=True)
        return response

    def create(
        self,
        value: str,
        echo: bool = FolderDefaults.echo,
    ) -> "FolderModel":
        """Create a folder under this folder.

        Args:
            value (str): Name of folder to create under this folder
            echo (bool, optional): echo output to console

        """
        reason: str = f"create a subfolder named {value!r} under a {self._desc}"

        # check value is str
        value: str = self._check_str(value=value, src=self.create)

        # if value has '/' in it, treat it as a path
        if self.sep in value:
            return self.find_by_path(value=value, create=True, echo=echo)

        # check if subfolder exists already with same name
        if value in self.subfolders_by_name:
            return self.subfolders_by_name[value]

        # check self is not deleted and is not read only
        self._check_update_ok(reason=reason)

        # check self is not /
        self._check_minimum_depth(reason=reason, minimum_depth=1)

        self.spew(f"Issuing an API request to {reason}", echo=False)
        response: CreateFolderResponseModel = self.api_folders._create(
            name=value, parent_id=self.id
        )
        self.spew([f"Received an API response to {reason}", f"Response: {response}"], echo=echo)

        # get the created folder object
        self = self.refresh(force=True)
        created: Folder = self.root_folders.find(value=response, reason=reason, echo=echo)
        return created

    def find_subfolder(
        self,
        value: t.Union[str, enum.Enum],
        create: bool = FolderDefaults.create,
        echo: bool = FolderDefaults.echo,
    ) -> "Folder":
        """Find a folder under this folder.

        Args:
            value (str): can be name of subfolder, absolute path, or relative path to folder
            create (bool, optional): create folders that do not exist
            echo (bool, optional): echo output to console
        """
        # check value is str
        value: str = self._check_str(value=value, src=self.find_subfolder, enum_ok=True)

        # if / in value, find by path
        if self.sep in value:
            return self.find_by_path(value=value, create=create, echo=echo)

        # see if any subfolders exist that match name or id to value
        for folder in self.subfolders:
            if value in [folder.name, folder.id]:
                return folder

        # no subfolder found with matching name or id
        if create is True:
            return self.create(value=value, echo=echo)

        err: str = f"Subfolder with name or ID of {value!r} {self._str_under} not found"
        raise FolderNotFoundError([err, "", *self.subfolders_summary, err], folder=self)

    def find_by_path(
        self,
        value: t.Union[str, enum.Enum],
        create: bool = FolderDefaults.create,
        echo: bool = FolderDefaults.echo,
    ) -> "Folder":
        """Find a folder by path.

        Args:
            value (str): can be name of subfolder, absolute path, or relative path to folder
            create (bool, optional): create folders that do not exist
            echo (bool, optional): echo output to console
        """
        # check value is str
        value: str = self._check_str(value=value, src=self.find_by_path, enum_ok=True)

        # search under self
        folder: Folder = self

        # search under root folders if value startswith /
        if value.startswith(self.sep):
            folder: Folder = self.root_folders

        # split up the value on / and find each folder
        parts: t.List[str] = self.split(value=value)
        for part in parts:
            folder: Folder = folder.find_subfolder(value=part, create=create, echo=echo)
        return folder

    def find_by_id(
        self,
        value: t.Union[str, "Folder"],
    ) -> "Folder":
        """Find any folder in the system by id.

        Args:
            value (t.Union[str, "Folder"]): as str must be ID of folder

        """
        if not self.is_findable(value=value):
            raise AxonTypeError(
                src=self.find_by_id, attr="value", value=value, expected=self.get_types_findable()
            )

        value_id: str = value
        value_from: str = ""

        if isinstance(value, self._get_types_findable()):
            value_id: str = value.id
            value_from: str = f" (from {value})"

        folder: t.Optional[Folder] = self._get_by_id(value=value_id)

        if self.is_models_folders(folder):
            return folder

        err: str = f"Folder not found by ID {value_id!r}{value_from}"
        raise FolderNotFoundError([err, *self.all_folders_by_id_summary, err], folder=self)

    def echo_tree(self, secho_args: t.Optional[dict] = None, **kwargs) -> None:
        """Tool for echoing out the tree string."""
        secho_args: dict = {} if not isinstance(secho_args, dict) else secho_args
        kwargs["as_str"] = True
        secho_args["message"] = self.get_tree(**kwargs)
        click.secho(**secho_args)

    def get_str(
        self,
        include_details: bool = FolderDefaults.include_details,
        recursive: bool = FolderDefaults.recursive,
    ) -> str:
        """Get a string describing this folder.

        Args:
            include_details (bool, optional): if True, include more details in the output;
                if False, show only identity info
            recursive (bool, optional): if True, include recursive counts in the output;
                if False, show only counts in this folder
        """
        items: t.List[str] = [
            f"read_only={self.read_only!r}",
            f"path={self.path!r}",
            f"depth={self.depth!r}",
        ]
        if recursive:
            items += [
                f"subfolders_recursive={self.count_recursive_subfolders!r}",
                f"objects_recursive={self.count_recursive_objects!r}",
            ]
        else:
            items += [
                f"subfolders={self.count_subfolders!r}",
                f"objects={self.count_objects!r}",
            ]
        if include_details:
            items += [
                f"id={self.id!r}",
                f"type={self.root_type!r}",
                f"created_by={self.created_by_user_source!r}",
                f"created_at={str(self.created_at)!r}",
                f"updated_at={str(self.updated_at)!r}",
            ]
        attrs: str = ", ".join(items)
        ret: str = f"{self.get_tree_type()}({attrs})"
        return ret

    def spew(
        self,
        msg: t.Union[str, t.List[str]],
        echo: bool = FolderDefaults.echo,
        level: str = "debug",
        **kwargs,
    ):
        """Output information to log and console, depending on echo."""
        kwargs["msg"] = msg
        kwargs["do_echo"] = echo
        kwargs["log_level"] = level
        kwargs.setdefault("log", self.logger)
        echoer: t.Callable = get_echoer(level=level)
        echoer(**kwargs)

    @property
    def path_split(self) -> t.List[str]:
        """Get the path parts of self.path."""
        return [x for x in self.path.split(self.sep) if x.strip()]

    @classmethod
    def get_tree_type(cls) -> str:
        """Get the type to use in output of :meth:`get_str`."""
        return cls.__name__.replace("Model", "")

    @property
    def client(self):
        """Get the connect client used."""
        return self.root_folders.HTTP.CLIENT

    @property
    def deleted(self) -> bool:
        """Tracker set by :meth:`delete` after successful deletion."""
        return getattr(self, "_deleted", False)

    @deleted.setter
    def deleted(self, value: bool):
        """Tracker set by :meth:`delete` after successful deletion."""
        if isinstance(value, bool):
            self._deleted = value
            for folder in self.subfolders:
                folder.deleted = value

    @property
    def path_public(self) -> "FolderModel":
        """Get the root of the public folders."""
        return self.root_folders.find_subfolder(value=self.get_enum_names().public)

    @property
    def path_private(self) -> "FolderModel":
        """Get the root of the private folders."""
        return self.root_folders.find_subfolder(value=self.get_enum_names().private)

    @property
    def count_total(self) -> int:
        """Get count of subfolders and objects in this folder."""
        return self.count_subfolders + self.count_objects

    @property
    def count_subfolders(self) -> int:
        """Get the count of subfolders in this folder."""
        ret: int = 0
        ret += len(self.subfolders)
        return ret

    @property
    def count_objects(self) -> int:
        """Get the count of objects in this folder."""
        ret: int = 0
        ret += len(self.get_objects())
        return ret

    @property
    def count_recursive_total(self) -> int:
        """Get recursive count of subfolders and objects beneath this folder."""
        return self.count_recursive_subfolders + self.count_recursive_objects

    @property
    def count_recursive_subfolders(self) -> int:
        """Get the count of folders recursively under this folder."""
        ret: int = 0
        for folder in self.subfolders:
            ret += 1 + folder.count_recursive_subfolders
        return ret

    @property
    def count_recursive_objects(self) -> int:
        """Get the count of objects recursively under this folder."""
        ret: int = 0
        ret += self.count_objects
        for folder in self.subfolders:
            ret += folder.count_recursive_objects
        return ret

    @property
    def all_folders(self) -> t.List["Folder"]:
        """Get a list of all folders in the system."""
        if self.is_model_folders(self):
            return [self, *self.subfolders_recursive]
        return self.root_folders.all_folders

    @property
    def all_folders_by_id(self) -> t.Dict[str, "Folder"]:
        """Get a dict of all folders in the system mapped by id."""
        if self.is_model_folders(self):
            ret: t.Dict[str, Folder] = {self.id: self}
            ret.update(self.subfolders_by_id_recursive)
            return ret
        return self.root_folders.all_folders_by_id

    @property
    def all_folders_by_id_summary(self) -> t.List[str]:
        """Get a list of str of ids of all folders in the system."""
        return [
            "",
            "All folders in system by ID:",
            *[f"{k!r}: {v}" for k, v in self.all_folders_by_id.items()],
            "",
        ]

    @property
    def subfolders(self) -> t.List["Folder"]:
        """Get the subfolders under this folder as Folder objects."""
        return self._load_folders(values=self.children)

    @property
    def subfolders_recursive(self) -> t.List["Folder"]:
        """Get a list of all folders under this folder."""
        ret: t.List[Folder] = []
        for folder in self.subfolders:
            ret += [folder, *folder.subfolders_recursive]
        return ret

    @property
    def subfolders_summary(self) -> t.List[str]:
        """Get a list of str of the names, ids, and paths of folders under this folder."""
        return [f"Folders {self._str_under}:", *[x._str_summary for x in self.subfolders], ""]

    @property
    def subfolders_by_name(self) -> t.Dict[str, "Folder"]:
        """Get a dict of subfolders mapped by name."""
        return {x.name: x for x in self.subfolders}

    @property
    def subfolders_by_id_recursive(self) -> t.Dict[str, "Folder"]:
        """Get a dict of all subfolders recursively mapped by id."""
        ret: t.Dict[str, "Folder"] = {}
        for folder in self.subfolders:
            ret.update({folder.id: folder, **folder.subfolders_by_id_recursive})
        return ret

    @property
    def subfolders_by_path_recursive(self) -> t.Dict[str, "Folder"]:
        """Get a dict of all subfolders recursively mapped by path."""
        ret: t.Dict[str, "Folder"] = {}
        for folder in self.subfolders:
            ret.update({folder.path: folder, **folder.subfolders_by_path_recursive})
        return ret

    @property
    def root(self) -> t.Optional["Folder"]:
        """Get the root of this folder, if any."""
        if is_str(self.root_id):
            return self.find(value=self.root_id)
        if self.is_model_folder(self):
            return self.root_folders

    @property
    def parent(self) -> t.Optional["Folder"]:
        """Get the parent of this folder, if any."""
        if is_str(self.parent_id):
            return self.find(value=self.parent_id)
        if self.is_model_folder(self):
            return self.root_folders

    @property
    def id(self) -> str:
        """Get the ID of this folder."""
        return self._id

    @property
    def created_by_user(self) -> t.Optional[SystemUser]:
        """Get the SystemUser object for self.created_by."""
        if not hasattr(self, "_created_by_user"):
            self._created_by_user: t.Optional[SystemUser] = None
            if is_str(self.created_by):
                self._created_by_user: SystemUser = self.client.system_users.get_cached_single(
                    value=self.created_by
                )
        return self._created_by_user

    @property
    def created_by_user_source(self) -> t.Optional[str]:
        """Get the user name and user source attributes for self.created_by."""
        if isinstance(self.created_by_user, SystemUser):
            return self.created_by_user.user_source
        return None

    def get_tree_entry(
        self,
        maximum_depth: t.Optional[int] = None,
        include_details: bool = FolderDefaults.include_details,
    ) -> str:
        """Get the tree entry for this folder.

        Args:
            maximum_depth (t.Optional[int], optional): if self.depth >= maximum_depth,
                print recursive counts instead of normal counts
            include_details (bool, optional): include more attributes in output
        """
        if self._is_past_maximum_depth(maximum_depth=maximum_depth):
            entry: str = self.get_str(include_details=include_details, recursive=True)
        else:
            entry: str = self.get_str(include_details=include_details, recursive=False)
        return f"{self._tree_prefix_folder}{entry}"

    @classmethod
    def join(cls, *args: t.Any, absolute: bool = True) -> str:
        """Convert ['path', 'a', 'b'] to '/path/a/b'.

        Args:
            *args (t.Any): str or BaseEnum will be added to output
        """
        items: t.List[str] = [""] if absolute else []
        for arg in args:
            if isinstance(arg, str):
                items += cls.split(value=arg)
            if isinstance(arg, BaseEnum):
                items.append(str(arg))
        return cls.sep.join(items)

    def join_under(self, *args: t.Any) -> str:
        """Convert ['a', 'b'] to '/self.path/a/b'.

        Args:
            *args (t.Any): str or BaseEnum will be added to output
        """
        path: str = self.path if self.is_model_folder(self) else self.path_public.path
        return self.join(path, *args)

    @classmethod
    def split(cls, value: str) -> t.List[str]:
        """Convert '/path/a/ b' to ['path','a','b'].

        Args:
            value (str): string to convert

        Returns:
            t.List[str]: value split on cls.sep
        """
        return [x.strip() for x in value.strip().split(cls.sep) if x.strip()]

    @property
    def _str_under(self) -> str:
        """Get a str to use when describing what is under this folder."""
        return f"under path {self.path!r}"

    @property
    def _str_summary(self) -> str:
        """Get a summary string."""
        return f"ID={self.id!r}, Name={self.name!r}"

    def _refetch_root_folders(self) -> "FoldersModel":
        """Refetch the folders data from the API."""
        data: FoldersModel = self.api_folders._get()
        data.refreshed = True
        return data

    def _refresh(self) -> "Folder":
        """Refresh the root folders data."""
        self._clear_objects_cache()
        if self.is_model_folders(self):
            # fetch a new root folders
            root: FoldersModel = self._refetch_root_folders()
            # update root folders references in old root folders
            self.__dict__.update(root.__dict__)
            self.refreshed = True
            return self

        self.root_folders = self.root_folders._refresh()
        if self.deleted is not True:
            # find the updated version of self and update self
            updated: Folder = self.root_folders.find(value=self, refresh=False)
            self.__dict__.update(updated.__dict__)
        return self

    def _parse_refresh(self, value: t.Any = FolderDefaults.refresh, elapsed: bool = True) -> bool:
        """Check if value is True or is int/float and minimum < elapsed >= value."""
        # if bytes, convert to str
        value = bytes_to_str(value=value)

        # try to coerce to bool
        value = coerce_bool(obj=value, error=False)
        if isinstance(value, bool):
            return value

        if elapsed:
            # try to coerce to int or float
            value = coerce_int_float(value=value, error=False, ret_value=True)
            if isinstance(value, (int, float)) and self.refresh_elapsed >= value:
                return True

        return False

    def _get_by_id(self, value: str) -> t.Optional["Folder"]:
        """Get a folder anywhere in the system by ID.

        Args:
            value (str): ID to get

        Returns:
            t.Optional["Folder"]: Folder if ID found, None otherwise
        """
        return self.all_folders_by_id.get(value.strip())

    def _get_tree_entries_objects_prefix(
        self,
        objs: t.List[BaseModel],
        include_details: bool = FolderDefaults.include_details,
    ) -> t.List[str]:
        """Get the tree entries for all objects.

        Args:
            include_details (bool, optional): include more attributes in output
        """
        return [
            f"{self._tree_prefix_object}{x}"
            for x in self._get_tree_entries_objects(objs=objs, include_details=include_details)
        ]

    def _get_tree_entries_objects(
        self,
        objs: t.List[BaseModel],
        include_details: bool = FolderDefaults.include_details,
    ) -> t.List[str]:
        """Get the tree entries for all objects.

        Args:
            include_details (bool, optional): include more attributes in output
        """
        return [x.get_tree_entry(include_details=include_details) for x in objs]

    def _load_folders(
        self, values: t.Union[t.Union[dict, "Folder"], t.List[t.Union[dict, "Folder"]]]
    ) -> t.List["Folder"]:
        """Load list of folder dicts into Folder objects.

        Args:
            values (t.Union[t.Union[dict, "Folder"], t.List[t.Union[dict, "Folder"]]]): list
                of folders to load

        Returns:
            t.List["Folder"]: loaded folders
        """
        model: t.Type[Folder] = self.get_model_folder()

        def load(value: t.Union[dict, "Folder"], idx: int) -> dict:
            if isinstance(value, (dict, model)):
                value: dict = combo_dicts(
                    value.to_dict() if isinstance(value, model) else value,
                    root_folders=self.root_folders,
                )
                return value

            raise AxonTypeError(
                src=self._load_folders,
                attr="value",
                value=value,
                expected=t.Union[dict, Folder],
                extra=f"While in item #{idx + 1} out of {len(values)} items",
            )

        values = listify(values)
        values = [load(value=x, idx=idx) for idx, x in enumerate(values)]
        items: t.List[Folder] = model.schema(many=True).load(values, unknown=marshmallow.INCLUDE)
        return items

    @property
    def _desc(self) -> str:
        """Get a string to use in reasons."""
        return f"Folder named {self.name!r} {self._str_under}"

    @property
    def _tree_prefix_folder(self) -> str:
        """Get the prefix to use in get_tree for folders."""
        return "".join(([self.mark_indent] * (self.depth)) + [self.mark_folder])

    @property
    def _tree_prefix_object(self) -> str:
        """Get the prefix to use in get_tree for objects."""
        return "".join(([self.mark_indent] * self.depth) + [self.mark_object])

    def _check_str(
        self,
        value: t.Any,
        src: t.Any = None,
        attr: str = "value",
        strip: bool = True,
        enum_ok: bool = False,
    ) -> str:
        """Check if a value is a non-empty str."""
        src = self._check_str if src is None else src
        if enum_ok and isinstance(value, enum.Enum):
            value = str(value)
        if not is_str(value):
            raise AxonTypeError(src=src, attr=attr, value=value, expected=str)
        return value.strip() if strip else value

    def _clear_objects_cache(self):
        """Pass."""
        pass

    def _check_confirm(
        self,
        reason: str = "",
        confirm: bool = FolderDefaults.confirm,
        prompt: bool = FolderDefaults.prompt,
        default: bool = FolderDefaults.prompt_default,
        **kwargs,
    ) -> bool:
        """Check if confirm is True.

        Args:
            reason (str, optional): reason for confirmation
            confirm (bool, optional): user supplied value for confirm
            prompt (bool, optional): if True and confirm is not True, prompt user for confirmation
            default (bool, optional): default value to offer user when prompting
            kwargs: passed to :meth:`check_confirm_prompt`
        """
        tree: t.List[str] = self.get_tree(
            include_objects=True, include_details=False, maximum_depth=self.depth + 1
        )
        info: str = self.get_str(include_details=True, recursive=True)
        msgs: t.List[str] = [
            f"Tree {self._str_under}:",
            *tree,
            "",
            f"Current {info}",
            "",
        ]
        return check_confirm_prompt(
            reason=reason,
            src=self,
            msgs=msgs,
            value=confirm,
            prompt=prompt,
            default=default,
            **kwargs,
        )

    def _check_subfolder_exists(self, reason: str = "", value: t.Optional[str] = None):
        """Check if this folder already has a subfolder with same name."""
        if is_str(value):
            if value.strip() in self.subfolders_by_name:
                errs: t.List[str] = [
                    f"Unable to {reason}",
                    f"A subfolder named {value!r} already exists",
                    f"This {self!r}",
                ]
                raise FolderAlreadyExistsError(errs)

    def _check_under_folder(self, reason: str = "", value: t.Optional["Folder"] = None):
        """Check if this folder is under another folder."""
        if self.is_models_folders(value):
            value_path_trimmed: t.List[str] = value.path_split[: len(self.path_split)]
            if value_path_trimmed == self.path_split:
                errs: t.List[str] = [
                    f"Unable to {reason}",
                    f"Target path {value.path!r} is under this path {self.path!r}",
                ]
                raise NotAllowedError([*errs, "", f"This {self}"])

    def _check_update_ok(self, reason: str = ""):
        """Check if this folder can be modified."""
        errs: t.List[str] = []
        if self.deleted is True:
            errs.append("Folder is already deleted")

        if self.read_only is True:
            errs.append("folder is read-only")

        if errs:
            errs = " and ".join(errs)
            raise NotAllowedError([f"Unable to {reason}", errs, "", f"This {self}"])

    def _check_resolved_folder(
        self, reason: str = "", fallback: t.Optional["Folder"] = None, **kwargs
    ) -> "Folder":
        """Check if resolved folder meets object type specific restrictions."""
        return self

    def _check_minimum_depth(self, reason: str = "", minimum_depth: t.Optional[int] = None):
        """Check if this folder is not above a specified minimum depth."""
        if isinstance(minimum_depth, int) and self.depth < minimum_depth:
            depth: str = f"Folder depth of {self.depth}"
            min_depth: str = f"minimum_depth of {minimum_depth}"
            errs: t.List[str] = [
                f"Unable to {reason}" f"{depth} is below {min_depth} for this operation",
            ]
            raise NotAllowedError([*errs, "", f"This {self}"])

    def _is_past_maximum_depth(self, maximum_depth: t.Optional[int] = None) -> bool:
        """Check if this folder is not below a specified maximum depth."""
        return (
            (isinstance(self.depth, int) and self.depth >= 0)
            and (isinstance(maximum_depth, int) and maximum_depth >= 0)
            and self.depth >= maximum_depth
        )

    def __str__(self) -> str:
        """Get a str without details."""
        return self.get_str(include_details=False, recursive=False)

    def __repr__(self) -> str:
        """Get a str with details."""
        return self.get_str(include_details=True, recursive=False)

    def __eq__(self, other: t.Any) -> bool:
        """Check if this folder equals another folder."""
        return other.id == self.id if self.is_models_folders(other) else False


@dataclasses.dataclass(repr=False, eq=False)
class FoldersModel:
    """Dataclass model for response to get folders."""

    folders: t.List[dict]
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    _id: t.ClassVar[str] = "0"
    depth: t.ClassVar[int] = 0
    root_type: t.Optional[str] = None
    name: t.ClassVar[str] = FolderDefaults.sep
    parent_id: t.ClassVar[None] = None
    root_id: t.ClassVar[None] = None
    created_by: t.ClassVar[None] = None
    path: t.ClassVar[str] = FolderDefaults.sep
    read_only: t.ClassVar[bool] = True
    created_at: t.ClassVar[None] = None
    updated_at: t.ClassVar[None] = None
    predefined: t.ClassVar[t.Optional[bool]] = False
    root_folders: t.ClassVar["FoldersModel"] = None
    children_ids: t.ClassVar[t.List[str]] = None
    children: t.ClassVar[t.List[dict]] = None

    _refresh_dt: t.ClassVar[datetime.datetime] = None
    _refreshed: t.ClassVar[bool] = False

    def __post_init__(self):
        """Post."""
        self.root_folders: t.ClassVar["FoldersModel"] = self
        self.refresh_dt: t.ClassVar[datetime.datetime] = datetime.datetime.now()
        self.refreshed: t.ClassVar[bool] = False
        self.children_ids: t.ClassVar[t.List[str]] = [x["_id"] for x in self.folders]
        self.children: t.ClassVar[t.List[dict]] = self.folders


@dataclasses.dataclass(repr=False, eq=False)
class FolderModel:
    """Dataclass model for unmodeled folder objects in FoldersModel."""

    _id: str
    depth: int
    name: str
    root_folders: "FoldersModel" = get_field_dc_mm(mm_field=FoldersSchema)
    root_type: t.Optional[str] = None
    predefined: t.Optional[bool] = False
    path: t.Union[t.List[str], str] = dataclasses.field(default_factory=[])
    created_at: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(), default=None
    )
    updated_at: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(), default=None
    )
    children_ids: t.List[str] = dataclasses.field(default_factory=list)
    children: t.Optional[t.List[dict]] = dataclasses.field(default_factory=list)
    root_id: t.Optional[str] = None
    created_by: t.Optional[str] = None
    parent_id: t.Optional[str] = None
    read_only: bool = False
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Post."""
        if isinstance(self.path, list) and all([isinstance(x, str) for x in self.path]):
            self.path: str = self.sep + self.sep.join(self.path)
