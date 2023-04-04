# -*- coding: utf-8 -*-
"""API for working with enforcements."""
import typing as t
from ..api_endpoints import ApiEndpoint, ApiEndpoints
from ..json_api.paging_state import PagingState
from ..json_api.tasks import GetTasks, Task, TaskBasic, TaskFull, TaskTypes
from ..mixins import ModelMixins

# from cachetools import TTLCache, cached


class Tasks(ModelMixins):
    """API working with tasks for enforcements."""

    # XXX need get enums

    def get(
        self, generator: bool = False, **kwargs
    ) -> t.Union[t.List[TaskTypes], t.Generator[TaskTypes, None, None]]:
        """Get all tasks for all enforcements."""
        gen: t.Generator[TaskTypes, None, None] = self.get_generator(**kwargs)
        return gen if generator else list(gen)

    def get_generator(
        self,
        page_sleep: int = PagingState.page_sleep,
        page_size: int = PagingState.page_size,
        row_start: int = PagingState.row_start,
        row_stop: t.Optional[int] = PagingState.row_stop,
        log_level: t.Union[int, str] = PagingState.log_level,
        request_obj: t.Optional[GetTasks] = None,
        as_full: bool = False,
        as_task: bool = True,
        **kwargs,
    ) -> t.Generator[TaskTypes, None, None]:
        """Get all tasks for all enforcements in multiple model formats."""
        request_obj: GetTasks = GetTasks.get_request_if_not_request(
            request_obj=request_obj, **kwargs
        )
        for basic in self.direct_get_generator(
            page_sleep=page_sleep,
            page_size=page_size,
            row_start=row_start,
            row_stop=row_stop,
            log_level=log_level,
            request_obj=request_obj,
            **kwargs,
        ):
            if as_full or as_task:
                full: TaskFull = basic.get_full()
                if as_task:
                    yield Task.load(basic=basic, full=full, http=self.auth.http)
                else:
                    yield full
            else:
                yield basic

    def direct_get_generator(
        self,
        page_sleep: int = PagingState.page_sleep,
        page_size: int = PagingState.page_size,
        row_start: int = PagingState.row_start,
        row_stop: t.Optional[int] = PagingState.row_stop,
        log_level: t.Union[int, str] = PagingState.log_level,
        request_obj: t.Optional[GetTasks] = None,
        **kwargs,
    ) -> t.Generator[TaskBasic, None, None]:
        """Direct API layer to get all tasks for all enforcements in basic model."""
        request_obj: GetTasks = GetTasks.get_request_if_not_request(
            request_obj=request_obj, **kwargs
        )
        with PagingState(
            purpose="Get all Tasks for all Enforcement Sets in basic model",
            page_sleep=page_sleep,
            page_size=page_size,
            row_start=row_start,
            row_stop=row_stop,
            log_level=log_level,
        ) as state:
            while not state.stop_paging:
                page = state.page(method=self.direct_get, request_obj=request_obj)
                yield from page.rows

    def direct_get(self, request_obj: t.Optional[GetTasks] = None, **kwargs) -> t.List[TaskBasic]:
        """Direct API layer to get all tasks for enforcements in basic model."""
        api_endpoint: ApiEndpoint = ApiEndpoints.enforcements.tasks.get_basic
        request_obj: GetTasks = GetTasks.get_request_if_not_request(
            request_obj=request_obj, **kwargs
        )
        response: t.List[TaskBasic] = api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj
        )
        return response

    def direct_get_full(self, uuid: str) -> TaskFull:
        """Direct API layer to get a single task for an enforcement in full model."""
        api_endpoint: ApiEndpoint = ApiEndpoints.enforcements.tasks.get_full
        response: TaskFull = api_endpoint.perform_request(
            http=self.auth.http,
            uuid=uuid,
        )
        return response
