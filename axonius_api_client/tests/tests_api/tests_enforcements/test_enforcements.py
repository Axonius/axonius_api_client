# -*- coding: utf-8 -*-
"""Test suite."""
import pytest
from axonius_api_client.api.json_api.enforcements import (
    ActionCategory,
    ActionType,
    OnlyNewAssets,
    QueryType,
    Schedule,
    SetBasic,
    SetFull,
)
from axonius_api_client.exceptions import (
    ApiError,
    ApiWarning,
    ConfigRequired,
    ConfigUnknown,
    NotFoundError,
    NoTriggerDefinedError,
    ToolsError,
)


class Meta:
    name = "badwolf EC"
    name_cli = "Badwolf FROM CLI"
    name_copy = "yan badwolf EC"
    name_rename = "badwolf vittles"
    name_rename_cli = "badwolf vittles CLI"
    name_invalid = "i do not exist"
    name_create = "badwolf created"

    action_type = "create_notification"

    action_name = "badwolf action"
    action_name2 = "badwolf action 2"

    action_config = {}


class EnforcementsBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_enforcements):
        return api_enforcements

    @pytest.fixture(scope="class")
    def created_set(self, apiobj):
        try:
            created_set = apiobj.get_set(value=Meta.name)
        except NotFoundError:
            with pytest.warns(ApiWarning):
                created_set = apiobj.create(
                    name=Meta.name,
                    main_action_type=Meta.action_type,
                    main_action_name=Meta.action_name,
                    main_action_config=Meta.action_config,
                )

        assert isinstance(created_set, SetFull)

        yield created_set

        deleted = self.cleanup(apiobj=apiobj, value=created_set)
        assert isinstance(deleted, SetFull)

    def cleanup(self, apiobj, value):
        try:
            deleted = apiobj.delete(value=value)
        except NotFoundError:
            pass
        else:
            print(f"Deleted Enforcement Set:\n{deleted}")
            return deleted


class TestEnforcements(EnforcementsBase):
    def test_create_delete(self, apiobj):
        self.cleanup(apiobj=apiobj, value=Meta.name_create)
        with pytest.warns(ApiWarning):
            created_set = apiobj.create(
                name=Meta.name_create,
                main_action_type=Meta.action_type,
                main_action_name=Meta.action_name,
                main_action_config=Meta.action_config,
            )

        assert isinstance(created_set, SetFull)
        assert isinstance(created_set.BASIC, SetBasic)

        basic = created_set.get_basic(refresh=True)
        assert isinstance(basic, SetBasic)

        deleted = apiobj.delete(value=created_set)
        assert isinstance(deleted, SetFull)
        assert isinstance(deleted.BASIC, SetBasic)

        with pytest.raises(NotFoundError):
            deleted.get_basic(refresh=True)

    def test_attach_full_set_bad_type(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.attach_full_set({})

    def test_get_action_type_bad_type(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.get_action_type(value=4)

    def test_get_action_types(self, apiobj):
        value = apiobj.get_action_types()
        for x in value:
            assert isinstance(x, ActionType)

    def test_get_action_type(self, apiobj):
        action_type = apiobj.get_action_type(value=Meta.action_type)
        assert isinstance(action_type, ActionType)
        value = apiobj.get_action_type(value=action_type)
        assert value == action_type
        value = apiobj.get_action_type(value=action_type.to_dict())
        assert value == action_type

    def test_get_action_type_not_found(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get_action_type(value=Meta.name_invalid)

    def test_get_sets(self, created_set, apiobj):
        value = apiobj.get_sets()
        assert created_set.uuid in [x.uuid for x in value]

    def test_get_set(self, created_set, apiobj):
        value = apiobj.get_set(value=created_set)
        assert (value.name, value.uuid) == (created_set.name, created_set.uuid)
        value = apiobj.get_set(value=created_set.to_dict())
        assert (value.name, value.uuid) == (created_set.name, created_set.uuid)
        value = apiobj.get_set(value=created_set.uuid)
        assert (value.name, value.uuid) == (created_set.name, created_set.uuid)
        value = apiobj.get_set(value=created_set.name)
        assert (value.name, value.uuid) == (created_set.name, created_set.uuid)

    def test_get_set_action_get_required_conditionally_no_key(self, apiobj):
        atype = apiobj.get_action_type("add_custom_data")
        exp = ["field_name", "conditional", "field_value", "field_on", "field_list", "field_date"]
        value = atype.get_required_conditionally()
        assert value == exp

    def test_get_set_action_get_required_conditionally_with_key(self, apiobj):
        atype = apiobj.get_action_type("add_custom_data")
        exp = ["field_name", "conditional", "field_value"]
        value = atype.get_required_conditionally(config={"conditional": "field_value"})
        assert value == exp

    def test_get_set_action_no_schema(self, apiobj):
        atypes = apiobj.get_action_types()
        atype = [x for x in atypes if not x.schema][0]

        exp = {"name": "boobear", "action": {"action_name": atype.name, "config": {}}}

        with pytest.warns(ApiWarning):
            value = apiobj.get_set_action(action_type=atype, name="boobear")
        assert value == exp

    def test_get_set_action_invalid_type(self, apiobj):
        atypes = apiobj.get_action_types()
        atype = [x for x in atypes if x.schema][0]

        with pytest.raises(ApiError):
            apiobj.get_set_action(action_type=atype, name="boobear", config="1")

    def test_get_set_action_missing_required(self, apiobj):
        atypes = apiobj.get_action_types()
        atype = [x for x in atypes if x.schema][0]

        with pytest.raises(ConfigRequired):
            apiobj.get_set_action(action_type=atype, name="boobear", config={})

    def test_get_set_action_unknown(self, apiobj):
        atypes = apiobj.get_action_types()
        atype = [x for x in atypes if x.schema][0]

        with pytest.raises(ConfigUnknown):
            apiobj.get_set_action(action_type=atype, name="boobear", config={"k": "v"})

    def test_update_add_remove_action(self, created_set, apiobj):
        action_name = "yan badwolf"
        with pytest.warns(ApiWarning):
            added = apiobj.update_action_add(
                value=created_set,
                category=ActionCategory.failure,
                name=action_name,
                action_type=Meta.action_type,
                config=Meta.action_config,
            )
        assert isinstance(added, SetFull)
        assert action_name in " ".join(added.failure_actions_str)

        removed = apiobj.update_action_remove(
            value=added, category=ActionCategory.failure, name=action_name
        )
        assert action_name not in " ".join(removed.failure_actions_str)

    def test_update_conditions(self, created_set, apiobj):
        sq = apiobj.api_devices.saved_query.get(as_dataclass=True)[0]
        if not created_set.query_name:
            updated = apiobj.update_query(value=created_set, query_name=sq, query_type="devices")
            assert updated.query_name

        updated = apiobj.update_only_new_assets(value=created_set, update=True)
        assert updated.only_new_assets is True

        updated = apiobj.update_on_count_increased(value=created_set, update=True)
        assert updated.on_count_increased is True

        updated = apiobj.update_on_count_decreased(value=created_set, update=True)
        assert updated.on_count_decreased is True

        updated = apiobj.update_on_count_above(value=created_set, update=5)
        assert updated.on_count_above == 5

        updated = apiobj.update_on_count_above(value=created_set, update="None")
        assert updated.on_count_above is None

        updated = apiobj.update_on_count_above(value=created_set, update="5")
        assert updated.on_count_above == 5

        updated = apiobj.update_on_count_above(value=created_set, update=None)
        assert updated.on_count_above is None

        updated = apiobj.update_on_count_below(value=created_set, update=5)
        assert updated.on_count_below == 5

        updated = apiobj.update_on_count_below(value=created_set, update="None")
        assert updated.on_count_below is None

        updated = apiobj.update_on_count_below(value=created_set, update="5")
        assert updated.on_count_below == 5

        updated = apiobj.update_on_count_below(value=created_set, update=None)
        assert updated.on_count_below is None

    def test_update_schedule(self, created_set, apiobj):
        sq = apiobj.api_devices.saved_query.get(as_dataclass=True)[0]
        if created_set.query_name:
            updated = apiobj.update_query_remove(value=created_set)
            assert not updated._trigger_obj

        updated = apiobj.update_query(value=created_set, query_name=sq, query_type="devices")
        assert sq.name in str(updated)
        assert updated._trigger_obj

        updated = apiobj.update_schedule_never(value=updated)
        assert "never" in str(updated)

        updated = apiobj.update_schedule_discovery(value=updated)
        assert "discovery" in str(updated)

        updated = apiobj.update_schedule_hourly(value=updated, recurrence=2)
        assert "hourly" in str(updated)

        updated = apiobj.update_schedule_daily(value=updated, recurrence=2)
        assert "daily" in str(updated)

        updated = apiobj.update_schedule_weekly(value=updated, recurrence="2,5")
        assert "weekly" in str(updated)

        updated = apiobj.update_schedule_monthly(value=updated, recurrence="1,3,6,29")
        assert "monthly" in str(updated)

        updated = apiobj.update_query_remove(value=updated)
        assert not updated._trigger_obj

    def test_update_query(self, created_set, apiobj):
        sq = apiobj.api_devices.saved_query.get(as_dataclass=True)[0]
        if created_set.query_name:
            updated = apiobj.update_query_remove(value=created_set)
            assert not updated._trigger_obj

        updated = apiobj.update_query(value=created_set, query_name=sq, query_type="devices")
        assert sq.name in str(updated)
        assert updated._trigger_obj

        updated = apiobj.update_query_remove(value=updated)
        assert not updated._trigger_obj

    def test_update_no_trigger_failures(self, created_set, apiobj):
        if created_set.query_name:
            updated = apiobj.update_query_remove(value=created_set)
            assert not updated._trigger_obj

        with pytest.raises(NoTriggerDefinedError):
            apiobj.update_query_remove(value=created_set)

        with pytest.raises(NoTriggerDefinedError):
            apiobj.update_schedule_never(value=created_set)

        with pytest.raises(NoTriggerDefinedError):
            apiobj.update_schedule_discovery(value=created_set)

        with pytest.raises(NoTriggerDefinedError):
            apiobj.update_schedule_hourly(value=created_set, recurrence=1)

        with pytest.raises(NoTriggerDefinedError):
            apiobj.update_schedule_daily(value=created_set, recurrence=1)

        with pytest.raises(NoTriggerDefinedError):
            apiobj.update_schedule_weekly(value=created_set, recurrence="monday")

        with pytest.raises(NoTriggerDefinedError):
            apiobj.update_schedule_monthly(value=created_set, recurrence="1,2,29")

        with pytest.raises(NoTriggerDefinedError):
            apiobj.update_only_new_assets(value=created_set, update=True)

        with pytest.raises(NoTriggerDefinedError):
            apiobj.update_on_count_above(value=created_set, update=1)

        with pytest.raises(NoTriggerDefinedError):
            apiobj.update_on_count_below(value=created_set, update=1)

        with pytest.raises(NoTriggerDefinedError):
            apiobj.update_on_count_increased(value=created_set, update=True)

        with pytest.raises(NoTriggerDefinedError):
            apiobj.update_on_count_decreased(value=created_set, update=True)

    def test_copy_update_name_action(self, created_set, apiobj):
        copied = apiobj.copy(value=created_set, name=Meta.name_copy)
        assert copied.name == Meta.name_copy

        self.cleanup(apiobj=apiobj, value=Meta.name_rename)
        updated = apiobj.update_name(value=copied, name=Meta.name_rename)
        assert updated.name == Meta.name_rename

        with pytest.warns(ApiWarning):
            updated = apiobj.update_action_main(
                value=updated,
                name=Meta.action_name2,
                action_type=Meta.action_type,
                config=Meta.action_config,
            )
        assert Meta.action_name2 in str(updated)
        assert Meta.action_name2 in repr(updated)

        deleted = self.cleanup(apiobj=apiobj, value=updated)
        assert deleted.name == updated.name

    def test_model_query_remove_no_trigger(self, created_set, apiobj):
        with pytest.raises(NoTriggerDefinedError):
            created_set.query_remove()

    def test_model_set_sechedule_never_no_trigger(self, created_set, apiobj):
        with pytest.raises(NoTriggerDefinedError):
            created_set.set_schedule_never()


class TestOnlyNewAssets:
    def test_get_str_true(self):
        assert OnlyNewAssets.get_str(value=True) == str(OnlyNewAssets.added_entities)

    def test_get_str_false(self):
        assert OnlyNewAssets.get_str(value=False) == str(OnlyNewAssets.all_entities)

    def test_get_bool_none(self):
        assert OnlyNewAssets.get_bool(value=None) is None

    def test_get_bool_fail(self):
        with pytest.raises(ApiError):
            OnlyNewAssets.get_bool(value="x")

    def test_get_bool_true(self):
        assert OnlyNewAssets.get_bool(value=OnlyNewAssets.added_entities) is True
        assert OnlyNewAssets.get_bool(value=str(OnlyNewAssets.added_entities)) is True

    def test_get_bool_False(self):
        assert OnlyNewAssets.get_bool(value=OnlyNewAssets.all_entities) is False
        assert OnlyNewAssets.get_bool(value=str(OnlyNewAssets.all_entities)) is False


class TestQueryType:
    def test_get_value(self):
        assert QueryType.get_value("devices") == QueryType.devices

    def test_get_value_fail(self):
        with pytest.raises(ApiError):
            QueryType.get_value("x")


class TestSchedule:
    def test_get_value(self):
        for i in Schedule.keys():
            value = Schedule.get_value(i)
            assert value.name == i

        for i in Schedule.values():
            value = Schedule.get_value(i)
            assert value.value == i
            assert str(value) == i

    def test_get_value_fail(self):
        with pytest.raises(ApiError):
            Schedule.get_value("x")

    def test_get_time_default(self):
        value = Schedule.get_time()
        assert isinstance(value, str) and ":" in value

    def test_get_time(self):
        value = Schedule.get_time(hour=22, minute=2)
        assert value == "22:02"

    def test_get_time_hour_fail(self):
        with pytest.raises(ToolsError):
            Schedule.get_time(hour=24)

    def test_get_time_minute_fail(self):
        with pytest.raises(ToolsError):
            Schedule.get_time(minute=60)

    def test_get_conditions_default(self):
        value = Schedule.get_conditions()
        exp = {"new_entities": False, "previous_entities": False, "above": None, "below": None}
        assert value == exp

    def test_get_conditions(self):
        value = Schedule.get_conditions(
            on_count_above="100",
            on_count_below="5",
            on_count_increased=True,
            on_count_decreased=True,
        )
        exp = {"new_entities": True, "previous_entities": True, "above": 100, "below": 5}
        assert value == exp

    def test_get_conditions_fail(self):
        with pytest.raises(ToolsError):
            Schedule.get_conditions(on_count_above=-1)

        with pytest.raises(ToolsError):
            Schedule.get_conditions(on_count_below=-1)

        with pytest.raises(ToolsError):
            Schedule.get_conditions(on_count_increased="x")

        with pytest.raises(ToolsError):
            Schedule.get_conditions(on_count_decreased="x")

    def test_get_view_default(self):
        assert Schedule.get_view() is None

    def test_get_view_fail(self):
        with pytest.raises(ApiError):
            Schedule.get_view(query_type="x")

    def test_get_view(self):
        assert Schedule.get_view(query_uuid="xxx", query_type="users") == {
            "id": "xxx",
            "entity": "users",
        }

    def test_get_recurrence_never(self):
        sched = Schedule.never
        assert sched.get_recurrence() is None

    def test_get_recurrence_discovery(self):
        sched = Schedule.discovery
        assert sched.get_recurrence() is None

    def test_get_recurrence_hourly(self):
        sched = Schedule.hourly
        with pytest.raises(ToolsError):
            sched.get_recurrence()

        assert sched.get_recurrence("23") == 23

        with pytest.raises(ToolsError):
            sched.get_recurrence(25)

    def test_get_recurrence_daily(self):
        sched = Schedule.daily
        with pytest.raises(ToolsError):
            sched.get_recurrence()

        assert sched.get_recurrence("23") == 23

        with pytest.raises(ToolsError):
            sched.get_recurrence(0)

    def test_get_recurrence_weekly(self):
        sched = Schedule.weekly
        with pytest.raises(ToolsError):
            sched.get_recurrence()

        assert sched.get_recurrence("0,1") == ["0", "1"]
        assert sched.get_recurrence("Tuesday,Sunday") == ["1", "6"]
        assert sched.get_recurrence(["Wednesday", "mondaY"]) == ["0", "2"]
        assert sched.get_recurrence(["3", "MONDAY"]) == ["0", "3"]

        with pytest.raises(ToolsError):
            sched.get_recurrence("7")

    def test_get_recurrence_monthly(self):
        sched = Schedule.monthly
        with pytest.raises(ToolsError):
            sched.get_recurrence()

        assert sched.get_recurrence("8,1,29") == ["1", "8", "29"]
        assert sched.get_recurrence(["8", 1, "29"]) == ["1", "8", "29"]

        with pytest.raises(ToolsError):
            sched.get_recurrence("30")

    def test_get_trigger(self):
        exp = {
            "name": "Trigger",
            "view": None,
            "period": "never",
            "period_time": "13:00",
            "conditions": {
                "new_entities": False,
                "previous_entities": False,
                "above": None,
                "below": None,
            },
            "run_on": "AllEntities",
        }
        value = Schedule.get_trigger()
        assert value == exp
