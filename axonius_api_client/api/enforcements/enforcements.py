# -*- coding: utf-8 -*-
"""API models for working with Enforcement Center."""
from ...tools import listify
from ..mixins import ModelMixins, PagingMixinsObject
from ..routers import API_VERSION


class Enforcements(ModelMixins, PagingMixinsObject):
    """API model for working with enforcement center.

    Notes:
        The REST API will need to be updated to allow more power in this library.
        Until then, this class should be considered **BETA**.
    """

    def delete(self, rows):
        """Delete an enforcement by name."""
        return self._delete(ids=[x["uuid"] for x in listify(obj=rows, dictkeys=False)])

    @property
    def router(self):
        """Router for this API model.

        Returns:
            :obj:`.routers.Router`: REST API route defs
        """
        return API_VERSION.alerts

    def _delete(self, ids):
        """Delete objects by internal axonius IDs.

        Args:
            ids (:obj:`list` of :obj:`str`): internal_axon_ids of devices to process
        """
        path = self.router.root

        return self.request(method="delete", path=path, json=ids)

    def _create(self, name, main, success=None, failure=None, post=None, triggers=None):
        """Create an enforcement set.

        Args:
            name (:obj:`str`): name of enforcement to create
            main (:obj:`dict`): main action
            success (:obj:`list` of :obj:`dict`, optional): success actions
            failure (:obj:`list` of :obj:`dict`, optional): failure actions
            post (:obj:`list` of :obj:`dict`, optional): post actions
            triggers (:obj:`list` of :obj:`dict`, optional): saved query trigger

        Notes:
            This will get a public create method once the REST API server has been
            updated to expose /enforcements/actions, /api/enforcements/actions/saved,
            and others.

        Returns:
            :obj:`str`: ID of created enforcement set.
        """
        data = {}
        data["name"] = name
        data["actions"] = {}
        data["actions"]["main"] = main
        data["actions"]["success"] = success or []
        data["actions"]["failure"] = failure or []
        data["actions"]["post"] = post or []
        data["triggers"] = triggers or []

        path = self.router.root
        return self.request(method="put", path=path, json=data, is_json=False)

    def _get(self, query=None, row_start=0, page_size=0):
        """Get a page for a given query."""
        params = {}
        params["skip"] = row_start
        params["limit"] = page_size
        params["filter"] = query

        path = self.router.root

        return self.request(method="get", path=path, params=params)
