# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.enforcements."""
import datetime

import pytest
from axonius_api_client.api import json_api
from axonius_api_client.exceptions import ApiError, NotFoundError
from axonius_api_client.tools import listify

EC_NAME = "badwolf enforcement"
EC_TRIGGER_NAME = "badwolf trigger enforcement"
ACTION_TYPE = "create_notification"
ACTION_NAME = "badwolf action"
ACTION_TRIGGER_NAME = "badwolf triggerx action"


class EnforcementsBase:
    """Pass."""

    def cleanup(self, api_client, name):
        """Pass."""
        data = api_client.enforcements._get()
        for x in data:
            if x.name in listify(name):
                deleted = x.delete()
                print(f"Deleted enforcement {x.name!r} {x.uuid!r}")
                assert isinstance(deleted, json_api.generic.Deleted)
                assert deleted.deleted == 1

    @pytest.fixture(scope="function")
    def ec_obj(self, api_client):
        self.cleanup(api_client, EC_NAME)

        main = {"name": ACTION_NAME, "action": {"action_name": ACTION_TYPE, "config": {}}}
        ec_obj = api_client.enforcements._create(name=EC_NAME, main=main)
        print(f"Created enforcement {ec_obj.name!r} {ec_obj.uuid!r}")
        assert isinstance(ec_obj, json_api.enforcements.Enforcement)
        yield ec_obj

        self.cleanup(api_client, EC_NAME)

        data = api_client.enforcements._get()
        for x in data:
            assert x.name != EC_NAME
            assert x.uuid != ec_obj.uuid

    @pytest.fixture(scope="class")
    def sq_obj(self, api_client):
        return api_client.devices.saved_query.get()[0]


class TestEnforcementsPrivate(EnforcementsBase):
    def test_already_exists(self, api_client, ec_obj):
        with pytest.raises(ApiError):
            api_client.enforcements._check_name_exists(value=ec_obj.name)

    def test_not_exists(self, api_client, ec_obj):
        data = api_client.enforcements._check_name_exists(value="BADWOLF BADWOLF")
        assert data is None

    def test_get(self, api_client, ec_obj):
        data = api_client.enforcements._get()
        assert isinstance(data, list)
        assert data
        for x in data:
            assert isinstance(x, json_api.enforcements.EnforcementBasic)
        assert ec_obj.name in [x.name for x in data]
        assert ec_obj.uuid in [x.uuid for x in data]

    def test_get_by_uuid(self, api_client, ec_obj):
        data = api_client.enforcements._get_by_uuid(uuid=ec_obj.uuid)
        assert isinstance(data, json_api.enforcements.Enforcement)
        assert data.name == ec_obj.name
        assert data.uuid == ec_obj.uuid

    def test_find_trigger(self, api_client, sq_obj):
        data = api_client.enforcements._find_trigger(name=sq_obj["name"], type="devices")
        assert data == {"id": sq_obj["id"], "entity": "devices"}

    def test_find_trigger_bad_type(self, api_client):
        with pytest.raises(ApiError):
            api_client.enforcements._find_trigger(name="badwolf", type="BADWOLF")

    def test_triggers_map(self, api_client):
        data = api_client.enforcements._triggers_map
        assert data == {"devices": api_client.devices, "users": api_client.users}

    def test_get_run_on_true(self, api_client):
        data = api_client.enforcements._get_run_on(value=True)
        assert data == "AddedEntities"

    def test_get_run_on_false(self, api_client):
        data = api_client.enforcements._get_run_on(value=False)
        assert data == "AllEntities"


class TestEnforcementsPublic(EnforcementsBase):
    @pytest.fixture(scope="function")
    def ec_trigger_obj(self, api_client, sq_obj):
        self.cleanup(api_client, EC_TRIGGER_NAME)

        ec_obj = api_client.enforcements.create(
            name=EC_TRIGGER_NAME,
            main_action_name=ACTION_TRIGGER_NAME,
            main_action_type=ACTION_TYPE,
            trigger_name=sq_obj["name"],
            trigger_type="devices",
        )
        print(f"Created enforcement {ec_obj.name!r} {ec_obj.uuid!r}")
        assert isinstance(ec_obj, json_api.enforcements.Enforcement)

        assert ec_obj.trigger_name == sq_obj["name"]
        assert ec_obj.trigger_type == "devices"
        assert ec_obj.trigger_id == sq_obj["uuid"]
        yield ec_obj

        self.cleanup(api_client, EC_TRIGGER_NAME)

        data = api_client.enforcements._get()
        for x in data:
            assert x.name != EC_TRIGGER_NAME
            assert x.uuid != ec_obj.uuid

    def test_get(self, api_client, ec_obj):
        data = api_client.enforcements.get()
        assert data.__class__.__name__ != "generator"
        assert isinstance(data, list)
        assert data
        for x in data:
            assert isinstance(x, json_api.enforcements.EnforcementBasic)
        assert ec_obj.name in [x.name for x in data]
        assert ec_obj.uuid in [x.uuid for x in data]

    def test_get_generator(self, api_client, ec_obj):
        data = api_client.enforcements.get(generator=True)
        assert data.__class__.__name__ == "generator"
        data = list(data)
        for x in data:
            assert isinstance(x, json_api.enforcements.EnforcementBasic)
        assert ec_obj.name in [x.name for x in data]
        assert ec_obj.uuid in [x.uuid for x in data]

    def test_get_full(self, api_client, ec_obj):
        data = api_client.enforcements.get(full=True)
        assert isinstance(data, list)
        assert data
        for x in data:
            assert isinstance(x, json_api.enforcements.Enforcement)
        assert ec_obj.name in [x.name for x in data]
        assert ec_obj.uuid in [x.uuid for x in data]

    def test_get_by_uuid(self, api_client, ec_obj):
        data = api_client.enforcements.get_by_uuid(value=ec_obj.uuid)
        assert isinstance(data, json_api.enforcements.Enforcement)
        assert data.name == ec_obj.name
        assert data.uuid == ec_obj.uuid

    def test_get_by_name(self, api_client, ec_obj):
        data = api_client.enforcements.get_by_name(value=ec_obj.name)
        assert isinstance(data, json_api.enforcements.Enforcement)
        assert data.name == ec_obj.name
        assert data.uuid == ec_obj.uuid

    def test_get_by_uuid_basic(self, api_client, ec_obj):
        data = api_client.enforcements.get_by_uuid(value=ec_obj.uuid, full=False)
        assert isinstance(data, json_api.enforcements.EnforcementBasic)
        assert data.name == ec_obj.name
        assert data.uuid == ec_obj.uuid

    def test_get_by_name_basic(self, api_client, ec_obj):
        data = api_client.enforcements.get_by_name(value=ec_obj.name, full=False)
        assert isinstance(data, json_api.enforcements.EnforcementBasic)
        assert data.name == ec_obj.name
        assert data.uuid == ec_obj.uuid

    def test_get_by_uuid_not_found(self, api_client):
        with pytest.raises(NotFoundError):
            api_client.enforcements.get_by_uuid(value="badwolf badwolf")

    def test_get_by_name_not_found(self, api_client):
        with pytest.raises(NotFoundError):
            api_client.enforcements.get_by_name(value="badwolf badwolf")

    def test_create_trigger(self, api_client, ec_trigger_obj):
        assert ec_trigger_obj

    def test_create(self, api_client):
        try:
            data = api_client.enforcements.get_by_name(value=EC_NAME)
        except NotFoundError:
            pass
        else:
            data.delete()

        data = api_client.enforcements.create(
            name=EC_NAME, main_action_name=ACTION_NAME, main_action_type=ACTION_TYPE
        )
        assert isinstance(data, json_api.enforcements.Enforcement)
        assert data.name == EC_NAME
        assert data.main_action_name == ACTION_NAME
        assert data.main_action_type == ACTION_TYPE
        assert not data.triggers
        assert data.schedule_enabled is False
        assert data.schedule_type == "None"
        assert data.schedule_recurrence == "n/a"
        assert data.schedule_time == ""
        assert data.trigger_type == ""
        assert data.trigger_id == ""
        assert data.trigger_name == ""
        assert data.trigger_run_last is None
        assert data.trigger_run_count == 0
        assert data._run_on == ""
        assert data.only_run_against_new_assets is False
        assert data.only_run_when_assets_added is False
        assert data.only_run_when_assets_removed is False
        assert data.only_run_when_asset_count_above is None
        assert data.only_run_when_asset_count_below is None
        assert isinstance(data.updated_on, datetime.datetime)
        assert isinstance(data.updated_by_user_name, str) and data.updated_by_user_name
        assert isinstance(data.updated_by_first_name, str)
        assert isinstance(data.updated_by_last_name, str)
        assert isinstance(data.updated_by_full_name, str)
        assert data._get_schema_cls() == json_api.enforcements.EnforcementSchema

        assert str(data)
        assert repr(data)

        name_str = data._get_name_str()
        assert data.name in name_str
        assert data.uuid in name_str

        updated_str = data._get_updated_str()
        assert data.updated_by_user_name in updated_str
        assert data.updated_by_full_name in updated_str

        trigger_str = data._get_trigger_str()
        assert "None" in trigger_str

        schedule_str = data._get_schedule_str()
        assert "None" in schedule_str

        basic_from_full = data.get_basic()
        assert isinstance(basic_from_full, json_api.enforcements.EnforcementBasic)
        assert basic_from_full._get_schema_cls() == json_api.enforcements.EnforcementBasicSchema

        basic_tablize = basic_from_full.to_tablize()
        assert isinstance(basic_tablize, dict) and basic_tablize

        full_from_basic = basic_from_full.get_full()
        assert isinstance(full_from_basic, json_api.enforcements.Enforcement)

        full_from_full = data.get_full()
        assert isinstance(full_from_full, json_api.enforcements.Enforcement)

        deleted = data.delete()
        assert isinstance(deleted, json_api.generic.Deleted)
        assert deleted.deleted == 1

        deleted_basic = basic_from_full.delete()
        assert deleted_basic.deleted == 0

        with pytest.raises(NotFoundError):
            api_client.enforcements.get_by_name(value=EC_NAME)

    # def test_create_trigger(self, api_client, sq_obj):
    #     try:
    #         data = api_client.enforcements.get_by_name(value=EC_NAME)
    #     except NotFoundError:
    #         pass
    #     else:
    #         data.delete()

    #     data = api_client.enforcements.create(
    #         name=EC_NAME,
    #         main_action_name=ACTION_NAME,
    #         main_action_type=ACTION_TYPE,
    #         trigger_name=sq_obj["name"],
    #         trigger_type="devices",
    #     )
    #     assert isinstance(data, json_api.enforcements.Enforcement)
    #     assert data.name == EC_NAME
    #     assert data.main_action_name == ACTION_NAME
    #     assert data.main_action_type == ACTION_TYPE

    #     deleted = data.delete()
    #     assert isinstance(deleted, json_api.generic.Deleted)

    #     with pytest.raises(NotFoundError):
    #         api_client.enforcements.get_by_name(value=EC_NAME)
