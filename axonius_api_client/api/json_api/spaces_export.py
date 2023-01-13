# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import copy
import dataclasses
import typing as t

from ...constants.ctypes import PathLike
from ...exceptions import ApiError
from ...parsers.matcher import Matcher, MatcherLoad
from ...tools import coerce_bool, is_str, json_dump, json_load, strip_right


@dataclasses.dataclass
class QueryExport:
    """Pass."""

    data: dict
    parent: "SpaceExport"
    dependencies: t.Optional[dict] = dataclasses.field(default_factory=dict)
    purpose: t.Optional[str] = None

    @property
    def name(self) -> str:
        """Pass."""
        return self.data["name"]

    @name.setter
    def name(self, value: str) -> None:
        self.data["name"] = value

    @property
    def uuid(self) -> str:
        """Pass."""
        return self.data["_id"]["$oid"]

    @property
    def module(self) -> str:
        """Pass."""
        return self.data["module"]

    @property
    def dependents(self) -> t.List[str]:
        """Pass."""
        ret = []

        for uuid, uuids in self.dependencies.items():
            if self.uuid in uuids:
                ret.append(self.parent.query_by_module(module=self.module, value=uuid))

        return ret

    def to_str(self, dependency: bool = False) -> t.List[str]:
        """Pass."""
        info = []
        if is_str(self.purpose):
            info.append(f"usage={self.purpose!r}")
        info += [
            f"module={self.module!r}",
            # f"uuid={self.uuid!r}",
            f"name={self.name!r}",
        ]
        info = ", ".join(info)
        pre = "Query Dependency" if dependency else "Query"
        items = [
            f"{pre} {info}",
        ]
        for query in self.dependents:
            items += [f"  {x}" for x in query.to_str(dependency=True)]
        return items

    def __str__(self) -> str:
        """Pass."""
        return "\n".join(self.to_str())

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()


@dataclasses.dataclass
class ChartExport:
    """Pass."""

    data: dict
    parent: "SpaceExport"

    @property
    def excluded(self) -> bool:
        """Pass."""
        return self.data.get("$excluded", False)

    @excluded.setter
    def excluded(self, value: bool):
        """Pass."""
        if coerce_bool(value):
            self.data["$excluded"] = True

    @property
    def excluded_str(self) -> str:
        """Pass."""
        return "[EXCLUDED] " if self.excluded else ""

    @property
    def uuid(self) -> str:
        """Pass."""
        return self.data["_id"]["$oid"]

    @property
    def name(self) -> str:
        """Pass."""
        return self.data["name"]

    @name.setter
    def name(self, value: str) -> None:
        self.data["name"] = value

    @property
    def type(self) -> str:
        """Pass."""
        return self.data["metric"]

    @property
    def config(self) -> dict:
        """Pass."""
        return self.data["config"]

    @property
    def module(self) -> t.Optional[str]:
        """Pass."""
        return self.config.get("entity")

    @property
    def modules(self) -> t.List[str]:
        """Pass."""
        return (
            list(
                set(
                    [
                        x.get("entity")
                        for x in self.views
                        if isinstance(x, dict) and is_str(x.get("entity"))
                    ]
                )
            )
            if isinstance(self.views, list)
            else []
        )

    @property
    def view(self) -> t.Optional[str]:
        """Pass."""
        return self.config.get("view")

    @property
    def selected_view(self) -> t.Optional[str]:
        """Pass."""
        return self.config.get("selected_view")

    @property
    def base_view(self) -> t.Optional[str]:
        """Pass."""
        return self.config.get("base")

    @property
    def intersecting_views(self) -> t.Optional[t.List[str]]:
        """Pass."""
        return self.config.get("intersecting")

    @property
    def views(self) -> t.Optional[t.List[dict]]:
        """Pass."""
        return self.config.get("views")

    @property
    def queries(self) -> t.List[QueryExport]:
        """Pass."""
        ret = []

        if is_str(self.module):
            if is_str(self.view):
                ret.append(
                    self.parent.parent.query_by_module(
                        module=self.module, value=self.view, purpose="query"
                    )
                )

            if is_str(self.selected_view):
                ret.append(
                    self.parent.parent.query_by_module(
                        module=self.module, value=self.selected_view, purpose="query"
                    )
                )

            if is_str(self.base_view):
                ret.append(
                    self.parent.parent.query_by_module(
                        module=self.module, value=self.base_view, purpose="base"
                    )
                )

            if isinstance(self.intersecting_views, list):
                ret += [
                    self.parent.parent.query_by_module(
                        module=self.module, value=x, purpose="intersect"
                    )
                    for x in self.intersecting_views
                ]

        if isinstance(self.views, list):
            ret += [
                self.parent.parent.query_by_module(
                    module=x["entity"], value=x["id"], purpose="queries"
                )
                for x in self.views
                if isinstance(x, dict) and is_str(x.get("entity")) and is_str(x.get("id"))
            ]
        return ret

    @property
    def query_counts(self) -> int:
        """Pass."""
        return sum([1 + len(x.dependents) for x in self.queries])

    @property
    def module_str(self) -> str:
        """Pass."""
        return f"module={self.module!r}" if is_str(self.module) else f"modules={self.modules}"

    def to_str(self, queries: bool = True) -> t.List[str]:
        """Pass."""
        info = [
            f"queries={self.query_counts}",
            f"type={self.type!r}",
            self.module_str,
            # f"uuid={self.uuid!r}",
            f"name={self.name!r}",
        ]
        info = ", ".join(info)
        items = [
            f"{self.excluded_str}Chart {info}",
        ]
        if queries:
            for query in self.queries:
                items += [f"  {x}" for x in query.to_str()]
        return items

    def __str__(self) -> str:
        """Pass."""
        return "\n".join(self.to_str())

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()


@dataclasses.dataclass
class SpaceExport:
    """Pass."""

    data: dict
    parent: "SpacesExport"

    @property
    def excluded(self) -> bool:
        """Pass."""
        return self.data.get("$excluded", False)

    @excluded.setter
    def excluded(self, value: bool):
        """Pass."""
        if coerce_bool(value):
            self.data["$excluded"] = True

    @property
    def excluded_str(self) -> str:
        """Pass."""
        return "[EXCLUDED] " if self.excluded else ""

    @property
    def uuid(self) -> str:
        """Pass."""
        return self.space["_id"]["$oid"]

    @property
    def space(self) -> dict:
        """Pass."""
        return self.data["space"]

    @property
    def name(self) -> str:
        """Pass."""
        return self.space["name"]

    @name.setter
    def name(self, value: str) -> None:
        self.space["name"] = value

    @property
    def charts_order(self) -> t.List[str]:
        """Pass."""
        return self.space["panels_order"]

    @property
    def _charts(self) -> t.Dict[str, dict]:
        """Pass."""
        return self.data["charts"]

    @property
    def charts(self) -> t.List[ChartExport]:
        """Pass."""
        return [
            ChartExport(data=self._charts[x], parent=self)
            for x in self.charts_order
            if x in self._charts
        ]

    @property
    def chart_counts(self) -> int:
        """Pass."""
        return len(self.charts)

    @property
    def query_counts(self) -> int:
        """Pass."""
        return sum([x.query_counts for x in self.charts])

    def to_str(self, charts: bool = True, queries: bool = True) -> t.List[str]:
        """Pass."""
        info = [
            f"charts={self.chart_counts}",
            f"queries={self.query_counts}",
            # f"uuid={self.uuid!r}",
            f"name={self.name!r}",
        ]
        info = ", ".join(info)
        items = [
            "-" * 80,
            f"{self.excluded_str}Space {info}",
        ]
        if charts:
            for chart in self.charts:
                items += [f"  {x}" for x in chart.to_str(queries=queries)]
        return items

    def __str__(self) -> str:
        """Pass."""
        return "\n".join(self.to_str())

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()


@dataclasses.dataclass
class SpacesExport:
    """Pass."""

    data: dict
    postfix_names: t.Optional[str] = None
    postfix_names_spaces: t.Optional[str] = None
    postfix_names_charts: t.Optional[str] = None
    postfix_names_queries: t.Optional[str] = None
    exclude_names: t.Optional[MatcherLoad] = None
    exclude_names_spaces: t.Optional[MatcherLoad] = None
    exclude_names_charts: t.Optional[MatcherLoad] = None
    exclude_matcher_args: t.Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Pass."""
        if not isinstance(self.exclude_matcher_args, dict):
            self.exclude_matcher_args = {}

        self.set_excludes(
            names=self.exclude_names,
            spaces=self.exclude_names_spaces,
            charts=self.exclude_names_charts,
            **self.exclude_matcher_args,
        )
        self.add_postfix_names(value=self.postfix_names)
        self.add_postfix_names_spaces(value=self.postfix_names_spaces)
        self.add_postfix_names_charts(value=self.postfix_names_charts)
        self.add_postfix_names_queries(value=self.postfix_names_queries)

    def _err(self, msg: str, exc: t.Optional[Exception] = None):
        msg = f"Error parsing export data: {msg}"
        if exc is not None:
            msg += f"\nException: {type(exc)}: {exc}"
        raise ApiError(wrap_err_data(msg=msg, data=self.data))

    def set_excludes(
        self,
        names: t.Optional[MatcherLoad] = None,
        spaces: t.Optional[MatcherLoad] = None,
        charts: t.Optional[MatcherLoad] = None,
        **kwargs,
    ) -> t.Tuple[t.List[SpaceExport], t.List[ChartExport]]:
        """Pass."""
        names_matcher = Matcher.load(values=names, **kwargs)
        spaces_matcher = Matcher.load(values=spaces, **kwargs)
        charts_matcher = Matcher.load(values=charts, **kwargs)
        spaces_excluded = []
        charts_excluded = []
        for space in self.spaces:
            if spaces_matcher.equals(space.name) or names_matcher.equals(space.name):
                space.excluded = True
                spaces_excluded.append(space)
            for chart in space.charts:
                if charts_matcher.equals(chart.name) or names_matcher.equals(chart.name):
                    chart.excluded = True
                    charts_excluded.append(chart)
        return spaces_excluded, charts_excluded

    def add_postfix_names(self, value: t.Optional[str] = None):
        """Pass."""
        self.add_postfix_names_spaces(value=value)
        self.add_postfix_names_charts(value=value)
        self.add_postfix_names_queries(value=value)

    def add_postfix_names_spaces(self, value: t.Optional[str] = None):
        """Pass."""
        if isinstance(value, str):
            for space in self.spaces:
                space.name += value

    def add_postfix_names_charts(self, value: t.Optional[str] = None):
        """Pass."""
        if isinstance(value, str):
            for space in self.spaces:
                for chart in space.charts:
                    chart.name += value

    def add_postfix_names_queries(self, value: t.Optional[str] = None):
        """Pass."""
        if isinstance(value, str):
            for module, module_queries in self.queries.items():
                for query in module_queries:
                    query.name += value

    @classmethod
    def load(
        cls,
        data: t.Union["SpacesExport", dict, str, bytes, PathLike],
        postfix_names: t.Optional[str] = None,
        postfix_names_spaces: t.Optional[str] = None,
        postfix_names_charts: t.Optional[str] = None,
        postfix_names_queries: t.Optional[str] = None,
        exclude_names: t.Optional[MatcherLoad] = None,
        exclude_names_spaces: t.Optional[MatcherLoad] = None,
        exclude_names_charts: t.Optional[MatcherLoad] = None,
        **kwargs,
    ) -> "SpacesExport":
        """Pass."""
        cls_args = dict(
            postfix_names=postfix_names,
            postfix_names_spaces=postfix_names_spaces,
            postfix_names_charts=postfix_names_charts,
            postfix_names_queries=postfix_names_queries,
            exclude_names=exclude_names,
            exclude_names_spaces=exclude_names_spaces,
            exclude_names_charts=exclude_names_charts,
        )
        if isinstance(data, cls):
            return cls(data=data.to_dict(), **cls_args)

        pre = "Error parsing dashboard export data: "
        if not isinstance(data, dict):
            try:
                data = json_load(obj=data, **cls_args)
            except Exception as exc:
                msg = f"{pre}Expected dictionary, received {type(data)} instead"
                raise ApiError(wrap_err_data(msg=msg, data=data, exc=exc))

        if not isinstance(data, dict):
            msg = f"{pre}Expected dictionary, received {type(data)} instead"
            raise ApiError(wrap_err_data(msg=msg, data=data))

        try:
            ret = cls(data=data, **cls_args)
            str(ret)
        except Exception as exc:
            raise ApiError(f"{pre}{type(exc)}: {exc}")
        return ret

    def to_dict(self) -> dict:
        """Pass."""

        def filter_excludes(value):
            return {k: v for k, v in value.items() if not v.get("$excluded", False)}

        ret = copy.deepcopy(self.data)
        ret["spaces"] = filter_excludes(ret["spaces"])
        for space in ret["spaces"].values():
            space["charts"] = filter_excludes(space["charts"])
            space["space"]["panels_order"] = [
                x for x in space["space"]["panels_order"] if x in space["charts"]
            ]
        return ret

    def to_json(self) -> str:
        """Pass."""
        return json_dump(self.to_dict())

    @property
    def version(self) -> str:
        """Pass."""
        try:
            ret = self.data["version"]
        except Exception as exc:
            self._err("Problem accessing 'version' key", exc)
        return ret

    @property
    def exported_at(self) -> str:
        """Pass."""
        try:
            ret = self.data["exported_at"]
        except Exception as exc:
            self._err("Problem accessing 'exported_at' key", exc)
        return ret

    @property
    def _spaces(self) -> t.List[dict]:
        """Pass."""
        try:
            ret = list(self.data["spaces"].values())
        except Exception as exc:
            self._err("Problem accessing 'spaces' key", exc)
        return ret

    @property
    def spaces(self) -> t.List[SpaceExport]:
        """Pass."""
        ret = [SpaceExport(data=x, parent=self) for x in self._spaces]
        return ret

    @property
    def chart_count(self) -> int:
        """Pass."""
        return sum([len(x.charts) for x in self.spaces])

    @property
    def queries(self) -> t.Dict[str, t.List[QueryExport]]:
        """Pass."""
        ret = {}

        for k, v in self.data.items():
            if not k.endswith("_views"):
                continue

            module = strip_right(obj=k, fix="_views")
            if module not in ret:
                ret[module] = []

            if not isinstance(v, dict):
                continue

            views = v.get("views") or {}
            depedencies = v.get("dependencies") or {}

            if not isinstance(views, dict):
                continue

            ret[module] += [
                QueryExport(data=data, dependencies=depedencies, parent=self)
                for data in views.values()
            ]
        return ret

    def queries_by_module(self, module: str) -> t.List[QueryExport]:
        """Pass."""
        module = strip_right(obj=module, fix="_views")
        if module in self.queries:
            return self.queries[module]

        valid = list(self.queries)
        valid = "\n - " + "\n - ".join(valid)
        raise ApiError(f"Invalid module {module!r}, valids: {valid}")

    def query_by_module(
        self, module: str, value: str, purpose: t.Optional[str] = None, error: bool = True
    ) -> t.Optional[QueryExport]:
        """Pass."""
        queries = self.queries_by_module(module=module)
        for query in queries:
            if value in [query.uuid, query.name]:
                return dataclasses.replace(query, purpose=purpose)

        if not error:
            return None
        valid = (
            [f"Query(uuid={x.uuid!r}, name={x.name!r})" for x in queries] if queries else ["None!!"]
        )
        valid = "\n - " + "\n - ".join(valid)
        raise ApiError(
            f"No exported query from the {module!r} module found with a name or UUID of {value!r}!"
            f"\nValid exported queries for the {module!r} module:{valid}"
        )

    @property
    def query_module_counts(self) -> t.Dict[str, int]:
        """Pass."""
        return {k: len(v) for k, v in self.queries.items()}

    @property
    def _header(self) -> str:
        """Pass."""
        query_counts = sum(list(self.query_module_counts.values()))

        items = [
            f"version={self.version!r}",
            f"exported_on={self.exported_at!r}",
            f"spaces={len(self.spaces)}",
            f"charts={self.chart_count}",
            f"queries={query_counts}",
        ]
        return ", ".join(items)

    def to_str_queries(self) -> t.List[str]:
        """Pass."""
        items = []
        for module, module_queries in self.queries.items():
            items += [
                "-" * 40,
                f"Queries for module {module!r} ({len(module_queries)}):",
                *[f"  {x.name}" for x in module_queries],
            ]
        return items

    def to_str_spaces(self, charts: bool = True, queries: bool = True):
        """Pass."""
        items = []
        for space in self.spaces:
            items += space.to_str(queries=queries, charts=charts)
        return items

    def to_str(
        self,
        charts: bool = True,
        chart_queries: bool = True,
        queries: bool = True,
    ) -> t.List[str]:
        """Pass."""
        items = [f"Spaces Export {self._header}"]
        if queries:
            items += self.to_str_queries()
        items += self.to_str_spaces(queries=chart_queries, charts=charts)
        return items

    def __str__(self):
        """Pass."""
        return "\n".join(self.to_str())

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()


def wrap_err_data(msg: str, data: t.Any) -> str:
    """Pass."""
    return "\n\n".join([msg, f"{json_dump(data)}", msg])
