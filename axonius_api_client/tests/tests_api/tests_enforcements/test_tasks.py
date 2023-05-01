"""Tests for the ``enforcements/tasks`` API endpoint."""

import pytest

from axonius_api_client.exceptions import NotFoundError, ToolsError
from .test_enforcements import EnforcementsBase
from axonius_api_client.api.json_api.tasks import Result, TaskFilters, Task, TaskFull, TaskBasic


@pytest.fixture()
def mock_task_filters():
    """Pass."""
    action_names = ["action_type", "other_action_type", "drop_down_type"]
    enum_action_types = ["action_type", "drop_down_type", "other_action_type"]

    discovery_cycle_id = ["discovery_uuid_1", "discovery_uuid_2"]
    enum_discovery_uuids = ["discovery_uuid_1", "discovery_uuid_2"]

    enforcement_name = [
        {"text": "enforcement_name_1", "value": "task_uuid_1"},
        {"text": "enforcement_name_1", "value": "task_uuid_2"},
        {"text": "enforcement_name_2", "value": "task_uuid_3"},
    ]
    enum_enforcement_names = ["enforcement_name_1", "enforcement_name_2"]

    run = [1, 2, 3]
    enum_task_ids = [1, 2, 3]

    statuses = ["success", "error"]
    enum_statuses = ["error", "success"]

    task_filters = TaskFilters(
        action_names=action_names,
        discovery_cycle_id=discovery_cycle_id,
        enforcement_name=enforcement_name,
        run=run,
        statuses=statuses,
    )
    assert str(task_filters)
    assert repr(task_filters)

    assert task_filters.enum_enforcement_names == enum_enforcement_names
    assert task_filters.enum_discovery_uuids == enum_discovery_uuids
    assert task_filters.enum_action_types == enum_action_types
    assert task_filters.enum_statuses == enum_statuses
    assert task_filters.enum_task_ids == enum_task_ids
    yield task_filters


class TasksBase(EnforcementsBase):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_enforcements):
        """Pass."""
        return api_enforcements.tasks


class TestTasks(TasksBase):
    """Tests for Tasks."""

    @pytest.fixture(scope="class")
    def test_get_as_task(self, apiobj):
        tasks = apiobj.get(row_stop=1)
        assert isinstance(tasks, list)
        for task in tasks:
            assert isinstance(task, Task)
            assert isinstance(task.action_types, list)
            assert isinstance(task.result_main, Result)
            assert isinstance(task.results_success, list)
            assert isinstance(task.results_failure, list)
            assert isinstance(task.results_post, list)
            assert isinstance(task.results, list)
            yield task

    def test_to_dict(self, test_get_as_task):
        """Pass."""
        task = test_get_as_task
        assert isinstance(task.to_dict(), dict)

    def test_to_dicts(self, test_get_as_task):
        """Pass."""
        task = test_get_as_task
        data = list(Task.to_dicts([task]))
        assert isinstance(data, list)
        assert len(data) == 1

    def test_to_dicts_schemas(self, test_get_as_task):
        """Pass."""
        task = test_get_as_task
        data = list(Task.to_dicts([task], schemas=True))
        assert isinstance(data, list)
        assert len(data) == 2
        schemas = data[0]["schemas"]
        assert isinstance(schemas, dict) and schemas

    def test_get_as_full(self, apiobj):
        tasks = apiobj.get(row_stop=1, as_full=True)
        assert isinstance(tasks, list)
        for task in tasks:
            assert isinstance(task, TaskFull)

    def test_get_as_basic(self, apiobj):
        tasks = apiobj.get(row_stop=1, as_basic=True)
        assert isinstance(tasks, list)
        for task in tasks:
            assert isinstance(task, TaskBasic)


class TestTasksFilters(TasksBase):
    """Tests for TaskFilters."""

    def test_get_filters(self, apiobj):
        filters = apiobj.get_filters()
        assert isinstance(filters, TaskFilters)


class TestTasksFiltersCheckTaskId:
    def test_valid(self, mock_task_filters):
        """Pass."""
        expected = 1
        value = "1"
        data = mock_task_filters.check_task_id(value)
        assert data == expected

    def test_invalid(self, mock_task_filters):
        """Pass."""
        with pytest.raises(ToolsError) as exc:
            mock_task_filters.check_task_id(4)
        assert mock_task_filters.TASK_IDS in str(exc.value)


class TestTasksFiltersCheckActionTypes:
    def test_valid(self, mock_task_filters):
        """Pass."""
        expected = ["action_type"]
        value = "action_type"
        data = mock_task_filters.check_action_types(value)
        assert data == expected

    def test_pattern_valid(self, mock_task_filters):
        expected = ["action_type", "other_action_type"]
        value = "~a"
        data = mock_task_filters.check_action_types(value)
        assert data == expected

    def test_invalid_error_false(self, mock_task_filters):
        """Pass."""
        expected = []
        value = "invalid_action_type"
        data = mock_task_filters.check_action_types(value, error=False)
        assert data == expected

    def test_minimum_valid(self, mock_task_filters):
        """Pass."""
        expected = ["action_type"]
        value = "action_type"
        data = mock_task_filters.check_action_types(value, minimum=1)
        assert data == expected

    def test_minimum_invalid(self, mock_task_filters):
        """Pass."""
        value = ""
        with pytest.raises(NotFoundError) as exc:
            mock_task_filters.check_action_types(value, minimum=2)
        assert mock_task_filters.ACTION_TYPES in str(exc.value)

    def test_invalid(self, mock_task_filters):
        """Pass."""
        value = ["invalid_action_type"]
        with pytest.raises(NotFoundError) as exc:
            mock_task_filters.check_action_types(value)
        assert mock_task_filters.ACTION_TYPES in str(exc.value)


class TestTasksFiltersCheckDiscoveryUuids:
    def test_valid(self, mock_task_filters):
        """Pass."""
        expected = ["discovery_uuid_1"]
        value = "discovery_uuid_1"
        data = mock_task_filters.check_discovery_uuids(value)
        assert data == expected

    def test_pattern(self, mock_task_filters):
        expected = ["discovery_uuid_1", "discovery_uuid_2"]
        value = "~d"
        data = mock_task_filters.check_discovery_uuids(value)
        assert data == expected

    def test_minimum_valid(self, mock_task_filters):
        """Pass."""
        expected = ["discovery_uuid_1"]
        value = "discovery_uuid_1"
        data = mock_task_filters.check_discovery_uuids(value, minimum=1)
        assert data == expected

    def test_minimum_invalid(self, mock_task_filters):
        """Pass."""
        value = ""
        with pytest.raises(NotFoundError) as exc:
            mock_task_filters.check_discovery_uuids(value, minimum=2)
        assert mock_task_filters.DISCOVERY_UUIDS in str(exc.value)

    def test_invalid_error_false(self, mock_task_filters):
        """Pass."""
        expected = []
        value = "invalid_discovery_uuid"
        data = mock_task_filters.check_discovery_uuids(value, error=False)
        assert data == expected

    def test_invalid(self, mock_task_filters):
        """Pass."""
        value = ["invalid_discovery_uuid"]
        with pytest.raises(NotFoundError) as exc:
            mock_task_filters.check_discovery_uuids(value)
        assert mock_task_filters.DISCOVERY_UUIDS in str(exc.value)


class TestTasksFiltersCheckStatuses:
    def test_valid(self, mock_task_filters):
        """Pass."""
        expected = ["success"]
        value = "success"
        data = mock_task_filters.check_statuses(value)
        assert data == expected

    def test_pattern(self, mock_task_filters):
        expected = ["error", "success"]
        value = "~e"
        data = mock_task_filters.check_statuses(value)
        assert data == expected

    def test_minimum_valid(self, mock_task_filters):
        """Pass."""
        expected = ["success"]
        value = "success"
        data = mock_task_filters.check_statuses(value, minimum=1)
        assert data == expected

    def test_minimum_invalid(self, mock_task_filters):
        """Pass."""
        value = ""
        with pytest.raises(NotFoundError) as exc:
            mock_task_filters.check_statuses(value, minimum=2)
        assert mock_task_filters.STATUSES in str(exc.value)

    def test_invalid_error_false(self, mock_task_filters):
        """Pass."""
        expected = []
        value = "invalid_status"
        data = mock_task_filters.check_statuses(value, error=False)
        assert data == expected

    def test_invalid(self, mock_task_filters):
        """Pass."""
        value = ["invalid_status"]
        with pytest.raises(NotFoundError) as exc:
            mock_task_filters.check_statuses(value)
        assert mock_task_filters.STATUSES in str(exc.value)


class TestTasksFiltersCheckEnforcementNames:
    def test_valid(self, mock_task_filters):
        """Pass."""
        expected = ["task_uuid_1", "task_uuid_2"]
        value = "enforcement_name_1"
        data = mock_task_filters.check_enforcement_names(value)
        assert data == expected

    def test_pattern(self, mock_task_filters):
        """Pass."""
        expected = ["task_uuid_1", "task_uuid_2", "task_uuid_3"]
        value = "~e"
        data = mock_task_filters.check_enforcement_names(value)
        assert data == expected

    def test_as_names(self, mock_task_filters):
        expected = ["enforcement_name_1", "enforcement_name_2"]
        value = "~e"
        data = mock_task_filters.check_enforcement_names(value, as_names=True)
        assert data == expected

    def test_minimum_valid(self, mock_task_filters):
        """Pass."""
        expected = ["task_uuid_1", "task_uuid_2"]
        value = "enforcement_name_1"
        data = mock_task_filters.check_enforcement_names(value, minimum=1)
        assert data == expected

    def test_minimum_invalid(self, mock_task_filters):
        """Pass."""
        value = ""
        with pytest.raises(NotFoundError) as exc:
            mock_task_filters.check_enforcement_names(value, minimum=2)
        assert mock_task_filters.ENFORCEMENT_NAMES in str(exc.value)

    def test_invalid_error_false(self, mock_task_filters):
        """Pass."""
        expected = []
        value = "invalid_enforcement_name"
        data = mock_task_filters.check_enforcement_names(value, error=False)
        assert data == expected

    def test_invalid(self, mock_task_filters):
        """Pass."""
        value = ["invalid_enforcement_name"]
        with pytest.raises(NotFoundError) as exc:
            mock_task_filters.check_enforcement_names(value)
        assert mock_task_filters.ENFORCEMENT_NAMES in str(exc.value)
