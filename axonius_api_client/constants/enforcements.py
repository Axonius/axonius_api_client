# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
from ..data import BaseEnum


class RunCondition(BaseEnum):
    """Valid values for conditions applied when task was run."""

    manual: str = "Manual run"
    custom_selection: str = "Custom selection"
    every_discovery: str = "Any results"
    new_entities: str = "New entities were added"
    previous_entities: str = "Previous entities were removed"
    above: str = "The number of entities is above {}"
    below: str = "The number of entities is below {}"
    test_run: str = "Test run"


class RunMethod(BaseEnum):
    """Valid values for methods of a task being run."""

    scheduled: str = "Scheduled"
    manual: str = "Manual Run"
    manual_test: str = "Manual Test Run"


class StatusTask(BaseEnum):
    """Valid values for status of tasks."""

    running: str = "In Progress"
    success: str = "Completed Successfully"
    failure: str = "Completed with Errors"
    terminated: str = "Terminated"
    pending: str = "Pending"
    failed: str = "Failed"
    partially: str = "Partially"


class StatusResult(BaseEnum):
    """Valid values for status of results for tasks."""

    success: str = "success"
    partial: str = "partial"
    running: str = "in progress"  # beautify task default is 'In Progress'
    failure: str = "failure"
    terminate: str = "terminate"
    pending: str = "pending"
    invalid: str = "invalid"  # not in cortex enum, beautify task exc is 'Invalid'


class Workflow(BaseEnum):
    """Valid values for result_type for results of tasks."""

    main: str = "main"
    success: str = "success"
    failure: str = "failure"
    post: str = "post"
