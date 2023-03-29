# -*- coding: utf-8 -*-
"""API for working with enforcements."""
import typing as t

# from ...constants.api import MAX_PAGE_SIZE
# from ...exceptions import AlreadyExists, ApiError, ApiWarning, NotAllowedError, NotFoundError
# from ...tools import listify
# from .. import json_api
from ..api_endpoints import ApiEndpoint, ApiEndpoints
from ..json_api.paging_state import PagingState
from ..json_api.tasks import GetTasks, Task, TaskBasic, TaskFull
from ..mixins import ModelMixins

# from cachetools import TTLCache, cached


class Tasks(ModelMixins):
    """API working with tasks for enforcements."""

    def _get_full(self, uuid: str) -> TaskFull:
        """Get a single task for an enforcement in full model."""
        api_endpoint: ApiEndpoint = ApiEndpoints.enforcements.tasks.get_full
        response: TaskFull = api_endpoint.perform_request(
            http=self.auth.http,
            uuid=uuid,
        )
        return response

    def _get_ensure(self, request_obj: t.Optional[GetTasks] = None, **kwargs) -> GetTasks:
        """Check that request_obj is the appropriate type."""
        if not isinstance(request_obj, GetTasks):
            request_obj = GetTasks(**kwargs)
        return request_obj

    # XXX need get enums
    def get_basic_generator(
        self,
        page_sleep: int = PagingState.page_sleep,
        page_size: int = PagingState.page_size,
        row_start: int = PagingState.row_start,
        row_stop: t.Optional[int] = PagingState.row_stop,
        log_level: t.Union[int, str] = PagingState.log_level,
        request_obj: t.Optional[GetTasks] = None,
        as_task: bool = True,
        **kwargs,
    ) -> t.Generator[Task, None, None]:
        """Get all Tasks for all Enforcement Sets in basic model."""
        request_obj: GetTasks = self._get_ensure(request_obj=request_obj, **kwargs)
        for row in self._get_basic_generator(
            page_sleep=page_sleep,
            page_size=page_size,
            row_start=row_start,
            row_stop=row_stop,
            log_level=log_level,
        ):
            yield Task.load(basic=row) if as_task else row

    def _get_basic_generator(
        self,
        page_sleep: int = PagingState.page_sleep,
        page_size: int = PagingState.page_size,
        row_start: int = PagingState.row_start,
        row_stop: t.Optional[int] = PagingState.row_stop,
        log_level: t.Union[int, str] = PagingState.log_level,
        request_obj: t.Optional[GetTasks] = None,
        **kwargs,
    ) -> t.Generator[TaskBasic, None, None]:
        """Get all Tasks for all Enforcement Sets in basic model."""
        request_obj: GetTasks = self._get_ensure(request_obj=request_obj, **kwargs)
        with PagingState(
            purpose="Get all Tasks for all Enforcement Sets in basic model",
            page_sleep=page_sleep,
            page_size=page_size,
            row_start=row_start,
            row_stop=row_stop,
            log_level=log_level,
        ) as state:
            while not state.stop_paging:
                page = state.page(method=self._get_basic, request_obj=request_obj)
                yield from page.rows

    def _get_basic(self, request_obj: t.Optional[GetTasks] = None, **kwargs) -> t.List[TaskBasic]:
        """Get all tasks for enforcements in basic model."""
        api_endpoint: ApiEndpoint = ApiEndpoints.enforcements.tasks.get_basic
        request_obj: GetTasks = self._get_ensure(request_obj=request_obj, **kwargs)
        response: t.List[TaskBasic] = api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj
        )
        return response
