# -*- coding: utf-8 -*-
"""Test suite."""
import pytest
from axonius_api_client.api.json_api.system_users import SystemUser
from axonius_api_client.constants.api import SETTING_UNCHANGED
from axonius_api_client.exceptions import ApiError, NotFoundError

from ...meta import EMAIL, EMAIL_ALT, USER_NAME


def get_by_name_external(name):
    return {"user_name": USER_NAME, "source": "external"}


def cleanup(api_client):
    objs = api_client.system_users._get()
    for obj in objs:
        if obj.user_name in [USER_NAME]:
            api_client.system_users._delete(uuid=obj.uuid)
            print(f"deleted {obj}")


class TestSystemUsersPrivate:
    def test_get(self, api_client):
        users = api_client.system_users._get()
        assert isinstance(users, list) and users
        for user in users:
            assert isinstance(user, SystemUser) and user

    def test_add_update_delete(self, api_client):
        cleanup(api_client)
        role_id = api_client.system_users.roles.get_by_name("Admin")["uuid"]
        user = api_client.system_users._add(
            user_name=USER_NAME, role_id=role_id, password=USER_NAME
        )
        assert isinstance(user, SystemUser)
        assert user.user_name == USER_NAME

        user.first_name = USER_NAME
        updated = api_client.system_users._update(**user.to_dict())
        assert isinstance(updated, SystemUser)
        assert updated.first_name == USER_NAME
        assert updated.uuid == user.uuid

        deleted = api_client.system_users._delete(uuid=user.uuid)
        assert deleted.document_meta == {"user_name": USER_NAME}
        cleanup(api_client)


class TestSystemUsersPublic:
    def test_get(self, api_client):
        users = api_client.system_users.get()
        assert isinstance(users, list) and users
        for user in users:
            assert isinstance(user, dict) and user

    def test_get_by_name(self, api_client):
        user_name = api_client.system_users.get()[0]["user_name"]
        user = api_client.system_users.get_by_name(name=user_name)
        assert user["user_name"] == user_name

    def test_get_by_uuid(self, api_client):
        user_uuid = api_client.system_users.get()[0]["uuid"]
        user = api_client.system_users.get_by_uuid(uuid=user_uuid)
        assert user["uuid"] == user_uuid

    def test_get_by_name_not_found(self, api_client):
        with pytest.raises(NotFoundError) as exc:
            api_client.system_users.get_by_name(name="XxXxX")

        assert "not found" in str(exc.value)

    def test_get_by_uuid_not_found(self, api_client):
        with pytest.raises(NotFoundError) as exc:
            api_client.system_users.get_by_uuid(uuid="XxXxX")

        assert "not found" in str(exc.value)

    def test_add_delete(self, api_client):
        cleanup(api_client)
        user = api_client.system_users.add(name=USER_NAME, role_name="Admin", password=USER_NAME)
        assert user["user_name"] == USER_NAME
        assert user["password"] == SETTING_UNCHANGED

        deleted = api_client.system_users.delete_by_name(name=USER_NAME)
        assert deleted == {"user_name": USER_NAME}
        cleanup(api_client)

    def test_add_exists(self, api_client):
        user_name = api_client.system_users.get()[0]["user_name"]
        with pytest.raises(ApiError) as exc:
            api_client.system_users.add(name=user_name, role_name="Admin", password=USER_NAME)

        assert "already exists" in str(exc.value)

    def test_delete_admin(self, api_client):
        with pytest.raises(ApiError) as exc:
            api_client.system_users.delete_by_name(name="admin")

        assert "Unable to delete" in str(exc.value)

    def test_set_role(self, api_client, temp_user):
        updated = api_client.system_users.set_role(name=temp_user.user_name, role_name="Viewer")
        assert updated["role_name"] == "Viewer"

    def test_set_role_external(self, api_client, monkeypatch):
        monkeypatch.setattr(api_client.system_users, "get_by_name", get_by_name_external)
        with pytest.raises(ApiError) as exc:
            api_client.system_users.set_role(name=USER_NAME, role_name="Viewer")

        assert "must be internal user" in str(exc.value)

    def test_set_first_last(self, api_client, temp_user):
        updated = api_client.system_users.set_first_last(
            name=temp_user.user_name, first=USER_NAME, last=USER_NAME
        )
        assert updated["first_name"] == USER_NAME
        assert updated["last_name"] == USER_NAME

    def test_set_first_last_external(self, api_client, monkeypatch):
        monkeypatch.setattr(api_client.system_users, "get_by_name", get_by_name_external)
        with pytest.raises(ApiError) as exc:
            api_client.system_users.set_first_last(name=USER_NAME, first=USER_NAME, last=USER_NAME)

        assert "must be internal user" in str(exc.value)

    def test_set_password(self, api_client, temp_user):
        updated = api_client.system_users.set_password(name=temp_user.user_name, password=USER_NAME)
        assert updated["password"] == SETTING_UNCHANGED

    def test_set_password_external(self, api_client, monkeypatch):
        monkeypatch.setattr(api_client.system_users, "get_by_name", get_by_name_external)
        with pytest.raises(ApiError) as exc:
            api_client.system_users.set_password(name=USER_NAME, password=USER_NAME)

        assert "must be internal user" in str(exc.value)

    def test_set_email(self, api_client, temp_user):
        updated = api_client.system_users.set_email(
            name=temp_user.user_name, email="badwolf@badwolf.com"
        )
        assert updated["password"] == SETTING_UNCHANGED

    def test_set_email_external(self, api_client, monkeypatch):
        monkeypatch.setattr(api_client.system_users, "get_by_name", get_by_name_external)
        with pytest.raises(ApiError) as exc:
            api_client.system_users.set_email(name=USER_NAME, email=USER_NAME)

        assert "must be internal user" in str(exc.value)

    def test_set_ignore_role_assignment_rules(self, api_client, temp_user):
        with pytest.raises(ApiError) as exc:
            api_client.system_users.set_ignore_role_assignment_rules(
                name=temp_user.user_name, enabled=True
            )
        assert "must be external user" in str(exc.value)

    def test_get_password_reset_link(self, api_client, temp_user):
        link = api_client.system_users.get_password_reset_link(name=temp_user.user_name)
        assert isinstance(link, str)
        assert "https://" in link

    def test_email_password_reset_link(self, api_client, smtp_setup, temp_user):
        smtp_setup[0]()
        api_client.system_users.set_email(name=temp_user.user_name, email=EMAIL)
        link, used_email = api_client.system_users.email_password_reset_link(
            name=temp_user.user_name
        )
        assert used_email == EMAIL
        assert "https://" in link

    def test_email_password_reset_link_custom(self, api_client, smtp_setup, temp_user):
        smtp_setup[0]()
        link, used_email = api_client.system_users.email_password_reset_link(
            name=temp_user.user_name, email=EMAIL_ALT
        )
        assert used_email == EMAIL_ALT
        assert "https://" in link

    def test_email_password_reset_link_no_email_defined(self, api_client, temp_user):
        with pytest.raises(ApiError) as exc:
            api_client.system_users.email_password_reset_link(name=temp_user.user_name)
        assert "no email address defined" in str(exc.value)
