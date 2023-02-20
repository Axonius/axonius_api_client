# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow
import marshmallow_jsonapi

from ...data import BaseEnum
from ...exceptions import (
    AxonTypeError,
    FolderAlreadyExistsError,
    FolderNotFoundError,
    NotAllowedError,
)
from ...tools import bytes_to_str, coerce_bool, coerce_int_float, combo_dicts, is_str, listify
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaDatetime, get_field_dc_mm
from .generic import Metadata, MetadataSchema
from .saved_queries import SavedQuery
from .system_users import SystemUser

SEP: str = "/"
ALL_ID: str = "all"
REFRESH: int = 60
Findables = t.Union[str, "FolderBase", "CreateFolderResponse"]
Loadables = t.Union[dict, "Folder"]
Refreshables = t.Optional[t.Union[str, bytes, int, float, bool]]


class FolderNames(BaseEnum):
    """Names of built-in folders used in Axonius."""

    public: str = "Shared Queries"
    private: str = "My Private Queries"
    asset_scope: str = "Asset Scope Queries"
    predefined: str = "Predefined Queries"
    untitled: str = "untitled folder"


class FolderPaths(BaseEnum):
    """Paths of built-in folders used in Axonius."""

    public: str = SEP.join(["", FolderNames.public.value])
    predefined: str = SEP.join(["", FolderNames.public.value, FolderNames.predefined.value])


class RootTypes(BaseEnum):
    """Types of root folders used in Axonius."""

    public: str = "PUBLIC"
    private: str = "PRIVATE"
    asset_scope: str = "ASSET_SCOPE"


class RootNames(BaseEnum):
    """Titles of built-in folders used in Axonius mapped to their root type."""

    public: str = FolderNames.public.value
    private: str = FolderNames.private.value
    asset_scope: str = FolderNames.asset_scope.value


class CreateFolderSchema(BaseSchemaJson):
    """Marshmallow schema for request to create folder."""

    name = marshmallow_jsonapi.fields.Str()
    parent_id = marshmallow_jsonapi.fields.Str()

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return CreateFolder

    class Meta:
        """Pass."""

        type_ = "folders_request_schema"


@dataclasses.dataclass(repr=False)
class CreateFolder(BaseModel):
    """Dataclass model for request to create folder."""

    name: str = get_field_dc_mm(mm_field=CreateFolderSchema._declared_fields["name"])
    parent_id: str = get_field_dc_mm(mm_field=CreateFolderSchema._declared_fields["parent_id"])

    @staticmethod
    def get_schema_cls() -> t.Optional[t.Type[BaseSchema]]:
        """Pass."""
        return CreateFolderSchema


class CreateFolderResponseSchema(MetadataSchema):
    """Marshmallow schema for response to create folder."""

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return CreateFolderResponse


@dataclasses.dataclass
class CreateFolderResponse(Metadata):
    """Dataclass model for response to create folder."""

    @property
    def folder_data(self) -> dict:
        """Get the folder_data dict from the create response metadata."""
        return self.document_meta["folder_data"]

    @property
    def id(self) -> str:
        """Get the ID of the created folder."""
        return self.folder_data["_id"]

    @property
    def parent_id(self) -> str:
        """Get the parent ID of the created folder."""
        return self.folder_data["parent_id"]

    @property
    def name(self) -> str:
        """Get the name of the created folder."""
        return self.folder_data["name"]

    @property
    def message(self) -> str:
        """Get the status message."""
        return self.document_meta["message"]

    @staticmethod
    def get_schema_cls() -> t.Optional[t.Type[BaseSchema]]:
        """Pass."""
        return CreateFolderResponseSchema

    def __str__(self) -> str:
        """Pass."""
        items: t.List[str] = [
            f"id={self.id!r}",
            f"parent_id={self.parent_id!r}",
            f"name={self.name!r}",
            f"message={self.message!r}",
        ]
        items: str = ", ".join(items)
        return f"{self.__class__.__name__}({items})"


class DeleteFolderResponseSchema(MetadataSchema):
    """Marshmallow schema for response to create folder."""

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return DeleteFolderResponse


@dataclasses.dataclass
class DeleteFolderResponse(Metadata):
    """Dataclass model for response to create folder."""

    @property
    def id(self) -> str:
        """Get the ID of the created folder."""
        return self.document_meta["folder_id"]

    def message(self) -> str:
        """Get the status message."""
        return self.document_meta["message"]

    @staticmethod
    def get_schema_cls() -> t.Optional[t.Type[BaseSchema]]:
        """Pass."""
        return DeleteFolderResponseSchema

    def __str__(self) -> str:
        """Pass."""
        items: t.List[str] = [
            f"id={self.id!r}",
            f"message={self.message!r}",
        ]
        items: str = ", ".join(items)
        return f"{self.__class__.__name__}({items})"


class RootFoldersSchema(BaseSchemaJson):
    """Marshmallow schema for response to get folders."""

    folders = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return RootFolders

    class Meta:
        """Pass."""

        type_ = "folders_response_schema"


class FolderBase:
    """Container of mixins used by RootFolders and Folders."""

    sep: t.ClassVar[str] = SEP
    mark_folder: t.ClassVar[str] = f"{sep} "
    mark_object: t.ClassVar[str] = "@ "
    mark_indent: t.ClassVar[str] = "| "

    # XXX copy(value: str, objects: bool = True)
    # XXX move(value: str)
    # XXX rename(value: str)

    def delete(
        self,
        delete_subfolders: bool = False,
        delete_objects: bool = False,
        refresh: Refreshables = REFRESH,
    ) -> DeleteFolderResponse:
        """Pass."""
        desc: str = f"Folder named {self.name!r} {self.str_under}"
        pre: str = f"Unable to delete a {desc}"

        # check that this folder is not read only
        if self.read_only:
            raise NotAllowedError([pre, "Folder is read-only", f"{self!r}"])

        # check that this folder is not at root level
        if not self.depth > 1:
            raise NotAllowedError(
                [pre, f"Folder is a root folder (depth={self.depth})", f"{self!r}"]
            )

        self = self.refresh(refresh=refresh)

        # if any recursive subfolders or objects exist
        # check that we have been specifically told to delete them
        if (self.count_recursive_subfolders and delete_subfolders is not True) or (
            self.count_recursive_objects and delete_objects is not True
        ):
            tree: t.List[str] = self.get_tree(include_objects=True)
            errs: t.List[str] = [
                pre,
                "",
                self.str_count_recursive_subfolders,
                f"delete_subfolders is {delete_subfolders}",
                "",
                self.str_count_recursive_objects,
                f"delete_objects is {delete_objects}",
            ]
            raise NotAllowedError([*errs, "", *tree, "", *errs])

        self.logger.info(f"Deleting {self!r}")
        # issue the API call to delete the folder and all of its objects
        response: DeleteFolderResponse = self._client.folders._delete(id=self.id)
        self.logger.info(f"Deleted {self!r}: {response}")

        # remove the parent reference to self
        self.parent.children = [x for x in self.parent.children if x["_id"] != self.id]
        return response

    def create(
        self,
        value: str,
        refresh: Refreshables = REFRESH,
    ) -> "Folder":
        """Create a folder.

        Examples:
            >>> # create a folder under the public folders, method 1
            >>> root_folders = client.folders.get()
            >>> root_folder = root_folders.root_public
            >>> folder = root_folder.create(value='badwolf1')
            >>> print(folder)
            Folder(path='Shared Queries/badwolf1', depth=2, count_folders=0, count_objects=0)

            >>> # create a folder under the public folders, method 2
            >>> root_folders = client.folders.get()
            >>> folder = root_folders.create(value='/Shared Queries/badwolf1')
            >>> print(folder)
            Folder(path='Shared Queries/badwolf1', depth=2, count_folders=0, count_objects=0)

        Args:
            value (str): Name of folder to create under this folder
            refresh (Refreshables, optional): See :meth:`refresh`

        No Longer Returned:
            Folder: Newly created folder

        No Longer Raises:
            FolderAlreadyExistsError: If a folder with the name in value already exists
            AxonTypeError: If value is not a string
        """
        if not is_str(value):
            raise AxonTypeError(obj=self.create, attr="value", value=value, expected=str)

        self = self.refresh(refresh=refresh)

        value: str = value.strip()

        if self.sep in value:
            # value has '/' in it, treat it as a path
            return self.find_by_path(value=value, create=True)

        desc: str = f"Folder named {value!r} {self.str_under}"

        # check that this folder is not read only
        if self.read_only:
            raise NotAllowedError(f"Unable to create a {desc}, {self.name!r} is read-only")

        existing: t.Optional[Folder] = self.subfolders_by_name.get(value)
        if isinstance(existing, Folder):
            # it already exists as the name of any sub-folder directly under this folder
            raise FolderAlreadyExistsError(
                msg=[f"{desc} already exists:", f"{existing!r}"], folder=existing
            )

        self.logger.info(f"Creating a {desc}")

        # issue the API call to create the folder
        response: CreateFolderResponse = self._client.folders._create(name=value, parent_id=self.id)

        # get the created folder object
        created: Folder = self.find(value=response, refresh=True)
        return created

    def find(
        self, value: Findables, create: bool = False, refresh: Refreshables = REFRESH
    ) -> "FolderBase":
        """Find a folder.

        Notes:
            If value is a string, it can be any of:
            * a valid ID of any folder in the system
            * an absolute path of any folder in the system
            * a relative path of any subfolder under this folder

        Args:
            value (t.Union[str, "FolderBase", CreateFolderResponse]): folder to search for
            create (bool, optional): create folder if it does not exist
        """
        if not isinstance(value, self._findables()):
            raise AxonTypeError(
                obj=self.find, attr="value", value=value, expected=self._findables()
            )

        self = self.refresh(refresh=refresh)

        folder: t.Optional[FolderBase] = None
        if is_str(value):
            # try to find by ID of any folder in system
            folder: t.Optional[FolderBase] = self._find_by_id(value=value)

            if not isinstance(folder, FolderBase):
                # try to find absolute path of any folder OR relative path of subfolder
                folder: Folder = self.find_subfolder(value=value, create=create)
        else:
            # try to find folder by value.id
            folder: Folder = self.find_by_id(value=value)
        return folder

    def find_subfolder(
        self, value: str, create: bool = False, refresh: Refreshables = REFRESH
    ) -> "Folder":
        """Pass."""
        if not is_str(value):
            raise AxonTypeError(obj=self.find_subfolder, attr="value", value=value, expected=str)

        self = self.refresh(refresh=refresh)

        value: str = value.strip()
        if self.sep in value:
            return self.find_by_path(value=value, create=create)

        for folder in self.subfolders:
            if value in [folder.name, folder.id]:
                return folder

        if create:
            return self.create(value=value)

        err: str = f"Subfolder with name or ID of {value!r} {self.str_under} not found"
        raise FolderNotFoundError(msg=[err, "", *self.subfolders_summary, err], folder=self)

    def find_by_path(
        self, value: str, create: bool = False, refresh: Refreshables = REFRESH
    ) -> "FolderBase":
        """Pass."""
        if not is_str(value):
            raise AxonTypeError(obj=self.find_by_path, attr="value", value=value, expected=str)

        self = self.refresh(refresh=refresh)
        value: str = value.strip()

        # look under current folder by default
        current: t.Union[RootFolders, Folder] = self
        if value.startswith(self.sep):
            # if path is absolute, look under root folders
            current: RootFolders = self.root_folders

        current_under: str = current.str_under
        parts: t.List[str] = self._split_path(value=value)
        parts_cnt: int = len(parts)
        for idx, part in enumerate(parts):
            if not part.strip():
                continue

            part_info: str = (
                f"path part {part!r} ({idx + 1} of {parts_cnt} from value {value})"
                f" {current_under}"
            )

            self.logger.info(f"Looking for {part_info}")

            try:
                current: Folder = current.find_subfolder(value=part, create=False)
            except FolderNotFoundError:
                self.logger.info(f"Did not find {part_info}, create={create}", exc_info=True)
                if not create:
                    raise
                current = current.create(value=part)
                self.logger.info(f"Created {part_info}")
            else:
                self.logger.info(f"Found {part_info}")
                current_under: str = current.str_under

        return current

    def find_by_id(self, value: Findables, refresh: Refreshables = REFRESH) -> "FolderBase":
        """Pass."""
        check: Findables = value
        check_from: str = ""

        if isinstance(value, (FolderBase, CreateFolderResponse)):
            check: str = value.id
            check_from: str = f" (from {value})"

        if not is_str(check):
            raise AxonTypeError(
                obj=self.find_by_id, attr="value", value=check, expected=self._findables()
            )

        self = self.refresh(refresh=refresh)

        folder: t.Optional[FolderBase] = self._find_by_id(value=check)

        if isinstance(folder, FolderBase):
            return folder

        err: str = f"Folder not found by ID {check!r}{check_from}"
        raise FolderNotFoundError(msg=[err, *self.all_folders_by_id_summary, err], folder=self)

    def refetch(self) -> "RootFolders":
        """Pass."""
        return self._client.folders._get()

    def refresh(self, refresh: Refreshables = REFRESH) -> "FolderBase":
        """Pass."""
        check: Refreshables = refresh

        if isinstance(check, (str, bytes)):
            try:
                # if bytes, convert to str
                check = bytes_to_str(value=check)
                # try to coerce to int or float
                check = coerce_int_float(value=check, error=False, ret_value=True)
                # try to coerce to bool
                check = coerce_bool(obj=check, error=False)
            except Exception:
                pass

        if isinstance(check, (int, float)) and check > 1 and self.refresh_elapsed >= check:
            check = True

        if check is True:
            # fetch a new root_folders
            root_folders: RootFolders = self.refetch()

            # update root_folders references
            self.root_folders.root_folders.__dict__ = root_folders.__dict__
            self.root_folders.__dict__ = root_folders.__dict__

            # find the updated version of self
            updated: FolderBase = root_folders.find(self)

            # update self
            self.__dict__ = updated.__dict__

        return self

    def get_objects(
        self,
        include_usage: bool = False,
        include_view: bool = False,
    ) -> t.List[SavedQuery]:
        """Get all objects in current folder.

        Args:
            include_usage (bool, optional): When fetching queries, include usage field
            include_view (bool, optional): When fetching queries, include view field
        """
        ret: t.List[SavedQuery] = []
        ret += self.get_queries(include_usage=include_usage, include_view=include_view)
        return ret

    def get_queries(
        self,
        include_usage: bool = False,
        include_view: bool = False,
    ) -> t.List[SavedQuery]:
        """Get all queries objects in current folder.

        Args:
            include_usage (bool, optional): When fetching queries, include usage field
            include_view (bool, optional): When fetching queries, include view field
        """
        ret: t.List[SavedQuery] = []
        if not isinstance(self, RootFolders):
            data: t.List[SavedQuery] = self._client.folders.get_queries_cached(
                include_usage=include_usage, include_view=include_view
            )
            ret += [x for x in data if x.folder_id == self.id]
        return ret

    def get_tree(
        self,
        max_depth: t.Optional[int] = None,
        include_objects: bool = False,
        include_details: bool = False,
    ) -> t.List[str]:
        """Get a tree view of all subfolders and their objects.

        Args:
            max_depth (t.Optional[int], optional): print only recursive counts past this depth,
                not the actual folders and objects
            include_objects (bool, optional): include objects in output
            include_details (bool, optional): show summary or details in output
        """
        items: t.List[str] = [
            self._get_tree_entry(max_depth=max_depth, include_details=include_details)
        ]
        if not self._check_max_depth(max_depth=max_depth):
            if include_objects:
                items += self._get_tree_entries_objects(include_details=include_details)
            for folder in self.subfolders:
                items += folder.get_tree(
                    max_depth=max_depth,
                    include_details=include_details,
                    include_objects=include_objects,
                )
        return items

    def get_str(self, include_details: bool = False, recursive: bool = False) -> str:
        """Pass."""
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
        ret: str = f"{self.__class__.__name__}({attrs})"
        return ret

    @property
    def refresh_elapsed(self) -> float:
        """Get the number of seconds since the last time this data was fetched."""
        return (datetime.datetime.now() - self.root_folders.refresh_dt).total_seconds()

    @property
    def is_public(self) -> bool:
        """Pass."""
        return self.root_type == RootTypes.public.value

    @property
    def is_private(self) -> bool:
        """Pass."""
        return self.root_type == RootTypes.private.value

    @property
    def is_asset_scope(self) -> bool:
        """Pass."""
        return self.root_type == RootTypes.asset_scope.value

    @property
    def root_public(self) -> "Folder":
        """Get the root of the public folders."""
        return self.root_folders.find_subfolder(value=FolderNames.public.value)

    @property
    def root_private(self) -> "Folder":
        """Get the root of the private folders."""
        return self.root_folders.find_subfolder(value=FolderNames.private.value)

    @property
    def root_asset_scope(self) -> "Folder":
        """Get the root of the asset scope folders."""
        return self.root_folders.find_subfolder(value=FolderNames.asset_scope.value)

    @property
    def count(self) -> int:
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
        ret += self.count_queries
        return ret

    @property
    def count_queries(self) -> int:
        """Get the count of query objects in this folder."""
        ret: int = 0
        ret += len(self.get_queries())
        return ret

    @property
    def count_recursive(self) -> int:
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
    def count_recursive_queries(self) -> int:
        """Get the count of query objects recursively under this folder."""
        ret: int = 0
        ret += self.count_queries
        for folder in self.subfolders:
            ret += folder.count_recursive_queries
        return ret

    @property
    def all_folders_by_id(self) -> t.Dict[str, "FolderBase"]:
        """Get a dict of all folders in the system mapped by id."""
        if isinstance(self, RootFolders):
            ret: t.Dict[str, FolderBase] = {self.id: self}
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
    def subfolders_summary(self) -> t.List[str]:
        """Get a list of str of the names, ids, and paths of folders under this folder."""
        return [f"Folders {self.str_under}:", *[x.str_summary for x in self.subfolders], ""]

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
    def root(self) -> t.Optional[t.Union["RootFolders", "Folder"]]:
        """Get the root of this folder, if any."""
        if is_str(self.root_id):
            return self.find(value=self.root_id)
        if isinstance(self, Folder):
            return self.root_folders

    @property
    def parent(self) -> t.Optional[t.Union["RootFolders", "Folder"]]:
        """Get the parent of this folder, if any."""
        if is_str(self.parent_id):
            return self.find(value=self.parent_id)
        if isinstance(self, Folder):
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
                self._created_by_user: SystemUser = self._client.system_users.get_cached_single(
                    value=self.created_by
                )
        return self._created_by_user

    @property
    def created_by_user_source(self) -> t.Optional[str]:
        """Get the user name and user source attributes for self.created_by."""
        if isinstance(self.created_by_user, SystemUser):
            return self.created_by_user.user_source
        return None

    @property
    def str_under(self) -> str:
        """Get a str to use when describing what is under this folder."""
        return f"under path {self.path!r}"

    @property
    def str_summary(self) -> str:
        """Get a summary string."""
        return f"ID={self.id!r}, Name={self.name!r}"

    @property
    def str_count_recursive_subfolders(self) -> str:
        """Get a str for the recursive count of folders."""
        return f"{self.count_recursive_subfolders} subfolders exist recursively under this folder."

    @property
    def str_count_recursive_objects(self) -> str:
        """Get a str for the recursive count of folders."""
        return f"{self.count_recursive_objects} objects exist recursively under this folder."

    def _find_by_id(self, value: str) -> t.Optional["FolderBase"]:
        """Find a folder anywhere in the system by ID.

        Args:
            value (str): ID to get

        Returns:
            t.Optional["FolderBase"]: FolderBase if ID found, None otherwise
        """
        return self.all_folders_by_id.get(value.strip())

    def _get_tree_entries_objects(self, include_details: bool = False) -> t.List[str]:
        """Get the tree entries for all objects.

        Args:
            include_details (bool, optional): include more attributes in output
        """
        return [
            f"{self._tree_prefix_object}{x._get_tree_entry(include_details=include_details)}"
            for x in self.get_objects()
        ]

    def _get_tree_entry(
        self, max_depth: t.Optional[int] = None, include_details: bool = False
    ) -> str:
        """Get the tree entry for this folder.

        Args:
            max_depth (t.Optional[int], optional): if self.depth >= max_depth,
                print recursive counts instead of normal counts
            include_details (bool, optional): include more attributes in output
        """
        if self._check_max_depth(max_depth=max_depth):
            entry: str = self.get_str(include_details=include_details, recursive=True)
        else:
            entry: str = self.get_str(include_details=include_details, recursive=False)
        return f"{self._tree_prefix_folder}{entry}"

    @staticmethod
    def _load_folder(
        value: Loadables,
        idx: int,
        total: int,
        root_folders: "RootFolders",
    ) -> "Folder":
        if isinstance(value, Folder):
            value = value.to_dict()

        if isinstance(value, dict):
            value: Folder = FolderSchema.load(
                combo_dicts(value, root_folders=root_folders), unknown=marshmallow.INCLUDE
            )
            return value

        raise AxonTypeError(
            obj=FolderBase._load_folder,
            attr="value",
            value=value,
            expected=t.Union[dict, Folder],
            extra=f"While in item #{idx + 1} out of {total} items",
        )

    def _load_folders(self, values: t.Union[Loadables, t.List[Loadables]]) -> t.List["Folder"]:
        """Load list of folder dicts into Folder objects.

        Args:
            values (t.Union[Loadables, t.List[Loadables]]): list of folders to load

        Returns:
            t.List["Folder"]: loaded folders
        """
        values: t.List[t.Union[dict, "Folder"]] = listify(values)
        total: int = len(values)
        items: t.List[Folder] = [
            self._load_folder(value=x, idx=idx, total=total, root_folders=self.root_folders)
            for idx, x in enumerate(values)
        ]
        return items

    @property
    def _tree_prefix_folder(self) -> str:
        """Get the prefix to use in get_tree for folders."""
        return "".join(([self.mark_indent] * (self.depth)) + [self.mark_folder])

    @property
    def _tree_prefix_object(self) -> str:
        """Get the prefix to use in get_tree for objects."""
        return "".join(([self.mark_indent] * self.depth) + [self.mark_object])

    def _check_max_depth(self, max_depth: t.Optional[int] = None) -> bool:
        """Check if supplied max_depth is equal to or over this folders depth.

        Args:
            max_depth (t.Optional[int], optional): user supplied max_depth

        Returns:
            bool: if max_depth and self.depth are ints and max_depth >= self.depth
        """
        return (
            (isinstance(self.depth, int) and self.depth >= 0)
            and (isinstance(max_depth, int) and max_depth >= 0)
            and self.depth >= max_depth
        )

    def _split_path(self, value: str) -> t.List[str]:
        """Convert '/path/a/ b' to ['path','a','b'].

        Args:
            value (str): string to convert

        Returns:
            t.List[str]: value split on self.sep
        """
        return [x.strip() for x in value.strip().split(self.sep)]

    @property
    def _client(self):
        """Get the connect client used."""
        return self.root_folders.HTTP.CLIENT

    @staticmethod
    def _findables() -> t.Tuple[t.Type]:
        """Get the types that are allowed for `value` in find."""
        return (str, FolderBase, CreateFolderResponse)

    def __str__(self) -> str:
        """Get a str without details."""
        return self.get_str(include_details=False, recursive=False)

    def __repr__(self) -> str:
        """Get a str with details."""
        return self.get_str(include_details=True, recursive=False)


@dataclasses.dataclass(repr=False)
class RootFolders(BaseModel, FolderBase):
    """Dataclass model for response to get folders."""

    folders: t.List[dict]
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    root_folders: t.ClassVar["RootFolders"] = None
    _id: t.ClassVar[str] = "0"
    depth: t.ClassVar[int] = 0
    root_type: t.Optional[str] = None
    name: t.ClassVar[str] = SEP
    parent_id: t.ClassVar[None] = None
    root_id: t.ClassVar[None] = None
    created_by: t.ClassVar[None] = None
    path: t.ClassVar[str] = SEP
    read_only: t.ClassVar[bool] = True
    created_at: t.ClassVar[None] = None
    updated_at: t.ClassVar[None] = None
    refresh_dt: t.ClassVar[datetime.datetime] = None

    def __post_init__(self):
        """Pass."""
        self.refresh_dt: t.ClassVar[datetime.datetime] = datetime.datetime.now()
        self.root_folders: RootFolders = self

    @property
    def children_ids(self) -> t.List[str]:
        """Stub to make RootFolders look like Folders."""
        return [x["_id"] for x in self.folders]

    @property
    def children(self) -> t.List[dict]:
        """Stub to make RootFolders look like Folders."""
        return self.folders

    @staticmethod
    def get_schema_cls() -> t.Optional[t.Type[BaseSchema]]:
        """Pass."""
        return RootFoldersSchema


@dataclasses.dataclass(repr=False)
class Folder(BaseModel, FolderBase):
    """Dataclass model for unmodeled folder objects in RootFolders."""

    _id: str
    depth: int
    name: str
    root_type: str
    root_folders: "RootFolders" = get_field_dc_mm(mm_field=RootFoldersSchema)
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
        """Pass."""
        if isinstance(self.path, list):
            self.path: str = self.sep + self.sep.join(self.path)


FolderSchema: marshmallow.schema.Schema = Folder.schema(many=False)
