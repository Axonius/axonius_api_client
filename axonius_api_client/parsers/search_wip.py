# -*- coding: utf-8 -*-
"""Fancy footwork for searching objects based on attributes.

# WIP!!
"""
import dataclasses
import typing as t

from ..tools import is_str, listify


@dataclasses.dataclass()
class Search:
    """Pass."""

    attr: str
    name: t.Optional[str] = None

    search_delim: t.ClassVar[str] = ":"
    pattern_prefix: t.ClassVar[str] = "~"

    def __post_init__(self):
        """Pass."""
        if not is_str(self.name):
            self.name = self.attr

    @property
    def search_prefix(self) -> str:
        """Pass."""
        return f"{self.name}{self.search_delim}"

    def is_match(self, value: t.Any) -> bool:
        """Pass."""
        return is_str(value) and value.strip().startswith(self.search_prefix)

        # import re
        # matches: bool = False
        # if is_str(search):
        #     search: str = search.strip()
        #     if :
        #         chop: int = len(self.search_spec)
        #         search= search[chop:].lstrip()
        #         matches = True

        #         if search.startswith(self.pattern_prefix):
        #             search = re.compile(search[1:], re.I)

        # return matches, search


"""
def coerce_tilde_re(value):
    return re.compile(value[1:].strip(), re.I)

def is_list(value):
    return isinstance(value, (list, tuple))

def is_int_float(value):
    if is_list(value):
        return all([is_int_float(value=x) for x in value])
    return isinstance(value, (int, float))
"""


@dataclasses.dataclass()
class SearchString(Search):
    """Pass.

    "=name of item 123"
    operators: t.List[str] = ["="]
    name: str = "string_equals"
    check: bool = value == attr_value

    "~name of item"
    operators: t.List[str] = ["~"]
    name: str = "string_pattern"
    value: re.Pattern = coerce_tilde_re(value=value)
    check: bool = is_pattern(value) and value.search(str(attr_value))

    "name of item 456"
    default: "string_equals"
    """

    @property
    def operators(self) -> t.Dict[str, callable]:
        """Pass."""
        return {
            "=": self.string_equals,
            "~": self.string_pattern,
        }

    @property
    def operator_default(self) -> callable:
        """Pass."""
        return self.string_equals


@dataclasses.dataclass()
class SearchOperator:
    """Pass."""

    coercer: callable
    operator: str
    example_value: str
    search: "Search"


@dataclasses.dataclass()
class SearchDate(Search):
    """Pass.

    ">24"
    operators: t.List[str] = [">"]
    name: str = "date_more_than_hours
    value: t.Union[int, float] = coerce_int_float(value[1:].strip())
    attr_value: t.Optional[float] = get_hours_ago(value=attr_value)
    check: bool = is_int_float([value, attr_value]) and attr_value >= value

    "<24"
    operators: t.List[str] = ["<"]
    name: str = "date_less_than_hours
    value: t.Union[int, float] = coerce_int_float(value[1:].strip())
    attr_value: t.Optional[float] = get_hours_ago(value=attr_value)
    check: bool = is_int_float([value, attr_value]) and value >= attr_value

    "~24"
    operators: t.List[str] = ["~"]
    name: str = "date_pattern"
    value: re.Pattern = coerce_tilde_re(value=value)
    check: bool = is_pattern(value) and value.search(str(attr_value))

    "24"
    default: "date_less_than_hours
    """

    @property
    def operators(self) -> t.List[SearchOperator]:
        """Pass."""
        return [
            SearchOperator(
                coercer=self.date_more_than_hours,
                operator=">",
                example=">24",
                purpose="date hours ago is more than",
                search=self,
            ),
            SearchOperator(
                coercer=self.date_less_than_hours,
                operator="<",
                example="<24",
                purpose="date hours ago is less than",
                search=self,
            ),
            SearchOperator(
                coercer=self.date_pattern,
                operator="~",
                example="~Feb",
                purpose="date string matches regex",
                search=self,
            ),
        ]

    @property
    def operator_default(self) -> callable:
        """Pass."""
        return self.date_less_than_hours


@dataclasses.dataclass()
class SearchListString(Search):
    """Pass.

    "=test3"
    operators: t.List[str] = ["="]
    name: str = "list_string_equals"
    check: bool = is_list(attr_value) and value in attr_value

    "~test" == any([pattern.search(str(x), re.I) for x in value])
    operators: t.List[str] = ["~"]
    name: str = "list_string_pattern"
    value: re.Pattern = coerce_tilde_re(value=value)
    check: bool = is_list(attr_value) and is_pattern(value) and
        any([value.search(x) for x in attr_value)])

    "test4"
    default": "list_string_equals"
    """

    @property
    def operators(self) -> t.Dict[str, callable]:
        """Pass."""
        return {
            "=": self.list_string_equals,
            "~": self.list_string_pattern,
        }

    @property
    def operator_default(self) -> callable:
        """Pass."""
        return self.list_string_equals


@dataclasses.dataclass()
class SearchBool(Search):
    """Pass.

    "=true" or "=false"
    operators: t.List[str] = ["="]
    name: str = "bool_equals"
    value: bool = coerce_bool(obj=value)
    check: bool = value == attr_value

    "~true"
    operators: t.List[str] = ["~"]
    name: str = "bool_pattern"
    value: re.Pattern = coerce_tilde_re(value=value)
    check: bool = is_pattern(value) and value.search(str(attr_value))

    "true" or "false"
    default: "bool_equals"
    """

    @property
    def operators(self) -> t.Dict[str, callable]:
        """Pass."""
        return {
            "=": self.bool_equals,
            "~": self.bool_pattern,
        }

    @property
    def operator_default(self) -> callable:
        """Pass."""
        return self.bool_equals


@dataclasses.dataclass()
class SearchNumber(Search):
    """Pass.

    "+11"
    operators: t.List[str] = ["+"]
    name: str = "number_more_than"
    value: t.Union[int, float] = coerce_int_float(value[1:].strip())
    check: bool = is_int_float([value, attr_value]) and attr_value >= value

    "-11"
    operators: t.List[str] = ["-"]
    name: str = "number_less_than"
    value: t.Union[int, float] = coerce_int_float(value[1:].strip())
    check: bool = is_int_float([value, attr_value]) and value >= attr_value

    "=11"
    operators: t.List[str] = ["="]
    name: str = "number_equals"
    value: t.Union[int, float] = coerce_int_float(value[1:].strip())
    check: bool = is_int_float([value, attr_value]) and value == attr_value

    "11"
    default: "number_equals"
    """

    @property
    def operators(self) -> t.Dict[str, callable]:
        """Pass."""
        return {
            "+": self.number_more_than,
            "-": self.number_less_than,
            "=": self.number_equals,
        }

    @property
    def operator_default(self) -> callable:
        """Pass."""
        return self.number_equals


@dataclasses.dataclass()
class SearchWorker:
    """Pass."""

    value: str
    search: t.Optional[Search] = None
    valids: t.List[t.Any] = dataclasses.field(default_factory=list)


@dataclasses.dataclass()
class Searches:
    """Pass.

    examples:
        - "test" == obj.name == "test"
        - "name:test" == obj.name == "test"
        - "tags:beta" == any of obj.tags equals "beta"
        - "~test$" == obj.name matches "test$"
        - "name:~test[0-9]demo" == obj.name matches "test[0-9]demo"
        - "name:~test && tags:~^beta" == obj.name matches regex AND any of obj.tags matches "^beta"

    TBD:
        - add support for dot nation, ala obj.updated_by.last_name (where updated_by is a
          dict in json str) or obj.access.config (where access is a BaseModel)
          perhaps only one level deep?
    """

    searches: t.List[Search]
    default: Search
    and_op: str = "&&"

    def get_workers(self, values: t.Any) -> t.List[t.List[SearchWorker]]:
        """Pass."""
        return list(self._get_workers(values=values))

    def _get_workers(self, values: t.Any) -> t.Generator[t.List[SearchWorker], None, None]:
        """Pass."""
        values: t.List[t.Any] = [x for x in listify(values) if is_str(x)]
        for value in values:
            yield [self._get_worker(value=x) for x in self.split_and_op(value=value)]

    def _get_worker(self, value: t.Any) -> SearchWorker:
        """Pass."""
        for searcher in self.searches:
            if searcher.is_match(value=value):
                return SearchWorker(searcher=searcher, value=value)
        return SearchWorker(searcher=self.default, value=value)

    @classmethod
    def split_and_op(cls, value: t.Any) -> t.List[str]:
        """Pass."""
        ret: t.List[str] = []
        if is_str(value):
            ret = [x.strip() for x in value.split(cls.and_op) if is_str(x)]
        return ret


SavedQuerySearches: Searches = Searches(
    default=SearchString(attr="name"),
    searches=[
        SearchString(attr="name"),
        SearchString(attr="description"),
        SearchString(attr="sort_field"),
        SearchString(attr="query"),
        SearchString(attr="uuid"),
        SearchString(attr="module", name="asset_type"),
        SearchString(attr="created_by_str", name="created_by"),
        SearchString(attr="updated_by_str", name="updated_by"),
        SearchDate(attr="last_run_time", name="last_run"),
        SearchDate(attr="last_updated"),
        SearchListString(attr="fields"),
        SearchListString(attr="tags"),
        SearchBool(attr="always_cached", name="is_always_cached"),
        SearchBool(attr="is_referenced"),
        SearchNumber(attr="page_size"),
    ],
)
