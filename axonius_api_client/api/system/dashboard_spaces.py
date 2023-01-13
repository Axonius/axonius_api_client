# -*- coding: utf-8 -*-
"""API for working with dashboards and discovery lifecycle."""
import os
import pathlib
import typing as t

import requests

from ...constants.ctypes import PathLike
from ...exceptions import NotFoundError
from ...parsers.matcher import Matcher, MatcherLoad
from ...tools import dt_now_file, get_path, listify, path_write
from ..api_endpoints import ApiEndpoint, ApiEndpoints
from ..json_api.dashboard_spaces import (
    ExportableSpacesResponse,
    ExportSpacesRequest,
    ImportSpacesRequest,
    ImportSpacesResponse,
    SpaceCharts,
    SpacesDetails,
)
from ..json_api.spaces_export import SpacesExport
from ..mixins import ModelMixins


class DashboardSpaces(ModelMixins):
    """API for working with dashboard spaces and charts."""

    def get(self, charts: bool = True) -> t.List[t.Union[SpacesDetails, SpaceCharts]]:
        """Pass."""
        ret = self._get()
        if charts:
            ret = [self._get_single(uuid=x.uuid) for x in ret]
        return ret

    def export_charts_to_csv(
        self,
        spaces: t.Optional[MatcherLoad] = None,
        charts: t.Optional[MatcherLoad] = None,
        error: bool = False,
        **kwargs,
    ) -> t.List[t.Tuple[SpaceCharts, str]]:
        """Pass."""
        spaces_matcher: Matcher = Matcher.load(values=spaces, **kwargs)
        msg_spaces_parsed: str = f"User supplied space names:\n{spaces_matcher}"
        self.LOG.info(msg_spaces_parsed)

        charts_matcher: Matcher = Matcher.load(values=charts, **kwargs)
        msg_charts_parsed: str = f"User supplied chart names:\n{charts_matcher}"
        self.LOG.info(msg_charts_parsed)
        spaces = self.get()
        ret = []
        for space in spaces:
            if spaces_matcher.values and not spaces_matcher.equals(space.name):
                continue
            for chart in space.charts_by_order:
                if charts_matcher.values and not charts_matcher.equals(chart.name):
                    continue
                ret.append((chart, chart.export_to_csv(error=error)))
        return ret

    def export_charts_to_csv_path(
        self,
        path: t.Optional[PathLike] = None,
        spaces: t.Optional[MatcherLoad] = None,
        charts: t.Optional[MatcherLoad] = None,
        error: bool = False,
        **kwargs,
    ) -> t.List[t.Tuple[SpaceCharts, str, pathlib.Path]]:
        """Pass."""

        def doit(csv_export: t.Tuple[SpaceCharts, str]) -> t.Tuple[SpaceCharts, str, pathlib.Path]:
            chart, data = csv_export
            space = chart.SPACE
            filename = f"{space.name}__{chart.name}__{dt_now_file()}.csv"
            chart_path = path / filename
            result = path_write(obj=chart_path, data=data)
            return (chart, data, result[0])

        if path is None:
            path = os.getcwd()
        path = get_path(path)

        return [
            doit(x)
            for x in self.export_charts_to_csv(spaces=spaces, charts=charts, error=error, **kwargs)
        ]

    def export_spaces(
        self,
        names: MatcherLoad,
        postfix_names: t.Optional[str] = None,
        postfix_names_spaces: t.Optional[str] = None,
        postfix_names_charts: t.Optional[str] = None,
        postfix_names_queries: t.Optional[str] = None,
        exclude_names: t.Optional[MatcherLoad] = None,
        exclude_names_spaces: t.Optional[MatcherLoad] = None,
        exclude_names_charts: t.Optional[MatcherLoad] = None,
        error_not_matched: bool = True,
        **kwargs,
    ) -> SpacesExport:
        """Export dashboard spaces, charts, and their queries.

        Args:
            names (MatcherLoad): names of dashboard spaces to export
            postfix_names (t.Optional[str], optional): str to add to names of all spaces,
                charts, and queries
            postfix_names_spaces (t.Optional[str], optional): str to add to names of spaces
            postfix_names_charts (t.Optional[str], optional): str to add to names of charts
            postfix_names_queries (t.Optional[str], optional): str to add to names of queries
            exclude_names (t.Optional[MatcherLoad], optional): Exclude any spaces or charts
                that equal these names or match these patterns
            exclude_names_spaces (t.Optional[MatcherLoad], optional): Exclude any spaces that
                equal these names or match these patterns
            exclude_names_charts (t.Optional[MatcherLoad], optional): Exclude any charts that
                equal these names or match these patterns
            error_not_matched (bool, optional): error on names provided that do not match the
                names of any existing dashboard space

        """
        data_args = dict(
            postfix_names=postfix_names,
            postfix_names_spaces=postfix_names_spaces,
            postfix_names_charts=postfix_names_charts,
            postfix_names_queries=postfix_names_queries,
            exclude_names=exclude_names,
            exclude_names_spaces=exclude_names_spaces,
            exclude_names_charts=exclude_names_charts,
        )

        desc = "Dashboard Space Names"
        msg_supplied: str = f"User supplied {desc} (pre-parse):\n{names!r}"
        self.LOG.debug(msg_supplied)
        valid_names = kwargs.get("valid_names")
        if not (isinstance(valid_names, (list, tuple)) and valid_names):
            valid_names: t.List[str] = self.get_exportables()
            msg_valid: str = f"Valid {desc} for exporting (fetched):\n{valid_names!r}"
        else:
            msg_valid: str = f"Valid {desc} for exporting (cached):\n{valid_names!r}"

        self.LOG.debug(msg_valid)
        matcher: Matcher = Matcher.load(values=names, **kwargs)
        msg_parsed: str = f"User supplied {desc} Dashboard Space names (parsed):\n{matcher}"
        self.LOG.debug(msg_parsed)

        matched, not_matched = matcher.matches(values=valid_names)
        msg_matched: str = f"Matched {desc}:\n{matched!r}"
        msg_not_matched: str = f"Not Matched {desc}:\n{not_matched!r}"
        msgs = "\n\n".join([msg_supplied, msg_valid, msg_parsed, msg_matched, msg_not_matched])

        if matched:
            self.LOG.debug(msg_matched)
        else:
            raise NotFoundError(f"No matching {desc} found!\n\n{msgs}")

        if not_matched:
            if error_not_matched:
                raise NotFoundError(
                    f"error_not_matched=True and some names provided did not match!\n\n{msgs}"
                )
            else:
                self.LOG.warning(msg_not_matched)
        else:
            self.LOG.debug(msg_not_matched)

        data: dict = self._export_spaces(spaces=matched, as_template=False)
        data_obj: SpacesExport = self.load_export_data(data=data, **data_args)
        return data_obj

    def import_spaces(
        self,
        data: t.Union["SpacesExport", dict],
        postfix_names: t.Optional[str] = None,
        postfix_names_spaces: t.Optional[str] = None,
        postfix_names_charts: t.Optional[str] = None,
        postfix_names_queries: t.Optional[str] = None,
        exclude_names: t.Optional[MatcherLoad] = None,
        exclude_names_spaces: t.Optional[MatcherLoad] = None,
        exclude_names_charts: t.Optional[MatcherLoad] = None,
        replace: bool = False,
    ) -> ImportSpacesResponse:
        """Import dashboard spaces, charts, and their queries.

        Args:
            data (t.Union["SpacesExport", dict]): Space data from an export
            postfix_names (t.Optional[str], optional): str to add to names of all spaces,
                charts, and queries
            postfix_names_spaces (t.Optional[str], optional): str to add to names of spaces
            postfix_names_charts (t.Optional[str], optional): str to add to names of charts
            postfix_names_queries (t.Optional[str], optional): str to add to names of queries
            exclude_names (t.Optional[MatcherLoad], optional): Exclude any spaces or charts
                that equal these names or match these patterns
            exclude_names_spaces (t.Optional[MatcherLoad], optional): Exclude any spaces that
                equal these names or match these patterns
            exclude_names_charts (t.Optional[MatcherLoad], optional): Exclude any charts that
                equal these names or match these patterns
            replace (bool, optional): If true and objects exist with same name, imported objects
                will replace existing objects. If False and objects exist with same name,
                imported objects will be renamed
        """
        data_args = dict(
            postfix_names=postfix_names,
            postfix_names_spaces=postfix_names_spaces,
            postfix_names_charts=postfix_names_charts,
            postfix_names_queries=postfix_names_queries,
            exclude_names=exclude_names,
            exclude_names_spaces=exclude_names_spaces,
            exclude_names_charts=exclude_names_charts,
        )
        data_obj: SpacesExport = self.load_export_data(data=data, **data_args)
        data: dict = data_obj.to_dict()
        response: ImportSpacesResponse = self._import_spaces(data=data, replace=replace)
        response.spaces_export = data_obj
        return response

    def get_exportables(self) -> t.List[str]:
        """Get a list of Dashboard Space names that are valid for exporting.

        Returns:
            t.List[str]: exportable Dashboard Space names
        """
        model: ExportableSpacesResponse = self._get_exportables()
        data: t.List[str] = model.spaces
        return data

    def load_export_data(
        self,
        data: t.Union["SpacesExport", dict],
        postfix_names: t.Optional[str] = None,
        postfix_names_spaces: t.Optional[str] = None,
        postfix_names_charts: t.Optional[str] = None,
        postfix_names_queries: t.Optional[str] = None,
        exclude_names: t.Optional[MatcherLoad] = None,
        exclude_names_spaces: t.Optional[MatcherLoad] = None,
        exclude_names_charts: t.Optional[MatcherLoad] = None,
        **kwargs,
    ) -> SpacesExport:
        """Load a dashboard spaces export into a dataclass.

        Args:
            data (t.Union["SpacesExport", dict]): Space data from an export
            postfix_names (t.Optional[str], optional): str to add to names of all spaces,
                charts, and queries
            postfix_names_spaces (t.Optional[str], optional): str to add to names of spaces
            postfix_names_charts (t.Optional[str], optional): str to add to names of charts
            postfix_names_queries (t.Optional[str], optional): str to add to names of queries
            exclude_names (t.Optional[MatcherLoad], optional): Exclude any spaces or charts
                that equal these names or match these patterns
            exclude_names_spaces (t.Optional[MatcherLoad], optional): Exclude any spaces that
                equal these names or match these patterns
            exclude_names_charts (t.Optional[MatcherLoad], optional): Exclude any charts that
                equal these names or match these patterns

        """
        data_args = dict(
            postfix_names=postfix_names,
            postfix_names_spaces=postfix_names_spaces,
            postfix_names_charts=postfix_names_charts,
            postfix_names_queries=postfix_names_queries,
            exclude_names=exclude_names,
            exclude_names_spaces=exclude_names_spaces,
            exclude_names_charts=exclude_names_charts,
        )

        ret = SpacesExport.load(data=data, **data_args)
        self.LOG.debug(f"Export loaded:\n{ret}")
        return ret

    def _get_exportables(self) -> ExportableSpacesResponse:
        """Direct API method to get exportable names.

        Returns:
            ExportableSpacesResponse: JSON API data model
        """
        api_endpoint: ApiEndpoint = ApiEndpoints.dashboard_spaces.get_exportable_space_names
        response: ExportableSpacesResponse = api_endpoint.perform_request(http=self.auth.http)
        return response

    def _get(self) -> t.List[SpacesDetails]:
        """Pass."""
        api_endpoint: ApiEndpoint = ApiEndpoints.dashboard_spaces.get
        response: ImportSpacesResponse = api_endpoint.perform_request(http=self.auth.http)
        return response

    def _get_single(self, uuid: str) -> SpaceCharts:
        """Pass."""
        api_endpoint: ApiEndpoint = ApiEndpoints.dashboard_spaces.get_single
        response: ImportSpacesResponse = api_endpoint.perform_request(
            http=self.auth.http, uuid=uuid
        )
        return response

    def _export_chart_csv(self, uuid: str) -> str:
        """Pass."""
        api_endpoint: ApiEndpoint = ApiEndpoints.dashboard_spaces.export_chart_csv
        response: str = api_endpoint.perform_request(http=self.auth.http, uuid=uuid)
        return response

    def _import_spaces(self, data: dict, replace: bool = False) -> ImportSpacesResponse:
        """Direct API method to import dashboard spaces, charts, and their queries.

        Args:
            data (dict): Space data from an export
            replace (bool, optional): If true and objects exist with same name, imported objects
                will replace existing objects. If False and objects exist with same name,
                imported objects will be renamed
        """
        api_endpoint: ApiEndpoint = ApiEndpoints.dashboard_spaces.import_spaces
        request_obj: ImportSpacesRequest = api_endpoint.request_model_cls(
            data=data, replace=replace
        )
        response: ImportSpacesResponse = api_endpoint.perform_request(
            request_obj=request_obj, http=self.auth.http
        )
        return response

    def _export_spaces(
        self, spaces: t.List[str], as_template: bool = False
    ) -> t.Union[bytes, dict]:
        """Direct API method to export dashboard spaces, charts, and their queries.

        Args:
            spaces (t.List[str]): list of spaces to export
            as_template (bool, optional): Returns a zip file as byte string, deprecated feature
        """
        spaces: t.List[str] = listify(spaces)
        api_endpoint: ApiEndpoint = ApiEndpoints.dashboard_spaces.export_spaces
        request_obj: ExportSpacesRequest = api_endpoint.request_model_cls(
            spaces=spaces, as_template=as_template
        )
        raw: bool = request_obj.as_template
        response: t.Union[dict, requests.Response] = api_endpoint.perform_request(
            request_obj=request_obj, raw=raw, http=self.auth.http
        )

        if raw:
            api_endpoint.check_response_status(http=self.auth.http, response=response)
            response: bytes = response.content

        return response
