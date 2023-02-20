# -*- coding: utf-8 -*-
"""API for working with enforcements."""
import typing as t

import cachetools

from ..api_endpoints import ApiEndpoint, ApiEndpoints
from ..json_api.folders import CreateFolder, CreateFolderResponse, DeleteFolderResponse, RootFolders

# from ..json_api.generic import Metadata
from ..json_api.paging_state import LOG_LEVEL_API, PAGE_SIZE, PagingState
from ..json_api.saved_queries import SavedQuery, SavedQueryGet
from ..mixins import ModelMixins

CACHE_QUERY_GET: cachetools.TTLCache = cachetools.TTLCache(maxsize=1024, ttl=60)


class Folders(ModelMixins):
    """Pass."""

    def get(self) -> RootFolders:
        """Pass."""
        data: RootFolders = self._get()
        return data

    def get_queries(
        self, generator: bool = False, **kwargs
    ) -> t.Union[t.List[SavedQuery], t.Generator[SavedQuery, None, None]]:
        """Get all saved queries."""
        gen: t.Generator[SavedQuery, None, None] = self.get_queries_generator(**kwargs)
        return gen if generator else list(gen)

    @cachetools.cached(cache=CACHE_QUERY_GET)
    def get_queries_cached(self, **kwargs) -> t.List[SavedQuery]:
        """Get all saved queries."""
        return list(self.get_queries_generator(**kwargs))

    def get_queries_generator(
        self,
        folder_id: str = "all",
        include_usage: bool = False,
        include_view: bool = False,
        page_sleep: int = 0,
        page_size: int = PAGE_SIZE,
        row_start: int = 0,
        row_stop: t.Optional[int] = None,
        log_level: t.Union[int, str] = LOG_LEVEL_API,
        query: t.Optional[str] = None,
        request_obj: t.Optional[SavedQueryGet] = None,
    ) -> t.Generator[SavedQuery, None, None]:
        """Get Saved Queries using a generator."""
        if not isinstance(request_obj, SavedQueryGet):
            request_obj = SavedQueryGet(
                filter=query,
                get_view_data=include_view,
                include_usage=include_usage,
                folder_id=folder_id,
            )

        purpose = f"Get Saved Queries using query: {query}"
        with PagingState(
            purpose=purpose,
            page_sleep=page_sleep,
            page_size=page_size,
            row_start=row_start,
            row_stop=row_stop,
            log_level=log_level,
        ) as state:
            while not state.stop_paging:
                page = state.page(method=self._get_query_model, request_obj=request_obj)
                yield from page.rows

    def _get_query_model(self, request_obj: SavedQueryGet) -> t.List[SavedQuery]:
        """Direct API method to get all saved queries."""
        api_endpoint = ApiEndpoints.saved_queries.get
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _get(self) -> RootFolders:
        """Direct API method to get all folders.

        Returns:
            RootFolders: API response model
        """
        api_endpoint: ApiEndpoint = ApiEndpoints.folders.get
        response: RootFolders = api_endpoint.perform_request(http=self.auth.http)
        return response

    def _create(self, name: str, parent_id: str) -> CreateFolderResponse:
        """Pass."""
        api_endpoint: ApiEndpoint = ApiEndpoints.folders.create
        request_obj: CreateFolder = api_endpoint.load_request(name=name, parent_id=parent_id)
        response: CreateFolderResponse = api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj
        )
        return response

    def _delete(self, id: str) -> DeleteFolderResponse:
        """Pass."""
        api_endpoint: ApiEndpoint = ApiEndpoints.folders.delete
        response: DeleteFolderResponse = api_endpoint.perform_request(http=self.auth.http, id=id)
        return response
