# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import typing as t
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

    @classmethod
    def is_from_schedule(cls, value: t.Any = None) -> bool:
        """Check if value equals running."""
        return cls.scheduled.value_matches(value)


class StatusTask(BaseEnum):
    """Valid values for status of tasks."""

    running: str = "In Progress"
    success: str = "Completed Successfully"
    failure: str = "Completed with Errors"
    terminated: str = "Terminated"
    pending: str = "Pending"
    failed: str = "Failed"
    failed_partially: str = "Partially"

    @classmethod
    def error_states(cls) -> t.List["StatusTask"]:
        """Get all states that equate to failure."""
        return [cls.failure, cls.failed, cls.failed_partially]

    @classmethod
    def success_states(cls) -> t.List["StatusTask"]:
        """Get all states that equate to success."""
        return [cls.success]

    @classmethod
    def terminated_states(cls) -> t.List["StatusTask"]:
        """Get all states that equal terminated."""
        return [cls.terminated]

    @classmethod
    def pending_states(cls) -> t.List["StatusTask"]:
        """Get all states that equal pending."""
        return [cls.pending]

    @classmethod
    def is_pending(cls, value: t.Any = None) -> bool:
        """Check if value equals pending."""
        return any(x.value_matches(value) for x in cls.pending_states())

    @classmethod
    def is_terminated(cls, value: t.Any = None) -> bool:
        """Check if value equals terminated."""
        return any(x.value_matches(value) for x in cls.terminated_states())

    @classmethod
    def is_error(cls, value: t.Any = None) -> t.Optional[bool]:
        """Check if value equals error."""
        return any(x.value_matches(value) for x in cls.error_states())

    @classmethod
    def is_success(cls, value: t.Any = None) -> bool:
        """Check if value equals success."""
        return any(x.value_matches(value) for x in cls.success_states())


class StatusResult(BaseEnum):
    """Valid values for status of results for tasks."""

    success: str = "success"
    partial: str = "partial"
    running: str = "in progress"  # beautify task default is 'In Progress'
    failure: str = "failure"
    terminate: str = "terminate"
    pending: str = "pending"
    invalid: str = "invalid"  # not in cortex enum, beautify task exc is 'Invalid'

    @classmethod
    def success_states(cls) -> t.List["StatusResult"]:
        """Get all states that equate to success."""
        return [cls.success]

    @classmethod
    def error_states(cls) -> t.List["StatusResult"]:
        """Get all states that equate to failure."""
        return [cls.failure, cls.partial, cls.invalid]

    @classmethod
    def terminated_states(cls) -> t.List["StatusResult"]:
        """Get all states that equal terminated."""
        return [cls.terminate]

    @classmethod
    def pending_states(cls) -> t.List["StatusResult"]:
        """Get all states that equal pending."""
        return [cls.pending]

    @classmethod
    def is_success(cls, value: t.Any = None) -> bool:
        """Check if value equals success."""
        return any(x.value_matches(value) for x in cls.success_states())

    @classmethod
    def is_error(cls, value: t.Any = None) -> bool:
        """Check if value equals error."""
        return any(x.value_matches(value) for x in cls.error_states())

    @classmethod
    def is_terminated(cls, value: t.Any = None) -> bool:
        """Check if value equals terminated."""
        return any(x.value_matches(value) for x in cls.terminated_states())

    @classmethod
    def is_pending(cls, value: t.Any = None) -> bool:
        """Check if value equals pending."""
        return any(x.value_matches(value) for x in cls.pending_states())


class FlowTypes(BaseEnum):
    """Valid values for flow_type for results of tasks."""

    main: str = "main"
    success: str = "success"
    failure: str = "failure"
    post: str = "post"


class RunAgainst(BaseEnum):
    """Defines which entities the enforcement should run upon."""

    against_all: str = "AllEntities"
    against_new: str = "AddedEntities"

    @classmethod
    def is_against_new(cls, value: t.Any = None) -> bool:
        """Check if value equals against new."""
        return any(x.value_matches(value) for x in [cls.against_new])
