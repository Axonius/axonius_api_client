# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import re
import textwrap
import typing as t

import marshmallow
import marshmallow_jsonapi

from ...constants.api import GUI_PAGE_SIZES, FolderDefaults
from ...constants.ctypes import FolderBase, PatternLikeListy, Refreshables
from ...data import BaseEnum
from ...exceptions import ApiAttributeTypeError, ApiError, NotAllowedError, NotFoundError
from ...parsers.tables import tablize
from ...tools import (
    check_confirm_prompt,
    coerce_bool,
    coerce_int,
    dt_now,
    dt_parse,
    is_str,
    listify,
    parse_value_copy,
)
from .base import BaseModel, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, UnionField, get_schema_dc
from .generic import Metadata
from .nested_access import Access, AccessSchema
from .resources import PaginationRequest, PaginationSchema, ResourcesGet, ResourcesGetSchema


class QueryTypes(BaseEnum):
    """Pass."""

    devices: str = "devices"
    users: str = "users"
    vulnerabilities: str = "vulnerabilities"


class SavedQueryGetSchema(ResourcesGetSchema):
    """Pass."""

    folder_id = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    creator_ids = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    used_in = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    used_adapters = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    get_view_data = SchemaBool(load_default=True, dump_default=True)
    include_usage = SchemaBool(load_default=True, dump_default=True)

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return SavedQueryGet

    class Meta:
        """Pass."""

        type_ = "request_views_schema"


class QueryHistorySchema(BaseSchemaJson):
    """Pass."""

    query_id = marshmallow_jsonapi.fields.Str(allow_none=False)
    saved_query_name = marshmallow_jsonapi.fields.Str(
        load_default=None, dump_default=None, allow_none=True
    )
    saved_query_tags = marshmallow.fields.List(marshmallow_jsonapi.fields.Str())
    start_time = SchemaDatetime(allow_none=True)
    end_time = SchemaDatetime(allow_none=True)
    duration = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    run_by = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    run_from = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    execution_source = marshmallow_jsonapi.fields.Dict(
        load_default=None, dump_default=None, allow_none=True
    )
    status = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    module = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    results_count = marshmallow.fields.Integer(
        load_default=None, dump_default=None, allow_none=True
    )

    class Meta:
        """Pass."""

        type_ = "entities_queries_history_response_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return QueryHistory

    @classmethod
    def validate_attr_excludes(cls) -> t.List[str]:
        """Pass."""
        return ["document_meta", "id"]


class QueryHistoryRequestSchema(BaseSchemaJson):
    """Pass."""

    folder_id = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    run_by = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    run_from = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    modules = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    saved_query_name_term = marshmallow_jsonapi.fields.Str(allow_none=True)
    date_from = SchemaDatetime(allow_none=True)
    date_to = SchemaDatetime(allow_none=True)
    page = marshmallow_jsonapi.fields.Nested(PaginationSchema)
    sort = marshmallow_jsonapi.fields.Str(
        allow_none=True,
        load_default=None,
        dump_default=None,
        validate=QueryHistorySchema.validate_attr,
    )
    search = marshmallow_jsonapi.fields.Str(allow_none=True, load_default="", dump_default="")
    filter = marshmallow_jsonapi.fields.Str(allow_none=True, load_default="", dump_default="")

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return QueryHistoryRequest

    class Meta:
        """Pass."""

        type_ = "entities_queries_history_request_schema"

    @classmethod
    def validate_attrs(cls) -> dict:
        """Pass."""
        return QueryHistorySchema.validate_attrs()


class SavedQuerySchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    always_cached = SchemaBool(load_default=False, dump_default=False)
    asset_scope = SchemaBool(load_default=False, dump_default=False)
    private = SchemaBool(load_default=False, dump_default=False)
    description = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    view = marshmallow_jsonapi.fields.Dict(allow_none=True, load_default={}, dump_default={})
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    # PBUG: An null predefined can still come back from the server.
    predefined = SchemaBool(allow_none=True, load_default=False, dump_default=False)
    date_fetched = marshmallow_jsonapi.fields.Str(
        allow_none=True, load_default=None, dump_default=None
    )
    is_asset_scope_query_ready = SchemaBool()
    is_referenced = SchemaBool()
    query_type = marshmallow_jsonapi.fields.Str(
        allow_none=True, load_default="saved", dump_default="saved"
    )
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    timestamp = marshmallow_jsonapi.fields.Str(allow_none=True)
    last_updated = SchemaDatetime(allow_none=True)
    updated_by = marshmallow_jsonapi.fields.Str(
        allow_none=True, load_default=None, dump_default=None
    )
    user_id = marshmallow_jsonapi.fields.Str(allow_none=True, load_default=None, dump_default=None)
    uuid = marshmallow_jsonapi.fields.Str(allow_none=True, load_default=None, dump_default=None)
    folder_id = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    last_run_time = SchemaDatetime(allow_none=True, load_default=None, dump_default=None)
    created_by = marshmallow_jsonapi.fields.Str(
        allow_none=True, load_default=None, dump_default=None
    )
    used_in = marshmallow_jsonapi.fields.List(UnionField(types=[dict, str]))
    module = marshmallow_jsonapi.fields.Str(allow_none=True, load_default=None, dump_default=None)
    access = marshmallow_jsonapi.fields.Nested(
        AccessSchema,
        load_default=Access().to_dict(),
        dump_default=Access().to_dict(),
    )
    user_archived = SchemaBool(allow_none=True, load_default=False, dump_default=False)

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return SavedQuery

    class Meta:
        """Pass."""

        type_ = "views_details_schema"


class SavedQueryCreateSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    view = marshmallow_jsonapi.fields.Dict()
    description = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    always_cached = SchemaBool(load_default=False, dump_default=False)
    private = SchemaBool(load_default=False, dump_default=False)
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    asset_scope = SchemaBool(load_default=False, dump_default=False)
    access = marshmallow_jsonapi.fields.Nested(
        AccessSchema,
        load_default=Access().to_dict(),
        dump_default=Access().to_dict(),
    )
    folder_id = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return SavedQueryCreate

    class Meta:
        """Pass."""

        type_ = "views_schema"


class SavedQueryMixins:
    """Pass."""

    @property
    def folder(self) -> FolderBase:
        """Pass."""
        return self.HTTP.CLIENT.folders.queries.find_cached(folder=self.folder_id)

    @property
    def folder_path(self) -> str:
        """Pass."""
        return self.folder.path

    @property
    def _api(self) -> object:
        """Pass."""
        return getattr(self.HTTP.CLIENT, self.module)

    def get_names(self) -> t.List[str]:
        """Pass."""
        names: t.List[str] = [
            x.name
            for x in self._api.saved_query.get(
                as_dataclass=True, include_usage=False, get_view_data=False
            )
        ]
        return names

    def move(
        self,
        folder: t.Union[str, FolderBase],
        create: bool = FolderDefaults.create_action,
        refresh: Refreshables = FolderDefaults.refresh_action,
        echo: bool = FolderDefaults.echo_action,
        root: t.Optional[FolderBase] = None,
    ) -> "SavedQuery":
        """Move an object to another folder.

        Args:
            folder (t.Union[str, FolderBase]): folder to move an object to
            create (bool, optional): create folder if it does not exist
            refresh (Refreshables, optional): refresh the folders before searching
            echo (bool, optional): echo output to console
            root (t.Optional[FolderBase], optional): root folders to use to find folder
                instead of root folders from `self.folder`
        """
        reason: str = f"Move '{self.folder.path}/@{self.name}' to {folder!r}/@{self.name}"
        self._check_update_ok(reason=reason)

        if not isinstance(root, FolderBase):
            root: FolderBase = self.folder.root_folders
            root.refresh(value=refresh)

        folder: FolderBase = root.find(
            folder=folder,
            create=create,
            refresh=False,
            echo=echo,
            minimum_depth=1,
            reason=reason,
        )
        self.folder_id = folder.id
        return self._api.saved_query._update_handler(sq=self, as_dataclass=True)

    def copy(
        self,
        folder: t.Optional[t.Union[str, FolderBase]] = None,
        name: t.Optional[str] = None,
        copy_prefix: str = FolderDefaults.copy_prefix,
        create: bool = FolderDefaults.create_action,
        echo: bool = FolderDefaults.echo_action,
        refresh: Refreshables = FolderDefaults.refresh_action,
        private: bool = False,
        asset_scope: bool = False,
        always_cached: bool = False,
        root: t.Optional[FolderBase] = None,
    ) -> "SavedQuery":
        """Create a copy of an object, optionally in a different folder.

        Args:
            folder (t.Optional[t.Union[str, FolderBase]], optional): Folder to copy an object to
            name (t.Optional[str], optional): if supplied, name to give copy, otherwise use
                self.name + copy_prefix
            copy_prefix (str, optional): value to prepend to current name if no new name supplied
            create (bool, optional): create folder if it does not exist
            echo (bool, optional): echo output to console
            refresh (Refreshables, optional): refresh the folders before searching
            private (bool, optional): set copy as private, will change default folder used
            asset_scope (bool, optional): set copy as asset scope, will change default folder used
            root (t.Optional[FolderBase], optional): root folders to use to find folder
                instead of root folders from `self.folder`

        """
        private: bool = coerce_bool(private)
        asset_scope: bool = coerce_bool(asset_scope)
        always_cached: bool = coerce_bool(always_cached)

        names: t.List[str] = self.get_names()
        name: str = parse_value_copy(
            default=self.name, value=name, copy_prefix=copy_prefix, existing=names
        )

        if not isinstance(root, FolderBase):
            root: FolderBase = self.folder.root_folders
            root.refresh(value=refresh)

        fallback: t.Optional[FolderBase] = None
        if asset_scope:
            # PBUG currently problematic in dev
            self.HTTP.CLIENT.data_scopes.check_feature_enabled()
            fallback: t.Optional[FolderBase] = root.path_asset_scope

        default: FolderBase = None if self.folder.read_only else self.folder

        reason: str = f"Copy '{self.folder_path}/@{self.name}' to '{folder}/@{name}'"

        folder: FolderBase = root.resolve_folder(
            folder=folder,
            create=create,
            echo=echo,
            reason=reason,
            refresh=False,
            default=default,
            private=private,
            asset_scope=asset_scope,
            fallback=fallback,
        )
        create_obj: SavedQueryCreate = SavedQueryCreate(
            name=name,
            view=self.view,
            description=self.description,
            always_cached=always_cached,
            asset_scope=asset_scope,
            private=private,
            tags=self.tags,
            access=self.access,
            folder_id=folder.id,
        )
        create_response_obj = self._api.saved_query._add_from_dataclass(obj=create_obj)
        created_obj: SavedQuery = self._api.saved_query.get_by_uuid(
            value=create_response_obj.id, as_dataclass=True
        )
        return created_obj

    def _check_update_ok(self, reason: str = ""):
        """Pass."""
        errs: t.List[str] = []
        if self.predefined is True:
            errs.append("Saved Query is predefined")

        if errs:
            raise NotAllowedError([f"Unable to {reason}", *errs, "", "While in object:", f"{self}"])

    def delete(
        self,
        confirm: bool = FolderDefaults.confirm,
        echo: bool = FolderDefaults.echo_action,
        prompt: bool = FolderDefaults.prompt,
        prompt_default: bool = FolderDefaults.prompt_default,
    ) -> Metadata:
        """Delete an object.

        Args:
            confirm (bool, optional): if not True, will throw exc
            echo (bool, optional): echo output to console
            prompt (bool, optional): if confirm is not True and this is True, prompt user
                to delete an object
            prompt_default (bool, optional): if prompt is True, default choice to offer user
                in prompt
        """
        reason: str = f"Delete '{self.folder.path}/@{self.name}'"
        self._check_update_ok(reason=reason)
        check_confirm_prompt(
            reason=reason,
            src=self,
            value=confirm,
            prompt=prompt,
            default=prompt_default,
            do_echo=echo,
        )
        self.delete_response = self.HTTP.CLIENT.devices.saved_query._delete(uuid=self.uuid)
        self.delete_response.deleted_object = self
        return self.delete_response

    @classmethod
    def create_from_other(cls, other: "SavedQueryMixins") -> "SavedQueryCreate":
        """Pass."""
        if isinstance(other, SavedQueryMixins):
            return SavedQueryCreate(
                **{
                    f.name: getattr(other, f.name)
                    for f in SavedQueryCreate._get_fields()
                    if hasattr(other, f.name)
                }
            )
        raise ApiError(f"{type(other)} is not not a subclass of {SavedQueryMixins}")

    def set_name(self, value: str):
        """Set the name of this SQ."""
        if not isinstance(value, str) or (isinstance(value, str) and not value.strip()):
            raise ApiAttributeTypeError(f"Value must be a non-empty string, not {value!r}")
        self.name = value

    def set_description(self, value: str):
        """Set the description of this SQ."""
        if not isinstance(value, str):
            raise ApiAttributeTypeError(f"Value must be a string, not {value!r}")
        self.description = value

    def set_tags(self, value: t.List[str]):
        """Set the tags for this SQ."""
        value = listify(value)
        if not all([isinstance(x, str) and x.strip() for x in value]):
            raise ApiAttributeTypeError(f"Tags must be a list of non-empty strings, not {value!r}")

        self.tags = value

    @property
    def fields(self) -> t.List[str]:
        """Get the fields for this SQ."""
        return self.view.get("fields") or []

    @fields.setter
    def fields(self, value: t.List[str]):
        """Set the fields for this SQ."""
        value = listify(value)
        if not all([isinstance(x, str) and x.strip() for x in value]):
            raise ApiAttributeTypeError(f"Fields {value} must be a list of non-empty strings")

        self.view["fields"] = value

    @property
    def _query(self) -> dict:
        """Get the query object from the view object."""
        return self.view.get("query") or {}

    @property
    def _sort(self) -> dict:
        """Get the sort object from the view object."""
        return self.view.get("sort") or {}

    @property
    def sort_field(self) -> str:
        """Get the field the SQ should be sorted on."""
        return self._sort.get("field") or ""

    @sort_field.setter
    def sort_field(self, value: str):
        if not isinstance(value, str):
            raise ApiAttributeTypeError(f"Sort field {value!r} must be a string")
        self._sort["field"] = value

    @property
    def sort_descending(self) -> bool:
        """Get whether the sort_field should be sorted descending or not."""
        return self._sort.get("desc", True)

    @sort_descending.setter
    def sort_descending(self, value: bool):
        """Set whether the sort_field should be sorted descending or not."""
        self._sort["desc"] = coerce_bool(obj=value, errmsg="Sort descending must be a boolean")

    @property
    def query(self) -> str:
        """Get the AQL for this SQ."""
        return self._query.get("filter") or ""

    @query.setter
    def query(self, value: str):
        """Set the AQL for this SQ."""
        self._query["filter"] = value

    @property
    def query_expr(self) -> str:
        """Get the expr AQL for this SQ."""
        return self._query.get("onlyExpressionsFilter") or ""

    @query_expr.setter
    def query_expr(self, value: str):
        """Set the expr AQL for this SQ."""
        self._query["onlyExpressionsFilter"] = value

    @staticmethod
    def reindex_expressions(value: t.List[dict]) -> t.List[dict]:
        """Reindex the GUI query wizard expressions."""
        if isinstance(value, list):
            for idx, item in enumerate(value):
                if not isinstance(item, dict):
                    raise ApiAttributeTypeError(f"Expression must be a dict {item}")
                if idx == 0:
                    item.pop("i", None)
                else:
                    item["i"] = idx
        return value

    @property
    def expressions(self) -> t.List[dict]:
        """Get the query wizard expressions for this SQ."""
        return self._query.get("expressions") or []

    @expressions.setter
    def expressions(self, value: t.List[dict]):
        """Set the query wizard expressions for this SQ."""
        if not isinstance(value, list) or not all([isinstance(x, dict) and x for x in value]):
            raise ApiAttributeTypeError(
                f"Expressions {value} must be a list of non-empty dictionaries"
            )
        self.reindex_expressions(value=value)
        self._query["expressions"] = value

    @property
    def page_size(self) -> int:
        """Get the page size for this SQ."""
        return self.view.get("pageSize", GUI_PAGE_SIZES[0])

    @page_size.setter
    def page_size(self, value: int):
        value = coerce_int(
            obj=value,
            valid_values=GUI_PAGE_SIZES,
            errmsg=f"Invalid page size {value!r} for Saved Queries",
        )

        self.view["pageSize"] = value

    def update_description(
        self, value: str, append: bool = False, as_dataclass: bool = True
    ) -> t.Union["SavedQuery", dict]:
        """Pass."""
        if append and is_str(self.description):
            value = f"{self.description}{value}"
        reason: str = "update description to {value}"
        self._check_update_ok(reason=reason)
        self.set_description(value=value)
        apiobj = getattr(self.HTTP.CLIENT, self.module)
        response = apiobj.saved_query._update_handler(sq=self, as_dataclass=as_dataclass)
        return response


@dataclasses.dataclass(repr=False)
class SavedQuery(BaseModel, SavedQueryMixins):
    """Pass."""

    id: str = dataclasses.field(metadata={"update": False})
    name: str = dataclasses.field(metadata={"min_length": 1, "update": True})
    view: t.Optional[dict] = dataclasses.field(default_factory=dict, metadata={"update": True})
    query_type: str = dataclasses.field(default="saved", metadata={"update": True})
    updated_by: t.Optional[str] = dataclasses.field(default=None, metadata={"update": False})
    user_id: t.Optional[str] = dataclasses.field(default=None, metadata={"update": False})
    uuid: t.Optional[str] = dataclasses.field(default=None, metadata={"update": False})
    date_fetched: t.Optional[str] = dataclasses.field(default=None, metadata={"update": False})
    timestamp: t.Optional[str] = dataclasses.field(default=None, metadata={"update": False})
    last_updated: t.Optional[datetime.datetime] = dataclasses.field(
        default=None,
        metadata={
            "dataclasses_json": {"mm_field": SchemaDatetime(allow_none=True)},
        },
    )
    always_cached: bool = dataclasses.field(default=False, metadata={"update": True})
    asset_scope: bool = dataclasses.field(default=False, metadata={"update": True})
    private: bool = dataclasses.field(default=False, metadata={"update": True})
    description: t.Optional[str] = dataclasses.field(default="", metadata={"update": True})
    tags: t.List[str] = dataclasses.field(default_factory=list, metadata={"update": True})
    predefined: t.Optional[bool] = dataclasses.field(default=False, metadata={"update": False})
    is_asset_scope_query_ready: bool = dataclasses.field(default=False, metadata={"update": False})
    is_referenced: bool = dataclasses.field(default=False, metadata={"update": False})
    folder_id: str = dataclasses.field(default="", metadata={"update": True})
    last_run_time: t.Optional[datetime.datetime] = dataclasses.field(
        default=None,
        metadata={
            "dataclasses_json": {"mm_field": SchemaDatetime(allow_none=True)},
            "update": False,
        },
    )
    created_by: t.Optional[str] = dataclasses.field(default=None, metadata={"update": False})
    module: t.Optional[str] = dataclasses.field(default=None, metadata={"update": False})
    used_in: t.Optional[t.List[t.Union[str, dict]]] = dataclasses.field(default_factory=list)
    access: t.Optional[Access] = dataclasses.field(default_factory=Access)
    user_archived: t.Optional[bool] = dataclasses.field(default=False, metadata={"update": False})

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Pass."""
        self.uuid = self.uuid or self.id
        if not is_str(self.folder_id):
            self.folder_id = ""

    @classmethod
    def get_tree_type(cls) -> str:
        """Get the name to use for objects in tree outputs."""
        return "SavedQuery"

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return SavedQuerySchema

    @staticmethod
    def _str_properties() -> t.List[str]:
        """Pass."""
        return [
            "name",
            "uuid",
            "folder_path",
            "description",
            "tags",
            "query",
            "fields",
            "last_updated",
            "private",
            "always_cached",
            "is_referenced",
            "asset_scope",
            "is_asset_scope_query_ready",
        ]

    @property
    def last_updated_str(self) -> str:
        """Get the last updated in str format."""
        return (
            self.last_updated.strftime("%Y-%m-%dT%H:%M:%S%z")
            if isinstance(self.last_updated, datetime.datetime)
            else self.last_updated
        )

    @property
    def created_by_str(self) -> str:
        """Pass."""
        from .system_users import SystemUser

        return SystemUser.get_user_source(value=self.created_by)

    @property
    def updated_by_str(self) -> str:
        """Pass."""
        from .system_users import SystemUser

        return SystemUser.get_user_source(value=self.updated_by)

    @property
    def _tree_summary(self) -> dict:
        """Pass."""
        return {
            "name": self.name,
            "query_type": self.module,
        }

    @property
    def _tree_details(self) -> dict:
        """Pass."""
        return {
            "name": self.name,
            "query_type": self.module,
            "description": self.description,
            "uuid": self.uuid,
            "query": self.query,
            "tags": self.tags,
            "fields": self.fields,
            "is_predefined": self.predefined,
            "is_referenced": self.is_referenced,
            "is_private": self.private,
            "is_always_cached": self.always_cached,
            "is_asset_scope": self.asset_scope,
            "is_asset_scope_ready": self.is_asset_scope_query_ready,
            "created_by": self.created_by_str,
            "updated_by": self.updated_by_str,
            "last_updated": self.last_updated_str,
            "last_run_time": self.last_run_time,
        }

    def get_tree_entry(self, include_details: bool = False) -> str:
        """Pass."""

        def to_str(value):
            return str(value) if isinstance(value, datetime.datetime) else value

        obj: dict = self._tree_details if include_details else self._tree_summary
        items: t.List[str] = [f"{k}={to_str(v)!r}" for k, v in obj.items()]
        items: str = ", ".join(items)
        return f"{self.get_tree_type()}({items})"

    @property
    def tags_str(self) -> str:
        """Pass."""
        return ", ".join(self.tags or [])

    def to_strs(self) -> t.List[str]:
        """Pass."""
        items = list(self.col_info.items()) + list(self.col_details.items())
        return [f"{k}: {v}" for k, v in items]

    def to_tablize(self) -> dict:
        """Get tablize-able repr of this obj."""
        col_info = [
            f"{k.upper()}={textwrap.fill('' if v is None else str(v), width=30)}"
            for k, v in self.col_info.items()
        ]
        col_details = [f"{k}: {v}" for k, v in self.col_details.items()]
        ret = {}
        ret["Info"] = "\n".join(col_info)
        ret["Details"] = "\n".join(col_details)
        return ret

    @property
    def str_details(self) -> str:
        """Pass."""
        items = {}
        items.update(self.col_info)
        items.update(self.col_details)
        return "\n".join([f"{k.upper()}={v}" for k, v in items.items()])

    @property
    def col_details(self) -> dict:
        """Get the details for this SQ."""
        return {
            "predefined": self.predefined,
            "referenced": self.is_referenced,
            "private": self.private,
            "always_cached": self.always_cached,
            "asset_scope": self.asset_scope,
            "asset_scope_ready": self.is_asset_scope_query_ready,
            "page_size": self.page_size,
            "access": self.access,
            "created_by": self.created_by_str,
            "updated_by": self.updated_by_str,
            "last_updated": self.last_updated_str,
            "last_run_time": self.last_run_time,
        }

    @property
    def col_info(self) -> dict:
        """Pass."""
        return {
            "name": self.name,
            "uuid": self.uuid,
            "folder": self.folder_path,
            "asset_type": self.module,
            "description": self.description if isinstance(self.description, str) else "",
            "tags": self.tags_str,
        }


@dataclasses.dataclass
class SavedQueryCreate(BaseModel, SavedQueryMixins):
    """Pass."""

    name: str
    view: dict
    description: t.Optional[str] = ""
    always_cached: bool = False
    asset_scope: bool = False
    private: bool = False
    tags: t.List[str] = dataclasses.field(default_factory=list)
    access: t.Optional[Access] = dataclasses.field(default_factory=Access)
    folder_id: str = ""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return SavedQueryCreateSchema


@dataclasses.dataclass
class SavedQueryGet(ResourcesGet):
    """Pass."""

    folder_id: str = ""
    creator_ids: t.Optional[t.List[str]] = dataclasses.field(default_factory=list)
    used_in: t.Optional[t.List[str]] = dataclasses.field(default_factory=list)
    used_adapters: t.Optional[t.List[str]] = dataclasses.field(default_factory=list)
    get_view_data: bool = True
    include_usage: bool = True

    def __post_init__(self):
        """Pass."""
        self.folder_id = self.folder_id or ""
        self.creator_ids = self.creator_ids or []
        self.used_in = self.used_in or []
        self.page = self.page if self.page else PaginationRequest()

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return SavedQueryGetSchema


@dataclasses.dataclass
class QueryHistoryRequest(BaseModel):
    """Pass."""

    run_by: t.Optional[t.List[str]] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="run_by",
        default_factory=list,
    )
    run_from: t.Optional[t.List[str]] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="run_from",
        default_factory=list,
    )
    modules: t.Optional[t.List[str]] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="modules",
        default_factory=list,
    )
    tags: t.Optional[t.List[str]] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="tags",
        default_factory=list,
    )
    saved_query_name_term: t.Optional[str] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="saved_query_name_term",
        default=None,
    )
    date_from: t.Optional[datetime.datetime] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="date_from",
        default=None,
    )
    date_to: t.Optional[datetime.datetime] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="date_to",
        default=None,
    )
    page: t.Optional[PaginationRequest] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="page",
        default_factory=PaginationRequest,
    )
    search: t.Optional[str] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="search",
        default="",
    )
    filter: t.Optional[str] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="filter",
        default=None,
    )

    def __post_init__(self):
        """Pass."""
        self.run_by = self.run_by or []
        self.run_from = self.run_from or []
        self.modules = self.modules or []
        self.tags = self.tags or []
        self.page = self.page if self.page else PaginationRequest()

    def set_sort(self, value: t.Optional[str] = None, descending: bool = False) -> t.Optional[str]:
        """Pass."""
        if isinstance(value, str) and value:
            value = QueryHistorySchema.validate_attr(value=value, exc_cls=NotFoundError)
            value = self._prepend_sort(value=value, descending=descending)
        else:
            value = None

        self.sort = value
        return value

    def set_name_term(self, value: t.Optional[str] = None) -> t.Optional[str]:
        """Pass."""
        if isinstance(value, str) and value:
            self.saved_query_name_term = value
        else:
            value = None
            self.saved_query_name_term = value
        return value

    def set_date(
        self,
        date_start: t.Optional[datetime.datetime] = None,
        date_end: t.Optional[datetime.datetime] = None,
    ) -> t.Tuple[t.Optional[datetime.datetime], t.Optional[datetime.datetime]]:
        """Pass."""
        if date_end and not date_start:
            raise ApiError("date_start must also be supplied when date_end is supplied")

        if date_start:
            date_start = dt_parse(date_start)
            if date_end:
                date_end = dt_parse(date_end)
            else:
                date_end = dt_now()
        return (date_start, date_end)

    @classmethod
    def get_list_props(cls) -> t.List[str]:
        """Pass."""
        return [x.name for x in cls._get_fields() if x.type == t.Optional[t.List[str]]]

    def set_list(
        self,
        prop: str,
        values: t.Optional[t.List[str]] = None,
        enum: t.Optional[t.List[str]] = None,
        enum_callback: t.Optional[callable] = None,
    ) -> t.List[str]:
        """Pass."""

        def err(check, use_enum):
            valids = [{f"Valid {prop} values": x} for x in use_enum]
            err = f"No {prop} matching {check!r} found out of {len(use_enum)} items"
            err_table = tablize(value=valids, err=err)
            raise NotFoundError(err_table)

        props = self.get_list_props()
        if prop not in props:
            raise ApiError(f"Invalid list property {prop}, valids: {props}")

        values = listify(values)
        use_enum = None
        if isinstance(enum, list) and enum:
            use_enum = enum
        elif callable(enum_callback):
            use_enum = enum_callback()

        matches = []
        for value in values:
            if isinstance(value, str):
                check = value
                if check.startswith("~"):
                    check = re.compile(check[1:])
            elif isinstance(value, t.Pattern):
                check = value
            else:
                raise ApiError(
                    f"Value must be {PatternLikeListy}, not type={type(value)}, value={value!r}"
                )

            if isinstance(use_enum, list) and use_enum:
                if isinstance(check, str):
                    if check not in use_enum:
                        err(check=check, use_enum=use_enum)
                    matches.append(check)
                elif isinstance(check, t.Pattern):
                    re_matches = [x for x in use_enum if check.search(x)]
                    if not re_matches:
                        err(check=check, use_enum=use_enum)
                    matches += re_matches
            else:
                if isinstance(check, str):
                    matches.append(check)

        self.logger.debug(f"Resolved {prop} values {values} to matches {matches}")
        setattr(self, prop, matches)
        return matches

    def set_search_filter(
        self, search: t.Optional[str] = None, filter: t.Optional[str] = None
    ) -> t.Tuple[t.Optional[str], t.Optional[str]]:
        """Pass."""
        values = [search, filter]
        is_strs = [isinstance(x, str) and x for x in values]
        if any(is_strs) and not all(is_strs):
            raise ApiError(f"Only search or filter supplied, must supply both: {values}")
        if not all(is_strs):
            search = ""
            filter = None
        self.search = search
        self.filter = filter
        return (search, filter)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return QueryHistoryRequestSchema


@dataclasses.dataclass
class QueryHistory(BaseModel):
    """Pass."""

    query_id: str = get_schema_dc(schema=QueryHistorySchema, key="query_id")
    saved_query_name: t.Optional[str] = get_schema_dc(
        schema=QueryHistorySchema, key="saved_query_name", default=None
    )
    saved_query_tags: t.Optional[t.List[str]] = get_schema_dc(
        schema=QueryHistorySchema, key="saved_query_tags", default=None
    )
    start_time: t.Optional[datetime.datetime] = get_schema_dc(
        schema=QueryHistorySchema, key="start_time", default=None
    )
    end_time: t.Optional[datetime.datetime] = get_schema_dc(
        schema=QueryHistorySchema, key="end_time", default=None
    )
    duration: t.Optional[str] = get_schema_dc(
        schema=QueryHistorySchema, key="duration", default=None
    )
    run_by: t.Optional[str] = get_schema_dc(schema=QueryHistorySchema, key="run_by", default=None)
    run_from: t.Optional[str] = get_schema_dc(
        schema=QueryHistorySchema, key="run_from", default=None
    )
    execution_source: t.Optional[dict] = get_schema_dc(
        schema=QueryHistorySchema, key="execution_source", default=None
    )
    status: t.Optional[str] = get_schema_dc(schema=QueryHistorySchema, key="status", default=None)
    module: t.Optional[str] = get_schema_dc(schema=QueryHistorySchema, key="module", default=None)
    results_count: t.Optional[int] = get_schema_dc(
        schema=QueryHistorySchema, key="results_count", default=None
    )
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls():
        """Pass."""
        return QueryHistorySchema

    @property
    def name(self) -> t.Optional[str]:
        """Pass."""
        return self.saved_query_name

    @property
    def tags(self) -> t.Optional[str]:
        """Pass."""
        return self.saved_query_tags

    @property
    def asset_type(self) -> t.Optional[str]:
        """Pass."""
        return self.execution_source.get("entity_type")

    @property
    def component(self) -> t.Optional[str]:
        """Pass."""
        return self.execution_source.get("component")

    def __str__(self) -> t.List[str]:
        """Pass."""

        def getval(prop):
            value = getattr(self, prop, None)
            if value is not None and not isinstance(value, (str, int, float, bool)):
                value = str(value)
            return repr(value)

        vals = ", ".join([f"{p}={getval(p)}" for p in self._props_details()])
        return f"{self.__class__.__name__}({vals})"

    def __repr__(self):
        """Pass."""
        return self.__str__()

    def to_csv(self) -> dict:
        """Pass."""

        def getval(prop):
            value = getattr(self, prop, None)
            if isinstance(value, list):
                value = "\n".join([str(x) for x in value])
            return value

        return {k: getval(k) for k in self._props_csv()}

    def to_tablize(self) -> dict:
        """Pass."""

        def getval(prop, width=30):
            value = getattr(self, prop, None)
            if not isinstance(value, str):
                value = "" if value is None else str(value)
            if isinstance(width, int) and len(value) > width:
                value = textwrap.fill(value, width=width)
            prop = prop.replace("_", " ").title()
            return f"{prop}: {value}"

        def getvals(props, width=30):
            return "\n".join([getval(prop=p, width=width) for p in props])

        tags = "\nTags:\n  " + "\n  ".join(self.tags or [])
        return {
            "Details": getvals(self._props_details(), None) + tags,
            "Results": getvals(self._props_timings() + self._props_results(), None),
        }

    @classmethod
    def _props_csv(cls) -> t.List[str]:
        """Pass."""
        return cls._props_custom() + [
            x for x in cls._get_field_names() if x not in cls._props_skip()
        ]

    @classmethod
    def _props_details(cls) -> t.List[str]:
        """Pass."""
        return [x for x in cls._props_custom() if x not in ["tags"]] + [
            x for x in cls._get_field_names() if x not in cls._props_details_excludes()
        ]

    @classmethod
    def _props_details_excludes(cls) -> t.List[str]:
        """Pass."""
        return cls._props_custom() + cls._props_skip() + cls._props_timings() + cls._props_results()

    @classmethod
    def _props_timings(cls) -> t.List[str]:
        """Pass."""
        return ["start_time", "end_time", "duration"]

    @classmethod
    def _props_skip(cls) -> t.List[str]:
        """Pass."""
        return ["execution_source", "document_meta", "saved_query_name", "saved_query_tags"]

    @classmethod
    def _props_custom(cls) -> t.List[str]:
        """Pass."""
        return ["name", "tags"]

    @classmethod
    def _props_results(cls) -> t.List[str]:
        """Pass."""
        return ["status", "results_count"]
