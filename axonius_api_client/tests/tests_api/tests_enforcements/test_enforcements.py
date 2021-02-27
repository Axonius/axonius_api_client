# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.enforcements."""
'''
# XXX need to re-flush EC!
import pytest

# from axonius_api_client.exceptions import NotFoundError

# from ...meta import CREATE_EC_ACTION_MAIN, CREATE_EC_NAME, CREATE_EC_TRIGGER1


class TestEnforcementsBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_enforcements):
        return api_enforcements


class TestEnforcementsPrivate(TestEnforcementsBase):
    def test_private_get(self, apiobj):
        data = apiobj._get()
        assert isinstance(data, dict)

        assets = data["assets"]
        assert isinstance(assets, list)

        for asset in assets:
            assert isinstance(asset, dict)


class TestEnforcementsPublic(TestEnforcementsBase):
    def test_get(self, apiobj):
        data = apiobj.get()
        assert isinstance(data, list)
        for found in data:
            assert isinstance(found["uuid"], str)
            assert isinstance(found["actions.main"], str)
            assert isinstance(found["name"], str)
            assert isinstance(found["date_fetched"], str)
            assert isinstance(found["last_updated"], str)
            assert "triggers.last_triggered" in found
            assert "triggers.times_triggered" in found

    def test_get_maxpages(self, apiobj):
        found = apiobj.get(max_pages=1, page_size=1)
        assert isinstance(found, list)
        # we can't test for length if there are no enforcements...
        # assert len(found) == 1

    def test_create_get_delete(self, apiobj, api_users):
        try:
            old_found = apiobj.get_by_name(CREATE_EC_NAME, eq_single=False)
        except Exception:
            old_found = None
        else:
            deleted = apiobj.delete(rows=old_found)
            assert isinstance(deleted, dict)
            assert isinstance(deleted["deleted"], int)
            assert deleted["deleted"] == 1

        trigger_name = api_users.saved_query.get()[0]["name"]
        trigger = {"view": {"name": trigger_name, "entity": "users"}}
        trigger.update(CREATE_EC_TRIGGER1)

        created = apiobj._create(
            name=CREATE_EC_NAME, main=CREATE_EC_ACTION_MAIN, triggers=[trigger],
        )
        assert isinstance(created, str)

        found = apiobj.get_by_name(CREATE_EC_NAME)
        """
        {
            "actions.main": "Badwolf Create Notification",
            "date_fetched": "2019-09-10 23:17:07+00:00",
            "last_updated": "Tue, 10 Sep 2019 23:17:07 GMT",
            "name": "Badwolf EC Example",
            "triggers.last_triggered": null,
            "triggers.times_triggered": 0,
            "triggers.view.name": "Users Created in Last 30 Days",
            "uuid": "5d782ef380ded0001bbe3c47"
        }
        """
        assert isinstance(found, dict)
        assert found["uuid"] == created
        assert found["actions.main"] == CREATE_EC_ACTION_MAIN["name"]
        assert found["name"] == CREATE_EC_NAME
        assert isinstance(found["date_fetched"], str)
        assert isinstance(found["last_updated"], str)
        assert "triggers.last_triggered" in found
        assert "triggers.times_triggered" in found
        assert found["triggers.view.name"] == trigger_name

        found_by_id = apiobj.get_by_uuid(found["uuid"])
        assert isinstance(found_by_id, dict)

        deleted = apiobj.delete(rows=found_by_id)
        assert isinstance(deleted, dict)
        assert isinstance(deleted["deleted"], int)
        assert deleted["deleted"] == 1

        with pytest.raises(NotFoundError):
            apiobj.get_by_uuid(found["uuid"])

        with pytest.raises(NotFoundError):
            apiobj.get_by_name(found["name"])
'''
