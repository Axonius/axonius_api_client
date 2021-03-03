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
        Create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
        ``apiobj`` is either ``client.devices`` or ``client.users``

        >>> apiobj = client.devices  # or client.users

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

            >>> apiobj.labels.get()
            ['tag1', 'tag2']

        """
        return [x.value for x in self._get()]

    def add(self, rows: Union[List[dict], str], labels: List[str]) -> int:
        """Add tags to assets.

        Examples:
            Get some assets to tag

            >>> rows = apiobj.get(wiz_entries=[{'type': 'simple', 'value': 'name equals test'}])
            >>> len(rows)
            1

            >>> apiobj.labels.add(rows=rows, labels=['api tag 1', 'api tag 2'])
            1

        Args:
            rows: list of internal_axon_id strs or list of assets returned from a get method
            labels: tags to add
        """
        ids = self._get_ids(rows=rows)
        return self._add(labels=labels, ids=ids).value

        # processed = 0

        # # only do 100 labels at a time, more seems to break API
        # for group in grouper(ids, 100):
        #     group = [x for x in group if x is not None]
        #     response = self._add(labels=labels, ids=group)
        #     processed += response

        # return processed

    def remove(self, rows: List[dict], labels: List[str]) -> int:
        """Remove tags from assets.

        Examples:
            Get some assets to un-tag

            >>> rows = apiobj.get(wiz_entries=[{'type': 'simple', 'value': 'name equals test'}])
            >>> len(rows)
            1

            >>> apiobj.labels.remove(rows=rows, labels=['api tag 1', 'api tag 2'])
            1

        Args:
            rows: list of internal_axon_id strs or list of assets returned from a get method
            labels: tags to remove
        """
        ids = self._get_ids(rows=rows)
        return self._remove(labels=labels, ids=ids).value

    def _get_ids(self, rows: Union[List[dict], str]) -> List[str]:
        """Get the internal_axon_id from a list of assets.

        Args:
            rows: list of internal_axon_id strs or list of assets returned from a get method
        """
        return [x["internal_axon_id"] if isinstance(x, dict) else x for x in listify(rows)]

    def _add(self, labels: List[str], ids: List[str]) -> json_api.generic.IntValue:
        """Direct API method to add labels/tags to assets.

        Args:
            labels: tags to process
            ids: internal_axon_id of assets to add tags to
        """
        api_endpoint = ApiEndpoints.assets.tags_add

        entities = {"ids": listify(ids), "include": True}
        request_obj = api_endpoint.load_request(entities=entities, labels=listify(labels))
        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=self.parent.ASSET_TYPE
        )

    def _get(self) -> List[json_api.generic.StrValue]:
        """Direct API method to get all known labels/tags."""
        api_endpoint = ApiEndpoints.assets.tags_get
        return api_endpoint.perform_request(http=self.auth.http, asset_type=self.parent.ASSET_TYPE)

    def _remove(self, labels: List[str], ids: List[str]) -> json_api.generic.IntValue:
        """Direct API method to remove labels/tags from assets.

        Args:
            labels: tags to process
            ids: internal_axon_id of assets to remove tags from
        """
        api_endpoint = ApiEndpoints.assets.tags_remove

        entities = {"ids": listify(ids), "include": True}
        request_obj = api_endpoint.load_request(entities=entities, labels=listify(labels))
        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=self.parent.ASSET_TYPE
        )
