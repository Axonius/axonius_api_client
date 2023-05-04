# -*- coding: utf-8 -*-
"""API for working with tags for assets."""
import datetime
import typing as t

from ..json_api.assets import ModifyTagsRequest
from ..json_api.generic import IntValue, StrValue
from ...tools import coerce_bool, listify, get_axon_ids
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

    # TODO: catch up to remove
    def add(
        self,
        rows: t.Union[t.List[dict], str],
        tags: t.List[str],
        invert_selection: bool = False,
    ) -> int:
        """Add tags to assets of the parent asset type.

        Args:
            rows: list of internal_axon_id strs or list of assets returned from a get method
            tags: tags to add to the assets supplied in rows
            invert_selection: True=add tags to assets that ARE NOT supplied in rows;
                False=add tags to assets that ARE supplied in rows

        Returns:
            int: number of assets that were modified by the REST API

        Examples:
            Get a client
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            Get the total number of assets
            >>> total: int = apiobj.count()
            >>> total
            2010
            Get some assets using the query wizard in the API client
            >>> wiz_entries: str = 'simple os.type equals Windows'
            >>> data = apiobj.get(wiz_entries=wiz_entries)
            >>> len(data)
            513
            Add tags to assets that ARE supplied
            >>> modify: list[str] = ['api tag 1', 'api tag 2']
            >>> apiobj.tags.add(rows=data, tags=modify)
            513
            Add tags to assets that ARE NOT supplied
            >>> modified: int = apiobj.tags.add(rows=data, tags=modify, invert_selection=True)
            >>> modified
            1497

        """
        ids = get_axon_ids(rows=rows)
        response: IntValue = self.direct_add(labels=tags, ids=ids, include=not invert_selection)
        return response.value

    def remove(
        self,
        values: t.Union[str, t.List[str]],
        assets: t.Optional[t.List[dict]] = None,
        ids: t.Optional[t.List[str]] = None,
        query: t.Optional[str] = "",
        # prompt: bool = True
        # confirm: bool = False
        # echo: bool = True
        # TODO:
        #   if not request_obj.filter, not request_obj.ids, and invert_selection=True,
        #   do confirmation prompt if prompt = True and confirm = False
        #   just echo if prompt = True
        #   to confirm removing tags from all assets
        wiz_entries: t.Optional[t.Union[t.List[dict], t.List[str], dict, str]] = None,
        wiz_parsed: t.Optional[dict] = None,
        history_date: t.Optional[t.Union[str, datetime.timedelta, datetime.datetime]] = None,
        history_days_ago: t.Optional[int] = None,
        history_exact: bool = False,
        history_date_parsed: t.Optional[str] = None,
        invert_selection: bool = False,
        request_obj: t.Optional[ModifyTagsRequest] = None,
        **kwargs
    ) -> int:
        """Remove tags from assets of the parent asset type.

        Notes:
            The selection of assets that the REST API will modify is determined as follows:
            * API client:
              * query = `wiz_parsed` or `wiz_entries` or `query` or ""
              * history = `history_date` or `history_days_ago` or None
              * selection = (supplied `ids` + ids from supplied `assets`)
            * Server Side:
              * selection += results from `query` on `history`
              * if invert_selection; selection = [x for x in ids_all if x not in selection]

        Args:
            values: the tags to apply
            assets: apply `values` to these assets fetched from the `get` method of the
                parent asset type, will extract `internal_axon_id` key from each asset
            ids: apply `values` to these manually provided list of internal_axon_ids
            query: apply `values` to assets that match this query
            wiz_entries: (overrides `query`), wizard expressions to create query from using query
                wizard built into the API client
            wiz_parsed: (overrides `wiz_entries`, `query`), parsed output from a query wizard
            history_date: (overrides `history_days_ago`), run `query` against asset data
                from this data to select assets to apply `values` to
            history_days_ago: run `query` against asset data from this many days ago to select
                assets to apply `values` to
            history_exact: False=Use the closest match for history_date and history_days_ago,
                True=Use the exact match for history_date and history_days_ago and error
                if no exact match is found
            history_date_parsed: (overrides `history_date, history_days_ago`), previously parsed
                history date to use instead of parsing `history_date` and `history_days_ago`
            invert_selection: True=remove tags from assets that ARE NOT supplied in rows;
                False=remove tags from assets that ARE supplied in rows
            request_obj: request object to send to the API
            **kwargs: used to create :obj:`ModifyTagsRequest` if request_obj is not provided

        Returns:
            int: number of assets that were modified by the REST API

        Examples:
            Get a client
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            Get the total number of assets
            >>> total: int = apiobj.count()
            >>> total
            2010
            Get some assets using the query wizard in the API client
            >>> wizard: str = 'simple os.type equals Windows'
            >>> data = apiobj.get(wiz_entries=wizard)
            >>> len(data)
            # Remove tags from assets that ARE supplied in rows
            >>> modify: list[str] = ['api tag 1', 'api tag 2']
            >>> modified = apiobj.tags.remove(rows=data, tags=modify)
            TODO: update and finish this example
            >>> modified
            1
        """
        request_obj = (
            request_obj
            if isinstance(request_obj, ModifyTagsRequest)
            else self.endpoints.remove.load_request(**kwargs)
        )
        assets_ids = get_axon_ids(rows=listify(assets))
        request_obj.ids = request_obj.ids + listify(ids) + listify(assets_ids)
        request_obj.labels = listify(request_obj.labels) + listify(values)
        request_obj.include = not coerce_bool(invert_selection)
        request_obj.filter = self.parent.parsed_or_query(
            query=query, wiz_entries=wiz_entries, wiz_parsed=wiz_parsed, request_obj=request_obj
        )
        request_obj.history = self.parent.parsed_or_date(
            history_date=history_date,
            history_days_ago=history_days_ago,
            history_exact=history_exact,
            history_date_parsed=history_date_parsed,
            request_obj=request_obj,
        )
        response: IntValue = self.direct_remove(request_obj=request_obj)
        return response.value

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
