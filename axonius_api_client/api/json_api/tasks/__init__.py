# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import typing as t

from .get_tasks import GetTasks, GetTasksSchema
from .result import Result
from .task import Task
from .task_basic import TaskBasic, TaskBasicSchema
from .task_filters import TaskFilters, TaskFiltersSchema
from .task_full import TaskFull, TaskFullSchema

TASK_TYPES: tuple = (TaskBasic, TaskFull, Task)
# noinspection PyTypeHints
TaskTypes = t.TypeVar("TaskTypes", *TASK_TYPES)

__all__ = (
    "Result",
    "TASK_TYPES",
    "TaskTypes",
    "Task",
    "TaskBasic",
    "TaskBasicSchema",
    "TaskFull",
    "TaskFullSchema",
    "GetTasksSchema",
    "GetTasks",
    "TaskFiltersSchema",
    "TaskFilters",
)
