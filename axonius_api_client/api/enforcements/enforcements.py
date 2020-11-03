# -*- coding: utf-8 -*-
"""API for working with enforcements."""
from typing import List, Optional

from ...tools import listify
from ..mixins import ModelMixins, PagingMixinsObject
from ..routers import API_VERSION, Router


class Enforcements(ModelMixins, PagingMixinsObject):  # pragma: no cover
    """API working with enforcements.

    Notes:
        Future versions of API client 4.x branch will be expanded quite a bit to make it user
        friendly. The current incarnation should be considered **BETA** until such time.
    """

    def delete(self, rows: List[dict]) -> str:  # pragma: no cover
        """Delete an enforcement by name."""
        return self._delete(ids=[x["uuid"] for x in listify(obj=rows, dictkeys=False)])

    @property
    def router(self) -> Router:
        """Router for this API model."""  # pragma: no cover
        return API_VERSION.alerts

    def _delete(self, ids: List[str]) -> str:  # pragma: no cover
        """Delete objects by internal axonius IDs."""
        path = self.router.root

        return self.request(method="delete", path=path, json=ids)

    def _create(
        self,
        name: str,
        main: dict,
        success: Optional[List[dict]] = None,
        failure: Optional[List[dict]] = None,
        post: Optional[List[dict]] = None,
        triggers: Optional[List[dict]] = None,
    ) -> str:  # pragma: no cover
        """Create an enforcement set.

        Args:
            name: name of enforcement to create
            main: main action
            success: success actions
            failure: failure actions
            post: post actions
            triggers: saved query trigger
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

    def _get(self, query: Optional[str] = None, row_start: int = 0, page_size: int = 0) -> dict:
        """Get a page of enforcements."""
        params = {}
        params["skip"] = row_start
        params["limit"] = page_size
        params["filter"] = query

        path = self.router.root

        return self.request(method="get", path=path, params=params)
