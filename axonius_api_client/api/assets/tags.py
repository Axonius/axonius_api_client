# -*- coding: utf-8 -*-
"""API for working with tags for assets."""
import datetime
import typing as t

from ..json_api.assets import ModifyTagsRequest
from ..json_api.generic import IntValue, StrValue
from ..json_api.saved_queries import SavedQuery
from ...constants.ctypes import PathLike
from ...constants.fields import AXID
from ...exceptions import AxonError
from ...parsers.aql import join_and_or_not
from ...projects.cf_token.tools import echoer
from ...tools import coerce_int, confirm
from .. import AssetMixin
from ..api_endpoints import ApiEndpoints, AssetTags
from ..mixins import ChildMixins


class Tags(ChildMixins):
    """API for working with tags for the parent asset type.

    Examples:
        * Get all known tags: :meth:`get`
        * Add tags to assets: :meth:`add`
        * Remove tags from assets: :meth:`remove`
    """

    parent: AssetMixin = None

    # TODO: create an AssetTag object
    def get(self) -> t.List[str]:
        """Get all tags that exist for the parent asset type

        Returns:
            t.List[str]: all tags that exist for the parent asset type

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> apiobj.tags.get()
            ['tag1', 'tag2']
        """
        response: t.List[StrValue] = self.direct_get()
        data: t.List[str] = [x.value for x in response]
        return data

    def build_request_obj(
        self,
        tags: t.Union[str, t.List[str]],
        ids: t.Optional[t.Sequence[str]] = None,
        ids_from_assets: t.Optional[t.Union[dict, t.List[dict]]] = None,
        ids_from_files: t.Optional[t.Union[PathLike, t.List[PathLike]]] = None,
        ids_keys: t.Sequence[str] = AXID.KEYS,
        include: bool = False,
        query: t.Optional[str] = None,
        query_wizard: t.Optional[t.Union[str, t.List[str], dict, t.List[dict]]] = None,
        query_wizard_parsed: t.Optional[dict] = None,
        saved_queries: t.Optional[t.Union[str, t.List[str], SavedQuery, t.List[SavedQuery]]] = None,
        history_date: t.Optional[t.Union[str, datetime.timedelta, datetime.datetime]] = None,
        history_days_ago: t.Optional[int] = None,
        history_exact: bool = False,
        history_date_parsed: t.Optional[str] = None,
        count_target: t.Optional[int] = None,
        count_target_minimum: t.Optional[int] = None,
        count_target_maximum: t.Optional[int] = None,
        request_obj: t.Optional[ModifyTagsRequest] = None,
        request_append: bool = True,
        prompt: bool = True,
        prompt_default: bool = False,
        verified: bool = False,
        echo: bool = True,
        **kwargs: t.Any,
    ) -> ModifyTagsRequest:
        """Build a request object for the tags API.

        Args:
            tags: tags to modify
            ids: internal_axon_id strings to modify or to exclude from query if `include` is False
            ids_from_assets: assets to get `id_keys` from and append to `ids`
            ids_from_files: .json, .jsonl, or .csv files to get `id_keys` from and append to `ids`
            ids_keys: keys to check in order to find valid internal_axon_id strings
            include: True: target=internal_axon_id in [`ids`] (ignores `query`),
                False: target=(`query`) and (not (internal_axon_id in [`ids`])) on `history_date`
            query: query to target assets
            query_wizard: entries to create query using query wizard
            query_wizard_parsed: (overrides `query_wizard`) parsed query wizard dict
            saved_queries: saved queries to AND with `query`
            history_date: (overrides `history_days_ago`) date for `query` to target assets
            history_days_ago: days ago for `query` to target assets
            history_exact: False=pick closest date if not found, True=error if not found
            history_date_parsed: (overrides `history_*`) parsed history date
            count_target: use this value instead of getting count of target assets to be modified
            count_target_minimum: error if count_target is less than this value
            count_target_maximum: error if count_target is greater than this value
            prompt: if not `verified`, True: prompt with count_target; False: error
            prompt_default: default prompt value if `prompt`
            verified: True: do not prompt, False: prompt with `count_target` if `prompt` else error
            echo: echo output to stderr
            request_obj: request object to send to the API
            request_append: True: append or replace values in provided `request_obj`
            **kwargs: used to create :obj:`ModifyTagsRequest` if request_obj is not provided
        """
        # TODO
        echoer(
            [
                f"ids_keys={ids_keys}",
                f"ids_from_assets={ids_from_assets}",
                f"ids_from_files={ids_from_files}",
                f"saved_queries={saved_queries}",
            ],
            echo=echo,
        )
        request_obj: ModifyTagsRequest = (
            request_obj
            if isinstance(request_obj, ModifyTagsRequest)
            else self.endpoints.remove.load_request(**kwargs)
        )

        request_obj.set_include(include=include, echo=echo)
        request_obj.set_tags(tags=tags, append=request_append, echo=echo)
        # TODO --> add support for ids_from_assets using Grabber... from_dicts?
        # TODO --> add support for ids_from_files using Grabber... from_files?
        """
        will need to write something like
        paths = listify(ids_from_files) 
        paths = [pathify(x) for x in paths if is_str(x) or isinstance(x, pathlib.Path)]
        for path in paths:
            if not path.is_file():
                echoer(f"ignoring invalid file path: {path}", level="error", echo=echo)
            if path.suffix == ".csv":
                echoer(f"reading ids from csv file: {path}", echo=echo)
                ids_from_files = Grabber.from_csv(path=path, keys=ids_keys)
            elif path.suffix == ".json":
                echoer(f"reading ids from json file: {path}", echo=echo)
                ids_from_files = Grabber.from_json(path=path, keys=ids_keys)
            elif path.suffix == ".jsonl":
                echoer(f"reading ids from jsonl file: {path}", echo=echo)
                ids_from_files = Grabber.from_jsonl(path=path, keys=ids_keys)
            else:
                echoer(f"ignoring unsupported file type: {path.suffix}", level="error", echo=echo)
        """
        request_obj.set_ids(ids=ids, append=request_append, echo=echo)
        # TODO VALIDATE SUPPLIED IDS BY GETTING COUNT OF internal_axon_id in [$ids_csv]
        """
        if not ids_verified and request_obj.ids:
             request_obj.ids_
                
        """
        # and comparing to len(ids) - if not equal, error
        # TODO --> HISTORY DATE
        use_history: t.Optional[str, datetime.datetime] = (
            request_obj.history_date or history_date_parsed
        )
        if not use_history:
            if history_date is not None:
                history_dates = self.parent.history_dates_obj()
                use_history: str = history_dates.get_date_by_date(
                    value=history_date, exact=history_exact
                )
            elif history_days_ago is not None:
                history_dates = self.parent.history_dates_obj()
                use_history: str = history_dates.get_date_by_days_ago(
                    value=history_days_ago, exact=history_exact
                )
        request_obj.set_history_date(history_date=use_history, echo=echo)
        # TODO --> HISTORY DATE

        # TODO --> QUERY
        query_wizard_parsed: dict = (
            query_wizard_parsed
            if isinstance(query_wizard_parsed, dict) and query_wizard_parsed.get("query")
            else self.parent.get_wiz_entries(wiz_entries=query_wizard) or {}
        )

        sources: t.Dict[str, t.Optional[str]] = {
            "supplied `query`": query,
            "supplied `wizard`": query_wizard_parsed.get("query"),
            "supplied `request_obj`": request_obj.filter,
        }
        # TODO NEED TO FETCH SAVED QUERIES
        # we want to use Matcher to allow for regex matching
        # sources.update({f"query from `saved_queries` {x.name}": x.query for x in saved_queries})

        # TODO THIS IS NOT WORKING: Getting None
        use_query = join_and_or_not(*sources.values())
        request_obj.set_query(query=use_query, echo=echo)
        # TODO --> QUERY

        request_obj.check_request(echo=echo)

        # TODO --> CHECK COUNT TARGET
        count_target: t.Optional[int] = coerce_int(obj=count_target, allow_none=True)
        count_max: t.Optional[int] = coerce_int(obj=count_target_maximum, allow_none=True)
        count_min: t.Optional[int] = coerce_int(obj=count_target_minimum, allow_none=True)

        if isinstance(count_target, int):
            target_source: str = f"user supplied count_target: {count_target}"
        else:
            count_target_query: str = request_obj.count_target_query
            target_source: str = f"fetching count of {request_obj.count_target_calculation}"
            count_target: int = self.parent.count(query=count_target_query)

        is_min_met: bool = count_target >= count_min if isinstance(count_min, int) else True
        is_max_met: bool = count_target <= count_max if isinstance(count_max, int) else True
        is_ok: bool = is_min_met and is_max_met
        is_error: bool = not is_ok
        counts: t.List[str] = [
            f"count_target={count_target}",
            f"count_target_source={target_source}",
            f"count_target_minimum={count_min}",
            f"count_target_maximum={count_max}",
            f"count_target >= count_target_minimum: {is_min_met}",
            f"count_target <= count_target_maximum: {is_max_met}",
        ]
        if is_error:
            raise AxonError([request_obj.ERROR_RANGE, *counts])
        if verified:
            echoer([request_obj.VERIFIED, *counts], echo=echo, level="debug")
        else:
            if prompt:
                confirm(
                    msgs=request_obj.TARGET,
                    text="\n".join(counts),
                    text_confirm=f"Please confirm you want to modify {count_target} assets",
                    default=prompt_default,
                    abort=True,
                )
            else:
                raise AxonError([request_obj.ERROR_FALSE, *counts])
        # TODO --> CHECK COUNT TARGET

        return request_obj

    def add(self, echo: bool = True, **kwargs) -> int:
        """Add tags to assets of the parent asset type.

        Args:
            echo: echo output to stderr
            **kwargs: passed to :meth:`_add_remove`

        Returns:
            int: number of assets that were modified by the REST API
        """
        request_obj = self.build_request_obj(echo=echo, **kwargs)
        response: IntValue = self.direct_add(request_obj=request_obj)
        count_modified: int = response.value
        return count_modified

    def remove(self, echo: bool = True, **kwargs) -> int:
        """Remove tags from assets of the parent asset type.

        Args:
            echo: echo output to stderr
            **kwargs: used to create :obj:`ModifyTagsRequest` if request_obj is not provided

        Returns:
            int: number of assets that were modified by the REST API
        """
        request_obj = self.build_request_obj(echo=echo, **kwargs)
        response: IntValue = self.direct_remove(request_obj=request_obj)
        count_modified: int = response.value
        return count_modified

    def direct_get(self) -> t.List[StrValue]:
        """Direct API method to get all known tags."""
        response: t.List[StrValue] = self.endpoints.get.perform_request(
            http=self.auth.http, asset_type=self.parent.ASSET_TYPE
        )
        return response

    @property
    def endpoints(self) -> AssetTags:
        """API endpoint group for this API model."""
        return ApiEndpoints.assets.tags

    # noinspection PyShadowingBuiltins
    def direct_add(self, request_obj: t.Optional[ModifyTagsRequest] = None, **kwargs) -> IntValue:
        """Direct API method to add labels to assets of the parent asset type.

        Args:
            request_obj: request object to send to the API
            **kwargs: used to create :obj:`ModifyTagsRequest` if request_obj is not provided

        Returns:
            IntValue: number of assets that were modified by the REST API
        """
        request_obj = (
            request_obj
            if isinstance(request_obj, ModifyTagsRequest)
            else self.endpoints.remove.load_request(**kwargs)
        )
        response: IntValue = self.endpoints.add.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=self.parent.ASSET_TYPE
        )
        return response

    # noinspection PyShadowingBuiltins
    def direct_remove(
        self, request_obj: t.Optional[ModifyTagsRequest] = None, **kwargs
    ) -> IntValue:
        """Direct API method to remove labels from assets of the parent asset type.

        Args:
            request_obj: request object to send to the API
            **kwargs: used to create :obj:`ModifyTagsRequest` if request_obj is not provided

        Returns:
            IntValue: number of assets that were modified by the REST API
        """
        request_obj = (
            request_obj
            if isinstance(request_obj, ModifyTagsRequest)
            else self.endpoints.remove.load_request(**kwargs)
        )
        response: IntValue = self.endpoints.remove.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=self.parent.ASSET_TYPE
        )
        return response
