# -*- coding: utf-8 -*-
"""API for working with enforcements."""
import typing as t

from ..api_endpoints import ApiEndpoint, ApiEndpoints
from ..json_api.count_operator import OperatorTypes
from ..json_api.generic import IntValue
from ..json_api.paging_state import Page, PagingState
from ..json_api.tasks import GetTasks, Task, TaskBasic, TaskFilters, TaskFull, TaskTypes
from ..json_api.tasks.get_tasks import TypeOperator
from ..mixins import ModelMixins
from ...constants.api import RE_PREFIX, TASK_SLOW_WARNING
from ...constants.ctypes import (
    PatternLike,
    TypeDelta,
    TypeFloat,
    TypeInt,
    TypeMatch,
    TypeDate,
    TypeBool,
)
from ...constants.general import SPLITTER
from ...tools import echo_debug, json_dump


class Tasks(ModelMixins):
    """API working with tasks for enforcements."""

    def count(self, request_obj: t.Optional[GetTasks] = None, **kwargs) -> int:
        """Get the number of tasks that match the provided filters in request_obj

        Args:
            request_obj: request object to use
            **kwargs: passed to build a new request object if one is not provided
        """
        request_obj: GetTasks = self.build_get_request(request_obj=request_obj, **kwargs)
        return self.direct_count(request_obj=request_obj).value

    def get_filters(self) -> TaskFilters:
        """Get all filters (enums) for all enforcements."""
        api_endpoint: ApiEndpoint = ApiEndpoints.enforcements.tasks.get_filters
        response: TaskFilters = api_endpoint.perform_request(http=self.auth.http)
        return response

    def get(
        self, generator: bool = False, **kwargs
    ) -> t.Union[t.List[TaskTypes], t.Generator[TaskTypes, None, None]]:
        """Get all tasks for all enforcements.

        Args:
            generator: return a generator of Tasks, else return a list of Tasks
            **kwargs: passed to :meth:`get_generator`
        """
        gen: t.Generator[TaskTypes, None, None] = self.get_generator(**kwargs)
        return gen if generator else list(gen)

    def build_get_request(
        self,
        date_from: t.Optional[TypeDate] = None,
        date_from_add: t.Optional[TypeDelta] = None,
        date_from_subtract: t.Optional[TypeDelta] = None,
        date_to: t.Optional[TypeDate] = None,
        date_to_add: t.Optional[TypeDelta] = None,
        date_to_subtract: t.Optional[TypeDelta] = None,
        duration_seconds: t.Optional[TypeFloat] = None,
        duration_operator: TypeOperator = OperatorTypes.less,
        task_id: t.Optional[TypeInt] = None,
        re_prefix: str = RE_PREFIX,
        split: bool = True,
        split_max: t.Optional[int] = None,
        split_sep: t.Optional[PatternLike] = SPLITTER,
        strip: bool = True,
        strip_chars: t.Optional[str] = None,
        action_types: t.Optional[TypeMatch] = None,
        action_types_error: bool = True,
        action_types_minimum: t.Optional[int] = None,
        discovery_uuids: t.Optional[TypeMatch] = None,
        discovery_uuids_error: bool = True,
        discovery_uuids_minimum: t.Optional[int] = None,
        enforcement_names: t.Optional[TypeMatch] = None,
        enforcement_names_error: bool = True,
        enforcement_names_minimum: t.Optional[int] = None,
        statuses: t.Optional[TypeMatch] = None,
        statuses_error: bool = True,
        statuses_minimum: t.Optional[int] = None,
        statuses_result: t.Optional[TypeMatch] = None,
        statuses_result_error: bool = True,
        statuses_result_minimum: t.Optional[int] = None,
        is_refresh: t.Optional[TypeBool] = None,
        search: t.Optional[str] = None,
        query: t.Optional[str] = None,
        sort: t.Optional[str] = None,
        history: t.Optional[TypeDate] = None,
        task_filters: t.Optional[TaskFilters] = None,
        request_obj: t.Optional[GetTasks] = None,
    ):
        """Build the request for getting tasks for all enforcements.

        Args:
            date_from: Only get tasks with creation date >= this date
            date_from_add: seconds to add to date_from or now if not provided
            date_from_subtract: seconds to subtract from date_from or now if not provided
            date_to: Only get tasks with creation date <= this date
            date_to_add: seconds to add to date_to or now if not provided
            date_to_subtract: seconds to subtract from date_to or now if not provided
            duration_seconds: Only get tasks where run time evaluates True against duration_operator
            duration_operator: evaluate run time against duration_seconds (less, greater, equal)
            task_id: Only return tasks related to the provided task ID
            split: Split strings provided to filters by split_sep
            split_max: Max number of splits to perform on strings provided to action_type,
            re_prefix: if any values provided start with this, treat them as regex patterns
            split: split values on split_sep
            split_max: if value > 0 and split=True, only split on split_sep N times
            split_sep: if split=True, split values on this pattern or string
            strip: strip values of strip_chars
            strip_chars: if strip=True, strip values of these characters from each string
            action_types: Only get tasks that were ran by types of actions (use re_prefix for regex)
            action_types_error: Error if any action_types provided are not valid matches
            action_types_minimum: Error if matches for action_types are < this number
            discovery_uuids: Only get tasks that were ran by discovery UUIDs (use re_prefix for
                regex)
            discovery_uuids_error: Error if any discovery_uuids provided are not valid matches
            discovery_uuids_minimum: Error if matches for discovery_uuids are < this number
            enforcement_names: Only get tasks that were ran by  enforcement names (use re_prefix
                for regex)
            enforcement_names_error: Error if any enforcement_names provided are not valid matches
            enforcement_names_minimum: Error if matches for enforcement_names are < this number
            statuses: Only get tasks that have the provided statuses (use re_prefix for regex)
            statuses_error: Error if any statuses provided are not valid matches
            statuses_minimum: Error if matches for statuses are < this number
            statuses_result: Only get tasks that have the provided result statuses (use re_prefix
                for regex)
            statuses_result_error: Error if any result statuses provided are not valid matches
            statuses_result_minimum: Error if matches for result statuses are < this number
            is_refresh: logging control, unknown use
            search: A textual value to search for (unknown use for this endpoint)
            query: AQL string data filter (other request attributes build this for you)
            sort: Field name to sort by with direction prefixed (e.g. '-name' or 'name')
            history: get tasks from a history date snapshot (unknown use for this endpoint)
            task_filters: TaskFilters object to build query from
            request_obj: previously built GetTasks object to use instead of building a new one
        """
        if not isinstance(request_obj, GetTasks):
            request_obj = GetTasks()
            request_obj.HTTP = self.auth.http

            # --> generic request params for objects
            # unknown if used for this endpoint
            request_obj.search = search

            # not needed, specific params build this for you
            request_obj.filter = query

            # sort field
            request_obj.sort = sort

            # unknown if used for this endpoint
            request_obj.set_history(value=history)

            # --> endpoint specific request params
            # start date
            request_obj.set_date_from(
                value=date_from, add=date_from_add, subtract=date_from_subtract
            )

            # end date
            request_obj.set_date_to(value=date_to, add=date_to_add, subtract=date_to_subtract)

            # logging control, unknown use
            request_obj.set_is_refresh(value=is_refresh)

            # duration, complex object (for no particular reason) in REST API
            request_obj.set_duration(operator=duration_operator, seconds=duration_seconds)

            if not isinstance(task_filters, TaskFilters):
                task_filters = self.get_filters()

            filter_args = dict(
                re_prefix=re_prefix,
                split=split,
                split_max=split_max,
                split_sep=split_sep,
                strip=strip,
                strip_chars=strip_chars,
                task_filters=task_filters,
            )

            # filter by specific task "pretty" ID (singular, can not supply multiple task IDs)
            request_obj.set_task_id(value=task_id, task_filters=task_filters)

            # filter by task status
            request_obj.set_statuses(
                values=statuses, error=statuses_error, minimum=statuses_minimum, **filter_args
            )

            # filter by task result status
            request_obj.set_statuses_result(
                values=statuses_result,
                error=statuses_result_error,
                minimum=statuses_result_minimum,
                **filter_args,
            )

            # filter by action type
            request_obj.set_action_types(
                values=action_types,
                error=action_types_error,
                minimum=action_types_minimum,
                **filter_args,
            )

            # filter by enforcement name
            request_obj.set_enforcement_names(
                values=enforcement_names,
                error=enforcement_names_error,
                minimum=enforcement_names_minimum,
                **filter_args,
            )

            # filter by discovery UUID
            request_obj.set_discovery_uuids(
                values=discovery_uuids,
                error=discovery_uuids_error,
                minimum=discovery_uuids_minimum,
                **filter_args,
            )
        request_obj.HTTP = self.auth.http
        return request_obj

    def get_generator(
        self,
        as_full: bool = False,
        as_basic: bool = False,
        page_sleep: int = PagingState.page_sleep,
        page_size: int = PagingState.page_size,
        row_start: int = PagingState.row_start,
        row_stop: t.Optional[int] = PagingState.row_stop,
        log_level: t.Union[int, str] = PagingState.log_level,
        request_obj: t.Optional[GetTasks] = None,
        echo: bool = True,
        **kwargs,
    ) -> t.Generator[TaskTypes, None, None]:
        """Get all tasks for all enforcements in multiple model formats.

        Args:
            as_full: return TaskFull (complicated model from the REST API)
            as_basic: return TaskBasic (complicated model from the REST API)
            page_sleep: seconds to sleep between pages
            page_size: number of rows to get per page
            row_start: row to start on
            row_stop: row to stop on
            log_level: log level to use
            request_obj: request object to use, will create using above args if not provided
            echo: echo debug output
            **kwargs: passed to :meth:`build_get_request`
        """
        request_obj: GetTasks = self.build_get_request(request_obj=request_obj, **kwargs)
        for basic in self.direct_get_generator(
            page_sleep=page_sleep,
            page_size=page_size,
            row_start=row_start,
            row_stop=row_stop,
            log_level=log_level,
            echo=echo,
            request_obj=request_obj,
            slow_warning=not as_basic,
        ):
            if as_basic:
                yield basic
            else:
                # only get the full model if we need it
                # this is because we can only get one full model at a time
                # which can take quite a long time if there are many tasks
                # this could be async but that's a problem for future me
                full: TaskFull = basic.get_full()
                if as_full:
                    yield full
                else:
                    yield Task.load(basic=basic, full=full, http=self.auth.http)

    def direct_get_generator(
        self,
        page_sleep: int = PagingState.page_sleep,
        page_size: int = PagingState.page_size,
        row_start: int = PagingState.row_start,
        row_stop: t.Optional[int] = PagingState.row_stop,
        log_level: t.Union[int, str] = PagingState.log_level,
        request_obj: t.Optional[GetTasks] = None,
        echo: bool = True,
        slow_warning: bool = False,
        **kwargs,
    ) -> t.Generator[TaskBasic, None, None]:
        """Direct API method to get all tasks for all enforcements in basic model.

        Args:
            page_sleep: seconds to sleep between pages
            page_size: number of rows to get per page
            row_start: row to start on
            row_stop: row to stop on
            log_level: log level to use
            request_obj: request object to use
            echo: echo to console
            slow_warning: echo a warning that the page fetch is quick,
                but the full model fetch is slow
            **kwargs: passed to build a new request object if one is not provided
        """
        request_obj: GetTasks = self.build_get_request(request_obj=request_obj, **kwargs)
        count: int = self.count(request_obj=request_obj)

        purpose = [
            f"Getting {count} tasks in 'basic model' format using request:",
            f"{json_dump(request_obj)}",
        ]
        if slow_warning:
            purpose += [TASK_SLOW_WARNING]

        purpose = "\n".join(purpose)
        echo_debug(purpose, do_echo=echo)
        with PagingState(
            purpose=purpose,
            page_sleep=page_sleep,
            page_size=page_size,
            row_start=row_start,
            row_stop=row_stop,
            log_level=log_level,
        ) as state:
            while not state.stop_paging:
                page: Page = state.page(method=self.direct_get, request_obj=request_obj)
                echo_debug(f"Received basic model {page}")
                yield from page.rows

    def direct_count(self, request_obj: t.Optional[GetTasks] = None, **kwargs) -> IntValue:
        """Direct API method to get the number of tasks for enforcements.

        Args:
            request_obj: request object to use
            **kwargs: passed to build a new request object if one is not provided
        """
        api_endpoint: ApiEndpoint = ApiEndpoints.enforcements.tasks.count
        request_obj: GetTasks = self.build_get_request(request_obj=request_obj, **kwargs)
        response: IntValue = api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj
        )
        return response

    def direct_get(self, request_obj: t.Optional[GetTasks] = None, **kwargs) -> t.List[TaskBasic]:
        """Direct API method to get all tasks for enforcements in basic model.

        Args:
            request_obj: request object to use
            **kwargs: passed to build a new request object if one is not provided
        """
        api_endpoint: ApiEndpoint = ApiEndpoints.enforcements.tasks.get_basic
        request_obj: GetTasks = self.build_get_request(request_obj=request_obj, **kwargs)
        response: t.List[TaskBasic] = api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj
        )
        return response

    def get_full(self, uuid: str) -> TaskFull:
        """Direct API method to get a single task for an enforcement in full model.

        Args:
            uuid: uuid of the task to get
        """
        api_endpoint: ApiEndpoint = ApiEndpoints.enforcements.tasks.get_full
        response: TaskFull = api_endpoint.perform_request(
            http=self.auth.http,
            uuid=uuid,
        )
        return response
