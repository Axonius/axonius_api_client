# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import abc
import dataclasses
import datetime
import enum
import typing as t

import click
import marshmallow
import marshmallow_jsonapi.fields as mm_fields

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
from ....tools import check_confirm_prompt, combo_dicts, is_str, listify, parse_refresh
from ..base import BaseModel
from ..custom_fields import SchemaDatetime, get_field_dc_mm
from ..system_users import SystemUser


class CreateFolderRequestSchema:
    """Marshmallow schema for request to create a folder."""

    name = mm_fields.Str()
    parent_id = mm_fields.Str()


class RenameFolderRequestSchema:
    """Marshmallow schema for request to rename a folder."""

    name = mm_fields.Str()


class MoveFolderRequestSchema:
    """Marshmallow schema for request to move a folder."""

    parent_id = mm_fields.Str()


class FoldersSchema:
    """Marshmallow schema for response to get folders."""

    folders = mm_fields.List(mm_fields.Dict())


# noinspection PyUnresolvedReferences
class FolderDataMixin:
    """Mixins for Metadata responses with 'folder_data' as dict."""

    @property
    def folder_data(self) -> dict:
        """Get the folder_data dict from the creation response metadata."""
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


# noinspection PyUnresolvedReferences
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
        self,
        value: Refreshables = FolderDefaults.refresh,
        force: bool = False,
        root: t.Optional["FoldersModel"] = None,
    ) -> "Folder":
        """Refresh the root folder data.

        Args:
            value (Refreshables, optional): only perform if refresh is True or is
                int/float and elapsed >= refresh.
            force (bool, optional): perform a refresh if force is True
            root (t.Optional["FoldersModel"], optional): dont fetch a new root, use this one yo

        """
        check: bool = self._parse_refresh(value)
        if check is True or force is True:
            return self._refresh(root=root)
        return self

    def _parse_refresh(self, value: Refreshables) -> bool:
        """Parse the refresh value."""
        return parse_refresh(value=value, refresh_elapsed=self.refresh_elapsed)

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

    @classmethod
    @abc.abstractmethod
    def get_enum_names(cls) -> BaseEnum:
        """Get the enum containing folder names for this folders object type."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def get_enum_paths(cls) -> BaseEnum:
        """Get the enum containing folder paths for this folders object type."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def get_model_folder(cls) -> t.Type["FolderModel"]:
        """Get the folder model for this folders object type."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def get_model_folders(cls) -> t.Type["FoldersModel"]:
        """Get the folders model for this folders object type."""
        raise NotImplementedError()

    @classmethod
    def get_models_folders(
        cls,
    ) -> t.Tuple[t.Type[t.Union["Folder", "FoldersModel", "FolderModel"]], ...]:
        """Get all folder models for this folders object type."""
        return (cls.get_model_folder(), cls.get_model_folders())

    @classmethod
    @abc.abstractmethod
    def get_models_objects(cls) -> t.Tuple[t.Type[BaseModel]]:
        """Get the object models for this folders object type."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def get_model_create_response(cls) -> t.Type[BaseModel]:
        """Get the folder create model for this folders object type."""
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def api_folders(self):
        """Get the folders API for this type of folders."""
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_objects(self, full_objects: bool = FolderDefaults.full_objects):
        """Get the objects for this folders object type."""
        raise NotImplementedError()

    @abc.abstractmethod
    def _create_object(self, **kwargs) -> BaseModel:
        """Create pass-thru for the object type in question."""
        raise NotImplementedError()

    @classmethod
    def get_types_findable(cls) -> t.Tuple[type, ...]:
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
        """Check if value is an instance of FoldersModel for this folders object type."""
        return isinstance(value, cls.get_model_folders())

    @classmethod
    def is_model_folder(cls, value: t.Any) -> bool:
        """Check if value is an instance of FolderModel for this folders object type."""
        return isinstance(value, cls.get_model_folder())

    @classmethod
    def is_models_objects(cls, value: t.Any) -> bool:
        """Check if value is an instance of BaseModel for this folders object type."""
        return isinstance(value, cls.get_models_objects())

    @classmethod
    def is_models_folders(cls, value: t.Any) -> bool:
        """Check if value is an instance of Folder for this folders object type."""
        return isinstance(value, cls.get_models_folders())

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

    # noinspection PyMethodFirstArgAssignment
    def find(
        self,
        folder: t.Union[str, enum.Enum, "Folder", "CreateFolderResponseModel"],
        create: bool = FolderDefaults.create,
        refresh: Refreshables = FolderDefaults.refresh,
        echo: bool = FolderDefaults.echo,
        minimum_depth: t.Optional[int] = None,
        reason: str = "",
    ) -> "Folder":
        """Find a folder.

        Args:
            folder (t.Union[str, enum.Enum, "Folder", "CreateFolderResponseModel"]): folder to find
                as any of absolute path, relative path, folder id, folder object
            create (bool, optional): create folders that do not exist
            refresh (Refreshables, optional): refresh logic, see :meth:`refresh`
            echo (bool, optional): echo output to console
            minimum_depth (t.Optional[int], optional): minimum depth of resolved path
            reason (str, optional): reason for the find
        """

        def check(folder):
            folder = folder._check_minimum_depth(reason=reason, minimum_depth=minimum_depth)
            return folder

        self = self.refresh(value=refresh)

        if isinstance(folder, enum.Enum):
            return check(self.find_subfolder(folder=folder, create=create, echo=echo))
        elif is_str(folder):
            # try to find by ID of any folder in system
            if folder.strip() in self.all_folders_by_id:
                return check(self.all_folders_by_id[folder.strip()])
            # try to find absolute path of any folder OR relative path of subfolder
            return check(self.find_subfolder(folder=folder, create=create, echo=echo))

        # try to find folder by folder.id or folder
        return check(self.find_by_id(folder=folder))

    def get_objects(
        self,
        full_objects: bool = FolderDefaults.full_objects,
        all_objects: bool = FolderDefaults.all_objects,
        recursive: bool = FolderDefaults.recursive,
        refresh: Refreshables = FolderDefaults.refresh,
    ) -> t.List[BaseModel]:
        """Get all objects in current folder.

        Args:
            full_objects (bool, optional): get objects with their full data
            all_objects (bool, optional): return all objects in system or only objects in this
                folder directly
            recursive (bool, optional): return all objects under this folder or only objects
                in this folder directly
            refresh (Refreshables, optional): refresh the object cache if this is True
        """
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
    ) -> t.List[object]:
        """Search for objects in this folder.

        Args:
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
            refresh (Refreshables, optional): refresh the folders before searching
        """
        """
        # NEXT: model out the rest of parsers.search_wip to support this:
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

        matches: t.List[object] = searches.matches
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
        folder: t.Optional[t.Union[str, FolderBase]] = None,
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
        refresh: Refreshables = FolderDefaults.refresh,
    ) -> t.Tuple["Folder", t.List[BaseModel]]:
        """Search for objects in a folder and copy them, optionally to a different folder.

        Args:
            searches (t.List[str]): List of object names to search for
            folder (t.Optional[t.Union[str, FolderBase]], optional): optional folder to copy
                objects to
            copy_prefix (str, optional): value to prepend to each objects name
            create (bool, optional): if target is supplied and does not exist, create it
            pattern_prefix (t.Optional[str], optional): if any searches start with
                this prefix, treat the search as a regex
            ignore_case (bool, optional): ignore case when building patterns for searches
                that start with pattern_prefix
            error_unmatched (bool, optional): Throw a fit if any searches supplied have no
                matches
            error_no_matches (bool, optional): Throw a fit if no searches match objects
            error_no_objects (bool, optional): Throw a fit if no objects exist in folder
            recursive (bool, optional): search all objects under folder
            all_objects (bool, optional): search all objects in the entire system
            full_objects (bool, optional): return objects with their full data
            echo (bool, optional): echo output to console
            refresh (Refreshables, optional): refresh the folders before searching
        """
        matches: t.List[object] = self.search_objects(
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
            refresh=refresh,
        )
        matches_cnt: str = f"{len(matches)} matches"
        reason: str = f"copy {matches_cnt} {self._desc} to {folder!r}"
        if folder is None:
            folder: Folder = self.path_public if self.read_only else self
        else:
            folder: Folder = self.find(folder=folder, create=create, echo=echo, reason=reason)
        results: t.List[BaseModel] = []

        msgs: t.List[str] = [
            f"Starting copy of {matches_cnt} from {self._str_under} to {folder._str_under}",
        ]
        self.spew(msgs, echo=echo, level="info")
        for idx, match in enumerate(matches):
            from_path: str = self.join_under(f"/@{match.name}")
            result: BaseModel = match.copy(
                folder=folder, copy_prefix=copy_prefix, root=folder.root_folders
            )
            new_path: str = folder.join_under(f"@{result.name}")
            self.spew(f"Created copy: {new_path!r}\n- From path: {from_path!r}", echo=echo)

            results.append(result)
        folder.refresh(force=True)
        self.refresh(force=True, root=folder.root_folders)
        return folder, results

    def search_objects_move(
        self,
        searches: t.List[str],
        folder: t.Union[str, enum.Enum, "Folder"],
        create: bool = FolderDefaults.create_action,
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
    ) -> t.Tuple["Folder", t.List[BaseModel]]:
        """Search for objects in a folder and move them to another folder.

        Args:
            searches (t.List[str]): List of object names to search for
            folder (t.Union[str, enum.Enum, "Folder"]): folder to move objects to
            create (bool, optional): if folder does not exist, create it
            pattern_prefix (t.Optional[str], optional): if any searches start with
                this prefix, treat the search as a regex
            ignore_case (bool, optional): ignore case when building patterns for searches
                that start with pattern_prefix
            error_unmatched (bool, optional): Throw a fit if any searches supplied have no
                matches
            error_no_matches (bool, optional): Throw a fit if no searches match objects
            error_no_objects (bool, optional): Throw a fit if no objects exist in folder
            recursive (bool, optional): search all objects under folder
            all_objects (bool, optional): search all objects in the entire system
            full_objects (bool, optional): return objects with their full data
            echo (bool, optional): echo output to console
            refresh (Refreshables, optional): refresh the folders before searching

        """
        matches: t.List[BaseModel] = self.search_objects(
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
            refresh=refresh,
        )
        matches_cnt: str = f"{len(matches)} matches"
        reason: str = f"move {matches_cnt} {self._desc} to {folder!r}"
        folder: Folder = self.find(folder=folder, create=create, echo=echo, reason=reason)
        results: t.List[BaseModel] = []

        msgs: t.List[str] = [
            f"Starting move of {matches_cnt} from {self._str_under} to {folder._str_under}",
        ]
        self.spew(msgs, echo=echo, level="info")
        for idx, match in enumerate(matches):
            from_path: str = self.join_under(f"/@{match.name}")
            result: BaseModel = match.move(
                folder=folder, create=create, echo=echo, root=folder.root_folders
            )
            new_path: str = folder.join_under(f"@{result.name}")
            self.spew(f"Moved: {new_path!r}\n- From path: {from_path!r}", echo=echo)
            results.append(result)
        folder.refresh(force=True)
        self.refresh(force=True, root=folder.root_folders)
        return folder, results

    def search_objects_delete(
        self,
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
        echo: bool = FolderDefaults.echo,
        refresh: Refreshables = FolderDefaults.refresh,
    ) -> t.Tuple[t.List[BaseModel], t.List[BaseModel]]:
        """Search for objects in a folder and delete them.

        Args:
            searches (t.List[str]): List of object names to search for
            confirm (bool, optional): Throw a fit if neither confirm nor prompt is True
            prompt (bool, optional): If confirm is not True and prompt is True, prompt user
                to delete each object
            prompt_default (bool, optional): if prompt is True, default choice to use in prompt
            pattern_prefix (t.Optional[str], optional): if any searches start with
                this prefix, treat the search as a regex
            ignore_case (bool, optional): ignore case when building patterns for searches
                that start with pattern_prefix
            error_unmatched (bool, optional): Throw a fit if any searches supplied have no
                matches
            error_no_matches (bool, optional): Throw a fit if no searches match objects
            error_no_objects (bool, optional): Throw a fit if no objects exist in folder
            recursive (bool, optional): search all objects under folder
            all_objects (bool, optional): search all objects in the entire system
            full_objects (bool, optional): return objects with their full data
            echo (bool, optional): echo output to console
            refresh (Refreshables, optional): refresh the folders before searching

        """
        matches: t.List[BaseModel] = self.search_objects(
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
            refresh=refresh,
        )
        results: t.List[BaseModel] = []
        matches_cnt: str = f"{len(matches)} matches"

        msgs: t.List[str] = [
            f"Starting delete of {matches_cnt} from {self._str_under}",
            f"confirm={confirm!r}, prompt={prompt!r}, prompt_default={prompt_default!r}",
        ]
        self.spew(msgs, echo=echo, level="info")
        for idx, match in enumerate(matches):
            from_path: str = self.join_under(f"/@{match.name}")
            result: BaseModel = match.delete(
                confirm=confirm, echo=echo, prompt=prompt, prompt_default=prompt_default
            )
            self.spew(f"Deleted {from_path!r}", echo=echo)
            results.append(result)

        self.refresh(force=True)
        return matches, results

    def create_object(self, echo: bool = FolderDefaults.echo_action, **kwargs) -> BaseModel:
        """Create passthru for the object type for this type of folders."""
        update: dict = {"folder": self}
        kwargs.update(update if self.is_model_folder(self) else {})
        created: bool = self._create_object(**kwargs)
        self.spew(msg=f"Created a {created.get_tree_type()}:\n{created}", level="info", echo=echo)
        self.refresh(force=True)
        return created

    def resolve_folder(
        self,
        folder: t.Optional[t.Union[str, enum.Enum, "Folder"]] = None,
        create: bool = FolderDefaults.create_action,
        refresh: Refreshables = FolderDefaults.refresh_action,
        echo: bool = FolderDefaults.echo_action,
        minimum_depth: t.Optional[int] = 1,
        default: t.Optional["Folder"] = None,
        fallback: t.Optional["Folder"] = None,
        reason: t.Optional[str] = "",
        **kwargs,
    ) -> "FolderModel":
        """Resolve a folder object to use.

        Args:
            folder (t.Optional[t.Union[str, enum.Enum, "Folder"]], optional): folder to resolve
            create (bool, optional): create folder if not found
            refresh (Refreshables, optional): Description
            echo (bool, optional): echo output to console
            minimum_depth (t.Optional[int], optional): minimum depth of resolved folder
            default (t.Optional["Folder"], optional): Description
            fallback (t.Optional["Folder"], optional): Description
            reason (t.Optional[str], optional): reason for resolve call
            kwargs: if folder not supplied and default_self is False, determine default
                from private:bool, public:bool, and object type specific traits like
                asset_scope:bool
        """
        attr_info: t.List[str] = [
            f"folder={folder!r}",
            f"fallback={fallback!r}",
            f"default={default!r}",
        ]
        # folder is a FolderModel, use it
        if self.is_model_folder(folder):
            ret: Folder = folder
            echo = False
        # folder is a str, find it as a folder or uuid
        elif is_str(folder) or isinstance(folder, enum.Enum):
            ret: Folder = self.find(
                folder=folder,
                create=create,
                echo=echo,
                reason=reason,
                refresh=refresh,
                minimum_depth=minimum_depth,
            )
        # default supplied
        elif self.is_model_folder(default):
            ret: Folder = default
        # pick a default folder based on kwargs
        else:
            ret: Folder = self.get_default_folder(**kwargs)

        attr_info: str = ", ".join(attr_info)
        msgs: t.List[str] = [
            f"Resolved folder from {attr_info}",
            f"{ret!r}",
            f"Reason: {reason}",
        ]
        self.spew(msgs, echo=echo)

        # check folder.depth > minimum_depth
        ret = ret._check_minimum_depth(reason=reason, minimum_depth=minimum_depth)
        # do object type specific checks as necessary
        ret = ret._check_resolved_folder(reason=reason, fallback=fallback, **kwargs)
        return ret

    def get_default_folder(self, private: bool = False, **kwargs) -> "FolderModel":
        """Determine default folder to use."""
        if private is True:
            return self.path_private
        return self.path_public

    def move(
        self,
        folder: t.Union[str, enum.Enum, "Folder"],
        create: bool = FolderDefaults.create_action,
        refresh: Refreshables = FolderDefaults.refresh_action,
        echo: bool = FolderDefaults.echo_action,
    ) -> "FolderModel":
        """Move this folder under some other path.

        Args:
            folder (t.Union[str, enum.Enum, "Folder"]): path to move this folder to
            create (bool, optional): create folder if it does not exist
            refresh (Refreshables, optional): refresh logic, see :meth:`refresh`
            echo (bool, optional): echo output to console
        """
        reason: str = f"move a {self._desc} to {folder!r}"

        # check self is not deleted and is not read only
        self._check_update_ok(reason=reason)

        # check self is not /, /Public, /Private
        self._check_minimum_depth(reason=reason, minimum_depth=2)

        # find the folder path, creating it if necessary
        folder: Folder = self.find(
            folder=folder, create=create, refresh=refresh, reason=reason, echo=echo
        )

        # check self is not under folder
        self._check_under_folder(reason=reason, value=folder)

        # check folder not deleted and is not read only
        folder._check_update_ok(reason=reason)

        # check folder is not /
        folder = folder._check_minimum_depth(reason=reason, minimum_depth=1)

        # check folder does not have a subfolder with same name as this folder
        folder._check_subfolder_exists(reason=reason, value=self.name)

        self.spew(f"Issuing an API request to {reason}", echo=False)
        response: MoveFolderResponseModel = self.api_folders._move(id=self.id, parent_id=folder.id)
        self.spew([f"Received an API response to {reason}", f"Response: {response}"], echo=echo)

        # refresh self
        self = self.refresh(force=True)
        return self

    def rename(self, folder: str, echo: bool = FolderDefaults.echo_action) -> "FolderModel":
        """Rename this folder.

        Args:
            folder (str): new name for folder
            echo (bool, optional): echo output to console

        """
        reason: str = f"rename a {self._desc} to {folder!r}"

        # check folder is str
        folder: str = self._check_str(value=folder, attr="folder", src=self.rename)

        if self.sep in folder:
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
        self.parent._check_subfolder_exists(reason=reason, value=folder)

        self.spew(f"Issuing an API request to {reason}", echo=False)
        response: RenameFolderResponseModel = self.api_folders._rename(id=self.id, name=folder)
        self.spew([f"Received an API response to {reason}", f"Response: {response}"], echo=echo)

        # refresh self
        self = self.refresh(force=True)
        return self

    def delete(
        self,
        confirm: bool = FolderDefaults.confirm,
        delete_subfolders: bool = FolderDefaults.delete_subfolders,
        delete_objects: bool = FolderDefaults.delete_objects,
        echo: bool = FolderDefaults.echo,
        prompt: bool = FolderDefaults.prompt,
        prompt_default: bool = FolderDefaults.prompt_default,
    ) -> DeleteFolderResponseModel:
        """Delete this folder.

        Args:
            confirm (bool, optional): if not True and prompt=False, raise exc
            delete_subfolders (bool, optional): if any subfolders exist under this folder,
                if True: delete them, else: raise exc
            delete_objects (bool, optional): if any objects exist in this folder,
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

        # if any recursive subfolders, check delete_subfolders is True
        if cnt_subs > 0 and delete_subfolders is not True:
            errs.append(f"delete_subfolders is {delete_subfolders} and must be {True}")

        # if any recursive objects exist, check delete_objects is True
        if cnt_objs > 0 and delete_objects is not True:
            errs.append(f"delete_objects is {delete_objects} and must be {True}")

        if errs:
            tree: t.List[str] = self.get_tree(include_objects=True, include_details=True)
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

    def create(self, folder: str, echo: bool = FolderDefaults.echo_action) -> "FolderModel":
        """Create a folder under this folder.

        Args:
            folder (str): Name of folder to create under this folder
            echo (bool, optional): echo output to console

        """
        reason: str = f"create a subfolder named {folder!r} under a {self._desc}"

        # check folder is str
        folder: str = self._check_str(value=folder, attr="folder", src=self.create)

        # if folder has '/' in it, treat it as a path
        if self.sep in folder:
            return self.find_by_path(folder=folder, create=True, echo=echo)

        # check if subfolder exists already with same name
        if folder in self.subfolders_by_name:
            return self.subfolders_by_name[folder]

        # check self is not deleted and is not read only
        self._check_update_ok(reason=reason)

        # check self is not /
        self._check_minimum_depth(reason=reason, minimum_depth=1)

        self.spew(f"Issuing an API request to {reason}", echo=False)
        response: CreateFolderResponseModel = self.api_folders._create(
            name=folder, parent_id=self.id
        )
        self.spew([f"Received an API response to {reason}", f"Response: {response}"], echo=echo)

        # get the created folder object
        self = self.refresh(force=True)
        created: Folder = self.root_folders.find(folder=response, reason=reason, echo=echo)
        return created

    def find_subfolder(
        self,
        folder: t.Union[str, enum.Enum],
        create: bool = FolderDefaults.create,
        echo: bool = FolderDefaults.echo,
    ) -> "Folder":
        """Find a folder under this folder.

        Args:
            folder (str): can be name of subfolder, absolute path, or relative path to folder
            create (bool, optional): create folders that do not exist
            echo (bool, optional): echo output to console
        """
        # check folder is str
        folder: str = self._check_str(
            value=folder, attr="folder", src=self.find_subfolder, enum_ok=True
        )

        # if / in folder, find by path
        if self.sep in folder:
            return self.find_by_path(folder=folder, create=create, echo=echo)

        # see if any subfolders exist that match name or id to folder
        for subfolder in self.subfolders:
            if folder in [subfolder.name, subfolder.id]:
                return subfolder

        # no subfolder found with matching name or id
        if create is True:
            return self.create(folder=folder, echo=echo)

        err: str = f"Subfolder with name or ID of {folder!r} {self._str_under} not found"
        raise FolderNotFoundError([err, "", *self.subfolders_summary, err], folder=self)

    def find_by_path(
        self,
        folder: t.Union[str, enum.Enum],
        create: bool = FolderDefaults.create,
        echo: bool = FolderDefaults.echo,
    ) -> "Folder":
        """Find a folder by path.

        Args:
            folder (str): can be name of subfolder, absolute path, or relative path to folder
            create (bool, optional): create folders that do not exist
            echo (bool, optional): echo output to console
        """
        # check folder is str
        folder: str = self._check_str(
            value=folder, attr="folder", src=self.find_by_path, enum_ok=True
        )

        # search under self
        ret: Folder = self

        # search under root folders if folder startswith /
        if folder.startswith(self.sep):
            ret: Folder = self.root_folders

        # split up the folder on / and find each subfolder recursively
        parts: t.List[str] = self.split(value=folder)
        for part in parts:
            ret: Folder = ret.find_subfolder(folder=part, create=create, echo=echo)
        return ret

    def find_by_id(self, folder: t.Union[str, "Folder"]) -> "Folder":
        """Find any folder in the system by id.

        Args:
            folder (t.Union[str, "Folder"]): as str must be ID of folder

        """
        if not self.is_findable(value=folder):
            raise AxonTypeError(
                src=self.find_by_id, attr="folder", value=folder, expected=self.get_types_findable()
            )

        value_id: str = folder
        value_from: str = ""

        if isinstance(folder, self._get_types_findable()):
            value_id: str = folder.id
            value_from: str = f" (from {folder})"

        if value_id.strip() in self.all_folders_by_id:
            return self.all_folders_by_id[value_id.strip()]

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
        return self.root_folders.find_subfolder(folder=self.get_enum_names().public)

    @property
    def path_private(self) -> "FolderModel":
        """Get the root of the private folders."""
        return self.root_folders.find_subfolder(folder=self.get_enum_names().private)

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
            return self.find(folder=self.root_id)
        if self.is_model_folder(self):
            return self.root_folders

    @property
    def parent(self) -> t.Optional["Folder"]:
        """Get the parent of this folder, if any."""
        if is_str(self.parent_id):
            return self.find(folder=self.parent_id)
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
        """Get the username and user source attributes for self.created_by."""
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

    def _refresh(self, root: t.Optional["FoldersModel"] = None) -> "Folder":
        """Refresh the root folder data."""
        self._clear_objects_cache()
        if self.is_model_folders(self):
            root: FoldersModel = (
                root if self.is_model_folders(root) else self._refetch_root_folders()
            )
            # update root folders references in old root folders
            self.__dict__.update(root.__dict__)
            self.refreshed = True
            return self

        self.root_folders = self.root_folders._refresh(root=root)
        if self.deleted is not True:
            # find the updated version of self and update self
            updated: Folder = self.root_folders.find(folder=self, refresh=False)
            self.__dict__.update(updated.__dict__)
        return self

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
        items: t.List[Folder] = model.schema(many=True, unknown=marshmallow.INCLUDE).load(
            values, unknown=marshmallow.INCLUDE
        )
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
        """Clear any object specific cache being used."""
        return

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

    def _check_minimum_depth(
        self,
        reason: str = "",
        minimum_depth: t.Optional[int] = None,
        fallback: t.Optional["Folder"] = None,
    ) -> "Folder":
        """Check if this folder is not above a specified minimum depth."""
        if isinstance(minimum_depth, int) and self.depth < minimum_depth:
            depth: str = f"Folder depth of {self.depth}"
            min_depth: str = f"minimum_depth of {minimum_depth}"
            errs: t.List[str] = [
                f"Unable to {reason}" f"{depth} is below {min_depth} for this operation",
            ]
            msgs: t.List[str] = [*errs, "", f"This {self}"]
            if self.is_model_folder(fallback):
                self.spew(msgs, echo=True)
                return fallback
            raise NotAllowedError(msgs)
        return self

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
    path: t.Union[t.List[str], str] = dataclasses.field(default_factory=list)
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
