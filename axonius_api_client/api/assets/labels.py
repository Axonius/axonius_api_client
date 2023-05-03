# -*- coding: utf-8 -*-
"""API for working with tags for assets."""
from typing import List, Union

from ...tools import listify
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..mixins import ChildMixins


class Labels(ChildMixins):
    """API for working with tags for the parent asset type.

    Examples:
        * Get all known tags: :meth:`get`
        * Add tags to assets: :meth:`add`
        * Remove tags from assets: :meth:`remove`

    See Also:
        * Device assets :obj:`axonius_api_client.api.assets.devices.Devices`
        * User assets :obj:`axonius_api_client.api.assets.users.Users`

    """

    def get(self) -> List[str]:
        """Get all known tags.

        Examples:
            Get all known tags for this asset type

            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> apiobj.labels.get()
            ['tag1', 'tag2']

        """
        return [x.value for x in self._get()]

    def get_expirable_names(self) -> List[str]:
        """Get all known expirable tags.

        Examples:
            Get all known expirable tags for this asset type

            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> apiobj.labels.get_expirable_names()
            ['tag1', 'tag2']

        """
        return [x.value for x in self._get_expirable_names()]

    def add(
        self, rows: Union[List[dict], str], labels: List[str], invert_selection: bool = False
    ) -> int:
        """Add tags to assets.

        Examples:
            Get some assets to tag

            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> data = apiobj.get(wiz_entries=[{'type': 'simple', 'value': 'name equals test'}])
            >>> len(data)
            1

            >>> apiobj.labels.add(rows=rows, labels=['api tag 1', 'api tag 2'])
            1

        Args:
            rows: list of internal_axon_id strs or list of assets returned from a get method
            labels: tags to add
            invert_selection: True=add tags to assets that ARE NOT supplied in rows;
                False=add tags to assets that ARE supplied in rows

        """
        ids = self._get_ids(rows=rows)
        return self._add(labels=labels, ids=ids, include=not invert_selection).value

    def _add(
        self, labels: List[str], ids: List[str], include: bool = True
    ) -> json_api.generic.IntValue:
        """Direct API method to add labels/tags to assets.

        Args:
            labels: tags to process
            ids: internal_axon_id of assets to add tags to
            include: True=add tags to assets that ARE supplied in rows;
                False=add tags to assets that ARE NOT supplied in rows
        """
        api_endpoint = ApiEndpoints.assets.tags_add

        entities = {"ids": listify(ids), "include": include}
        request_obj = api_endpoint.load_request(entities=entities, labels=listify(labels))
        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=self.asset_type
        )

    def remove(self, rows: List[dict], labels: List[str], invert_selection: bool = False) -> int:
        """Remove tags from assets.

        Examples:
            Get some assets to un-tag
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> data = apiobj.get(wiz_entries=[{'type': 'simple', 'value': 'name equals test'}])
            >>> len(data)
            1
            >>> apiobj.labels.remove(rows=data, labels=['api tag 1', 'api tag 2'])
            1

        Args:
            rows: list of internal_axon_id strs or list of assets returned from a get method
            labels: tags to remove
            invert_selection: True=remove tags from assets that ARE NOT supplied in rows;
                False=remove tags from assets that ARE supplied in rows

        """
        ids: List[str] = self._get_ids(rows=rows)
        return self._remove(labels=labels, ids=ids, include=not invert_selection).value

    def _remove(
        self, labels: List[str], ids: List[str], include: bool = True
    ) -> json_api.generic.IntValue:
        """Direct API method to remove labels/tags from assets.

        Args:
            labels: tags to process
            ids: internal_axon_id of assets to remove tags from
            include: True=remove tags from assets that ARE supplied in rows;
                False=remove tags from assets that ARE NOT supplied in rows
        """
        api_endpoint = ApiEndpoints.assets.tags_remove

        entities = {"ids": listify(ids), "include": include}
        request_obj = api_endpoint.load_request(entities=entities, labels=listify(labels))
        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=self.asset_type
        )

    @staticmethod
    def _get_ids(rows: Union[List[dict], str]) -> List[str]:
        """Get the internal_axon_id from a list of assets.

        Args:
            rows: list of internal_axon_id strs or list of assets returned from a get method
        """
        return [x["internal_axon_id"] if isinstance(x, dict) else x for x in listify(rows)]

    # noinspection PyUnresolvedReferences
    @property
    def asset_type(self) -> str:
        """Get the asset type of the parent AssetMixin."""
        return self.parent.ASSET_TYPE

    def _get(self) -> List[json_api.generic.StrValue]:
        """Direct API method to get all known labels/tags."""
        api_endpoint = ApiEndpoints.assets.tags_get
        return api_endpoint.perform_request(http=self.auth.http, asset_type=self.asset_type)

    def _get_expirable_names(self) -> List[json_api.generic.StrValue]:
        """Direct API method to get all known expirable labels/tags."""
        api_endpoint = ApiEndpoints.assets.tags_get_expirable_names
        return api_endpoint.perform_request(http=self.auth.http, asset_type=self.asset_type)
