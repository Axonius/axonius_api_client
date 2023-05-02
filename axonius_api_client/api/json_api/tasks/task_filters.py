# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow
import marshmallow_jsonapi.fields as mm_fields
import click

from ....constants.api import RE_PREFIX
from ....constants.ctypes import PatternLike, TypeMatch
from ....constants.general import SPLITTER
from ....exceptions import NotFoundError
from ....parsers.matcher import Matcher
from ....tools import coerce_int, listify
from ..base2 import BaseModel, BaseSchema
from ..custom_fields import field_from_mm


ATTR_MAP = {
    "action_types": {
        "TaskFilters": "action_names",
        "Task": "results[].type",
        "TaskBasic": "action_names",
        "TaskFull": None,
        "GetTasks": "action_names",
        "enum": "enum_action_types",
        "desc": "Action types in use by any Enforcement Set",
    },
    "discovery_uuids": {
        "TaskFilters": "discovery_cycle_id",
        "Task": "discover_uuid",
        "TaskBasic": "discovery_id",
        "TaskFull": None,
        "GetTasks": "discovery_cycle",
        "enum": "enum_discovery_uuids",
        "desc": "UUIDs of Discovery Cycles that have launched a task",
    },
    "enforcement_names": {
        "TaskFilters": "enforcement_name",
        "Task": "uuid",
        "TaskBasic": "uuid",
        "TaskFull": "uuid",
        "GetTasks": "enforcement_ids",
        "enum": "enum_enforcement_names",
        "desc": "Names of all Enforcement Sets that have launched a task",
    },
    "task_ids": {
        "TaskFilters": "run",
        "Task": "id",
        "TaskBasic": "pretty_id",
        "TaskFull": "pretty_id",
        "GetTasks": "task_id",
        "enum": "enum_task_ids",
        "desc": "Pretty IDs of all tasks for all Enforcement Sets",
    },
    "statuses": {
        "TaskFilters": "statuses",
        "Task": "status",
        "TaskBasic": "result_metadata_status",
        "TaskFull": None,
        "GetTasks": "statuses_filter",
        "enum": "enum_statuses",
        "desc": "Statuses of all tasks and task results for all Enforcement Sets",
    },
}


def build_include_options() -> list:
    """Pass."""
    options: list = []
    for arg, details in ATTR_MAP.items():
        long_form = arg.replace("_", "-")
        long_form_switch = f"--include-{long_form}/--no-include-{long_form}"
        short_form = "".join([x[0] for x in arg.split("_")])
        short_form_switch = f"-i{short_form}/-ni{short_form}"
        desc = details["desc"]
        option = click.option(
            long_form_switch,
            short_form_switch,
            arg,
            help=f"Include {desc} in output",
            default=True,
            show_envvar=True,
            show_default=True,
        )
        options.append(option)

    return options


class TaskFiltersSchema(BaseSchema):
    """Schema for filters for getting enforcement tasks in basic model."""

    action_names = mm_fields.List(
        mm_fields.Str(),
        data_key="action_names",
        description="List of all action types in use",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    discovery_cycle_id = mm_fields.List(
        mm_fields.Str(),
        data_key="discover_cycle_id",
        description="List of all discovery UUIds that launched a task",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    enforcement_name = mm_fields.List(
        mm_fields.Dict(),
        data_key="enforcement_name",
        description="List of dict with keys 'text' enforcement set name and 'value' task UUID",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    run = mm_fields.List(
        mm_fields.Int(),
        data_key="run",
        description="List of pretty IDs of all tasks",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    statuses = mm_fields.List(
        mm_fields.Str(),
        data_key="statuses",
        description="List of statuses in use",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )

    class Meta:
        """Meta."""

        type_ = "PROTO_TASK_FILTERS"
        unknown = marshmallow.INCLUDE

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return TaskFilters


SCHEMA: marshmallow.Schema = TaskFiltersSchema()


@dataclasses.dataclass
class TaskFilters(BaseModel):
    """Model for filters for getting enforcement tasks in basic model."""

    action_names: t.List[str] = field_from_mm(SCHEMA, "action_names")
    discovery_cycle_id: t.List[str] = field_from_mm(SCHEMA, "discovery_cycle_id")
    enforcement_name: t.List[dict] = field_from_mm(SCHEMA, "enforcement_name")
    run: t.List[int] = field_from_mm(SCHEMA, "run")
    statuses: t.List[str] = field_from_mm(SCHEMA, "statuses")

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA
    ACTION_TYPES: t.ClassVar[str] = ATTR_MAP["action_types"]["desc"]
    DISCOVERY_UUIDS: t.ClassVar[str] = ATTR_MAP["discovery_uuids"]["desc"]
    ENFORCEMENT_NAMES: t.ClassVar[str] = ATTR_MAP["enforcement_names"]["desc"]
    TASK_IDS: t.ClassVar[str] = ATTR_MAP["task_ids"]["desc"]
    STATUSES: t.ClassVar[str] = ATTR_MAP["statuses"]["desc"]

    def __post_init__(self):
        """Post init."""
        self.action_names = listify(self.action_names)
        self.discovery_cycle_id = listify(self.discovery_cycle_id)
        self.enforcement_name = listify(self.enforcement_name)
        self.run = listify(self.run)
        self.statuses = listify(self.statuses)

    @property
    def enum_enforcement_names(self) -> t.List[str]:
        """Get a list of all enforcement names that have a run a task."""
        return sorted(list(set(list([x["text"] for x in self.enforcement_name]))))

    @property
    def enum_task_ids(self) -> t.List[int]:
        """Get a list of all known task pretty_id's."""
        return sorted(self.run)

    @property
    def enum_action_types(self) -> t.List[str]:
        """Get a list of all action types in use."""
        return sorted(self.action_names)

    @property
    def enum_discovery_uuids(self) -> t.List[str]:
        """Get a list of all discovery cycle UUIDs that have launched a task."""
        return sorted(self.discovery_cycle_id)

    @property
    def enum_statuses(self) -> t.List[str]:
        """Get a list of all statuses in use."""
        return sorted(self.statuses)

    def check_task_id(self, value: t.Optional[t.Union[int, str, bytes]] = None) -> t.Optional[int]:
        """Check validity of a task id.

        Args:
            value: task id to check
        """
        parsed = coerce_int(
            obj=value,
            allow_none=True,
            max_value=max(self.enum_task_ids, default=0),
            min_value=min(self.enum_task_ids, default=0),
            errmsg=f"Invalid task id for {self.TASK_IDS}: {value}",
        )
        return parsed

    def check_action_types(self, values: t.Optional[TypeMatch] = None, **kwargs) -> t.List[str]:
        """Check validity of action types.

        Notes:
            The REST API names this "action_names", but the actual concept is "action_type".
            The value stored in action_names is the list of all action_types that are being used
            by any enforcement set.

        Args:
            values: strings (starting with re_prefix to treat as a pattern) or patterns
            kwargs: passed to check_values
        """
        return self.check_values(
            valids=self.enum_action_types, description=self.ACTION_TYPES, values=values, **kwargs
        )

    def check_discovery_uuids(self, values: t.Optional[TypeMatch] = None, **kwargs) -> t.List[str]:
        """Check validity of discovery UUIDs.

        Args:
            values: strings (starting with re_prefix to treat as a pattern) or patterns
            kwargs: passed to check_values
        """
        return self.check_values(
            valids=self.enum_discovery_uuids,
            description=self.DISCOVERY_UUIDS,
            values=values,
            **kwargs,
        )

    def check_statuses(self, values: t.Optional[TypeMatch] = None, **kwargs) -> t.List[str]:
        """Check validity of statuses.

        Args:
            values: strings (starting with re_prefix to treat as a pattern) or patterns
            kwargs: passed to check_values
        """
        return self.check_values(
            valids=self.enum_statuses, description=self.STATUSES, values=values, **kwargs
        )

    def check_enforcement_names(
        self, values: t.Optional[TypeMatch] = None, as_names: bool = False, **kwargs
    ) -> t.List[str]:
        """Check validity of enforcement names and return a list of all associated task UUIDs.

        Args:
            values: strings (starting with re_prefix to treat as a pattern) or patterns
            as_names: return a list of enforcement names matches instead of the task UUIDs
            kwargs: passed to check_values
        """
        matched = self.check_values(
            valids=self.enum_enforcement_names,
            description=self.ENFORCEMENT_NAMES,
            values=values,
            **kwargs,
        )
        if not as_names and matched:
            return [x["value"] for x in self.enforcement_name if x["text"] in matched]
        return matched

    @staticmethod
    def check_values(
        valids: t.List[str],
        description: str,
        values: t.Optional[TypeMatch] = None,
        error: bool = True,
        minimum: t.Optional[int] = None,
        re_prefix: str = RE_PREFIX,
        split: bool = True,
        split_max: t.Optional[int] = None,
        split_sep: t.Optional[PatternLike] = SPLITTER,
        strip: bool = True,
        strip_chars: t.Optional[str] = None,
    ) -> t.List[str]:
        """Check that a value is valid.

        Args:
            valids:
            description: what valids are being checked
            values: strings (starting with re_prefix to treat as a pattern) or patterns
            error: raise error if any value supplied fails to match
            minimum: raise error if matched is less than this number
            re_prefix: if any values provided start with this, treat them as regex patterns
            split: split values on split_sep
            split_max: if value > 0 and split=True, only split on split_sep N times
            split_sep: if split=True, split values on this pattern or string
            strip: strip values of strip_chars
            strip_chars: if strip=True, strip values of these characters

        Returns:
            list of valids that matches any supplied pattern or string in value
        """
        matcher: Matcher = Matcher(
            values=values,
            re_prefix=re_prefix,
            split=split,
            split_max=split_max,
            split_sep=split_sep,
            strip=strip,
            strip_chars=strip_chars,
        )

        valids_strs = [f"- {x}" for x in sorted(str(x) for x in valids)]
        matched, unmatched = matcher.matches(values=valids)
        matcher_strs: t.List[str] = [
            f"Searching against valid values of {description}",
            f"Parsed values {values!r} into {matcher}",
            f"error: {error}, minimum: {minimum}",
            f"Matched: {len(matched)}, Unmatched: {len(unmatched)}, Valid: {len(valids)}",
        ]
        matched_strs: t.List[str] = [f"- {i}" for i in sorted(str(x) for x in matched)]
        unmatched_strs: t.List[str] = [f"- {i}" for i in sorted(str(x) for x in unmatched)]
        valids_strs: t.List[str] = ["", f"Valids ({len(valids)}):", *valids_strs, ""]

        if unmatched and error:
            err_strs: t.List[str] = [
                "error is True and some searches did not match any valid values",
                f"Matched ({len(matched)}):",
                *matched_strs,
                f"Unmatched ({len(unmatched)}):",
                *unmatched_strs,
            ]
            raise NotFoundError([*err_strs, *matcher_strs, *valids_strs, *err_strs])

        if isinstance(minimum, int) and minimum > 0 and len(matched) < minimum:
            err_strs: t.List[str] = [
                f"minimum={minimum} and matched={len(matched)}",
                f"Unmatched ({len(unmatched)}):",
                *unmatched_strs,
            ]
            raise NotFoundError([*err_strs, *matcher_strs, *valids_strs, *err_strs])
        return matched

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return TaskFiltersSchema

    def __str__(self):
        """Pass."""
        return f"{self.__class__.__name__}(enums={[x.name for x in dataclasses.fields(self)]})"

    def __repr__(self):
        """Pass."""
        return str(self)
