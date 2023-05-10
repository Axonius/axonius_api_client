# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ....constants.fields import AXID
from ....parsers.aql import join_and_or_not
from ....projects.cf_token.tools import echoer
from ....tools import coerce_bool, dt_parse, listify
from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaDatetime, field_from_mm


def get_internal_axon_id(
    value: t.Any = None,
    length: t.Optional[int] = AXID.length,
    full_strip: bool = False,
    keep_chars: str = AXID.chars,
) -> t.Optional[str]:
    """Extract an internal_axon_id from a string if possible."""
    if not isinstance(value, (str, bytes)):
        return None

    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")

    value = value.strip()

    if full_strip:
        "".join(x for x in value if x in keep_chars)

    return (
        None
        if not value
        or (isinstance(length, int) and not len(value) == length)
        or not value.isalnum()
        else value
    )


def get_strs(
    self,
    attr: str,
    values: t.Optional[t.Union[str, t.Iterable[str]]] = None,
    append: bool = False,
    echo: bool = True,
    echo_maximum: t.Optional[int] = None,
    level: str = "debug",
    callback: t.Optional[t.Callable] = None,
) -> t.List[str]:
    """Get the strs from a value."""
    resolved = set(x.strip() for x in listify(values) if isinstance(x, str))

    if append:
        current = set(
            x.strip()
            for x in listify(getattr(self, attr, None))
            if isinstance(x, str) and x.strip()
        )
        resolved = current.union(resolved)

    resolved = list(resolved)

    _post = ""
    _resolved = resolved
    if isinstance(echo_maximum, int) and len(resolved) > echo_maximum:
        _post = f"\n... + {len(resolved) - echo_maximum} more"
        _resolved = resolved[:echo_maximum]

    _resolved = "\n".join(_resolved) + _post
    echoer(f"Resolved `{attr}` ({len(resolved)}):\n{_resolved}", echo=echo, level=level)
    return resolved


class ModifyTagsRequestSchema(BaseSchemaJson):
    """Schema for request to modify tags."""

    entities = mm_fields.Dict(
        load_default=dict,
        dump_default=dict,
        description="Entities to modify tags on",
    )
    labels = mm_fields.List(
        mm_fields.Str(),
        load_default=list,
        dump_default=list,
        description="Tags to modify",
    )
    filter = mm_fields.Str(
        load_default="",
        dump_default="",
        allow_none=True,
        description="AQL for the request",
    )  # FilterSchema
    history = SchemaDatetime(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="Get asset data for a specific point in time",
    )  # FilterSchema
    search = mm_fields.Str(
        load_default="",
        dump_default="",
        allow_none=True,
        # cortex does not allow_none, but we do to allow for empty searches
        description="search term for the request (unused?)",
    )  # FilterSchema

    class Meta:
        """JSONAPI config."""

        type_ = "add_tags_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return ModifyTagsRequest


SCHEMA = ModifyTagsRequestSchema()


@dataclasses.dataclass
class ModifyTagsRequest(BaseModel):
    """Model for request to modify tags."""

    entities: dict = field_from_mm(SCHEMA, "entities")
    labels: t.List[str] = field_from_mm(SCHEMA, "labels")
    filter: t.Optional[str] = field_from_mm(SCHEMA, "filter")
    history: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "history")
    search: t.Optional[str] = field_from_mm(SCHEMA, "search")

    SCHEMA: t.ClassVar[t.Any] = SCHEMA

    TARGET: t.ClassVar[str] = "Received count of assets that will be modified as count_target"
    ERROR_RANGE: t.ClassVar[str] = "{COUNT_TARGET} but it is outside of the supplied ranges"
    ERROR_FALSE: t.ClassVar[str] = (
        "{TARGET} but both `prompt` and `verified` are False, re-run with one or the other set to "
        "True"
    )
    VERIFIED: t.ClassVar[str] = (
        "{TARGET} and `verified` is True, not prompting user to " "verify count_target"
    )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return ModifyTagsRequestSchema

    def __post_init__(self):
        """Dataclasses post init."""
        if not isinstance(self.search, str):
            self.search = ""

        if not isinstance(self.entities, dict):
            self.entities = {}

        if "ids" not in self.entities:
            self.entities["ids"] = []

        if "include" not in self.entities:
            self.entities["include"] = True

    @property
    def tags(self) -> t.List[str]:
        """Get the tags."""
        return self.labels

    @tags.setter
    def tags(self, value: t.Union[str, t.List[str]]):
        """Set the tags."""
        self.labels = listify(value)

    @property
    def ids(self) -> t.List[str]:
        """Get the ids from entities."""
        if "ids" not in self.entities:
            self.entities["ids"] = []
        return self.entities["ids"]

    @ids.setter
    def ids(self, value: t.Union[str, t.List[str]]):
        """Set the ids on entities."""
        self.entities["ids"] = listify(value)

    @property
    def ids_count(self) -> int:
        """Get the number of `ids`."""
        return len(self.ids)

    @property
    def ids_str(self) -> str:
        """Get the `ids` as a comma separated string."""
        return ",".join([f'"{x}"' for x in self.ids])

    @property
    def include(self) -> bool:
        """Get the `include` value from entities."""
        return self.entities.get("include", True)

    @include.setter
    def include(self, value: bool):
        """Set the `include` value on entities."""
        self.entities["include"] = coerce_bool(value)

    @property
    def history_date(self) -> t.Optional[datetime.datetime]:
        """Get the history date."""
        return self.history

    @history_date.setter
    def history_date(self, value: t.Optional[datetime.datetime]):
        """Set the history date."""
        self.history = dt_parse(value, allow_none=True)

    @property
    def query(self) -> t.Optional[str]:
        """Get the query."""
        return self.filter

    @query.setter
    def query(self, value: t.Optional[str]):
        """Set the query."""
        self.filter = value

    @property
    def query_length(self) -> str:
        """Get the number of characters in `query`."""
        length = len(self.query or "")
        return f"{length} characters"

    @property
    def query_ids(self) -> str:
        """Get the query that would target supplied `ids`."""
        query = f'"internal_axon_id" in [{self.ids_str}]'
        return query

    @property
    def count_target_calculation(self) -> str:
        """Get the target string based on include."""
        text = f"internal_axon_id in [{self.ids_count} `ids`]"
        if not self.include:
            text = f"(NOT ({text})) AND (`query` with {self.query_length})"

        return text

    @property
    def count_target_parts(self) -> t.List[str]:
        """Get the query parts can be used to get the target count.

        Returns:
            List[str]: the query parts can be used to get the target count.
        """
        if self.include:
            parts = [self.query_ids]
        else:
            parts = []
            if self.ids:
                parts += [join_and_or_not(self.query_ids, not_flag=True)]
            parts += [self.query]
        parts = [x.strip() for x in parts if isinstance(x, str) and x.strip()]
        return parts

    @property
    def count_target_query(self) -> str:
        """Get the query that can be used to get the target count.

        Returns:
            str: The query that can be used to get the target count.
        """
        return join_and_or_not(*self.count_target_parts, and_flag=True)

    def check_request(self, echo: bool = True, level: str = "debug"):
        """Check the request before sending it."""
        if self.include:
            if self.filter:
                raise ValueError(f"`query` is ignored when include=True\n{self}")
            if not self.ids:
                raise ValueError(f"Must supply at least one id when include=True\n{self}")

        echoer(f"{self}", echo=echo, level=level)

    def set_include(self, include: bool, echo: bool = True, level: str = "debug") -> bool:
        """Set the include flag.

        Args:
            include: True: target=`ids` (ignores `query` and `history_date`),
                False: target=(ids from `query` on `history_date`) - `ids`
            echo: echo output to stderr
            level: level to use when echoing output

        Returns:
            bool
        """
        self.include = include
        echoer(f"Resolved `include`: {self.include}", echo=echo, level=level)
        return self.include

    def set_tags(
        self,
        tags: t.Union[str, t.List[str]],
        append: bool = True,
        echo: bool = True,
        level: str = "debug",
    ) -> t.List[str]:
        """Set the tags to modify.

        Args:
            tags: tags to set
            append: append or replace existing :attr:`tags`
            echo: echo output to stderr
            level: level to use when echoing output

        Returns:
            list of tags set to :attr:`tags`
        """
        self.tags = get_strs(self, attr="tags", values=tags, append=append, echo=echo, level=level)
        if not self.tags:
            raise ValueError("Must supply at least one tag")
        return self.tags

    def set_ids(
        self,
        ids: t.Sequence[str],
        append: bool = True,
        echo: bool = True,
        level: str = "debug",
    ):
        """Set the assets to modify (if include=False, assets to exclude from `query`).

        # TBD: support extract internal_axon_ids from csv, json, jsonl, or list of dicts

        Args:
            ids: ids to set
            append: append or replace existing :attr:`ids`
            echo: echo output to stderr
            level: level to use when echoing output

        Returns:
            list of ids set to :attr:`ids`
        """
        self.ids = get_strs(
            self,
            attr="ids",
            values=ids,
            append=append,
            echo=echo,
            level=level,
            echo_maximum=3,
            callback=AXID.is_axid,
            # TODO is this working?
        )
        return self.ids

    def set_history_date(
        self,
        history_date: t.Optional[t.Union[str, datetime.datetime]] = None,
        echo: bool = True,
        level: str = "debug",
    ) -> t.Optional[datetime.datetime]:
        """Set the date to for `query` (ignored if include=True).

        Args:
            history_date: value to set
            echo: echo output to stderr
            level: level to use when echoing output

        Returns:
            datetime.datetime set to :attr:`history`
        """
        self.history_date = history_date
        level = "warning" if self.include and self.history else level
        echoer(f"Resolved `history_date` to: {self.history_date}", echo=echo, level=level)
        return self.history_date

    def set_query(
        self,
        query: t.Optional[str] = None,
        echo: bool = True,
        level: str = "debug",
    ) -> t.Optional[str]:
        """Set the query to use for `history_date` (ignored if include=True).

        Args:
            query: value to set
            echo: echo output to stderr
            level: level to use when echoing output

        Returns:
            str set to :attr:`filter`
        """
        self.query = query.strip() if isinstance(query, str) and query.strip() else None
        level = "warning" if self.include and self.query else level
        echoer(f"Resolved `query` to:\n{self.query}", echo=echo, level=level)
        return self.query

    def __str__(self) -> str:
        """Get the string representation of the request."""
        items = [
            f"`tags`: {self.tags}",
            f"`ids`: {self.ids_count}",
            f"`include`: {self.include}",
            f"`history_date`{self._ignored}: {self.history_date}",
            f"`query`{self._ignored}: {self.query_length}",
            f"`count_target` calculated by: {self.count_target_calculation}",
        ]
        items = "\n  ".join(items)
        return f"{self.__class__.__name__}:\n  {items}"

    @property
    def _ignored(self) -> str:
        """Get the ignored string based on include."""
        return " (ignored because `include` is True)" if self.include else ""
