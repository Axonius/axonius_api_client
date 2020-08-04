# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from typing import List

from ...tools import grouper
from ..mixins import ChildMixins


class Labels(ChildMixins):
    """ChildMixins API model for working with labels/tags for the parent asset type."""

    def add(self, rows: List[dict], labels: List[str]) -> int:
        """Add labels/tags to assets.

        Args:
            rows (:obj:`list` of :obj:`dict`): assets returned from :meth:`get`
                to process
            labels (:obj:`list` of `str`): labels to process

        Returns:
            :obj:`int`: number of labels processed
        """
        ids = [row["internal_axon_id"] for row in rows]

        processed = 0

        # only do 100 labels at a time, more seems to break API
        for group in grouper(ids, 100):
            group = [x for x in group if x is not None]
            response = self._add(labels=labels, ids=group)
            processed += response

        return processed

    def get(self) -> List[str]:
        """Get all known labels/tags.

        Returns:
            :obj:`list` of :obj:`str`: all labels that exist in Axonius
        """
        return self._get()

    def remove(self, rows: List[dict], labels: List[str]) -> int:
        """Remove labels/tags from assets.

        Args:
            rows (:obj:`list` of :obj:`dict`): assets returned from :meth:`get`
                to process
            labels (:obj:`list` of `str`): labels to process

        Returns:
            :obj:`int`: number of labels processed
        """
        ids = [row["internal_axon_id"] for row in rows]

        processed = 0

        # only do 100 labels at a time, more seems to break API
        for group in grouper(ids, 100):
            group = [x for x in group if x is not None]
            response = self._remove(labels=labels, ids=group)
            processed += response

        return processed

    def _add(self, labels: List[str], ids: List[str]) -> int:
        """Direct API method to add labels/tags to assets.

        Args:
            labels (:obj:`list` of `str`): labels to process
            ids (:obj:`list` of `str`): internal_axon_id of assets to add **labels** to

        Returns:
            :obj:`int`: number of labels processed
        """
        data = {}
        data["entities"] = {}
        data["entities"]["ids"] = ids
        data["labels"] = labels

        path = self.router.labels
        return self.request(method="post", path=path, json=data)

    def _get(self) -> List[str]:
        """Direct API method to get all known labels/tags.

        Returns:
            :obj:`list` of :obj:`str`: all labels that exist in Axonius
        """
        path = self.router.labels
        return self.request(method="get", path=path)

    def _remove(self, labels: List[str], ids: List[str]) -> int:
        """Direct API method to remove labels/tags from assets.

        Args:
            labels (:obj:`list` of `str`): labels to process
            ids (:obj:`list` of `str`): internal_axon_id of assets to remove
                **labels** from

        Returns:
            :obj:`int`: number of labels processed
        """
        data = {}
        data["entities"] = {}
        data["entities"]["ids"] = ids
        data["labels"] = labels

        path = self.router.labels

        return self.request(method="delete", path=path, json=data)
