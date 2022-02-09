# -*- coding: utf-8 -*-
"""Test suite."""
import marshmallow
import pytest

from axonius_api_client.api.json_api.system_users import SystemUser, SystemUserCreateSchema
from axonius_api_client.constants.api import SETTING_UNCHANGED
from axonius_api_client.exceptions import ApiError, NotFoundError

from ...meta import EMAIL, EMAIL_ALT, USER_NAME


def get_by_name_external(name):
    return {"user_name": USER_NAME, "source": "external"}


def cleanup(apiobj):
    objs = apiobj._get()
    for obj in objs:
        if obj.user_name in [USER_NAME]:
            apiobj._delete(uuid=obj.uuid)
            print(f"deleted {obj}")


class TestSystemUsersPrivate:
    @pytest.fixture(scope="class")
    def apiobj(self, api_system_users):
        return api_system_users

    def test_get(self, apiobj):
        users = apiobj._get()
        assert isinstance(users, list) and users
        for user in users:
            assert isinstance(user, SystemUser) and user

    def test_add_update_delete(self, apiobj):
        cleanup(apiobj)
        role_id = apiobj.roles.get_by_name("Admin")["uuid"]
        with pytest.raises(marshmallow.ValidationError) as exc:
            schema = SystemUserCreateSchema()
            schema.load(
                {
                    "data": {
                        "type": "create_user_schema",
                        "attributes": {"user_name": "x", "role_id": "x"},
                    }
                }
            )
        assert "Must supply a password if " in str(exc.value)

        user = apiobj._add(user_name=USER_NAME, role_id=role_id, password=USER_NAME)
        assert isinstance(user, SystemUser)
        assert user.user_name == USER_NAME

        user.first_name = USER_NAME
        updated = apiobj._update(**user.to_dict())
        assert isinstance(updated, SystemUser)
        assert updated.first_name == USER_NAME
        assert updated.uuid == user.uuid

        deleted = apiobj._delete(uuid=user.uuid)
        assert deleted.document_meta == {"user_name": USER_NAME}
        cleanup(apiobj)


class TestSystemUsersPublic:
    @pytest.fixture(scope="class")
    def apiobj(self, api_system_users):
        return api_system_users

    def test_get(self, apiobj):
        users = apiobj.get()
        assert isinstance(users, list) and users
        for user in users:
            assert isinstance(user, dict) and user

    def test_get_by_name(self, apiobj):
        user_name = apiobj.get()[0]["user_name"]
        user = apiobj.get_by_name(name=user_name)
        assert user["user_name"] == user_name

    def test_get_by_uuid(self, apiobj):
        user_uuid = apiobj.get()[0]["uuid"]
        user = apiobj.get_by_uuid(uuid=user_uuid)
        assert user["uuid"] == user_uuid

    def test_get_by_name_not_found(self, apiobj):
        with pytest.raises(NotFoundError) as exc:
            apiobj.get_by_name(name="XxXxX")

        assert "not found" in str(exc.value)

    def test_get_by_uuid_not_found(self, apiobj):
        with pytest.raises(NotFoundError) as exc:
            apiobj.get_by_uuid(uuid="XxXxX")

        assert "not found" in str(exc.value)

    def test_add_delete(self, apiobj):
        cleanup(apiobj)
        user = apiobj.add(name=USER_NAME, role_name="Admin", password=USER_NAME)
        assert user["user_name"] == USER_NAME
        assert user["password"] == SETTING_UNCHANGED

        deleted = apiobj.delete_by_name(name=USER_NAME)
        assert deleted == {"user_name": USER_NAME}
        cleanup(apiobj)

    def test_add_exists(self, apiobj):
        user_name = apiobj.get()[0]["user_name"]
        with pytest.raises(ApiError) as exc:
            apiobj.add(name=user_name, role_name="Admin", password=USER_NAME)

        assert "already exists" in str(exc.value)

    def test_add_err_password(self, apiobj):
        with pytest.raises(ApiError) as exc:
            apiobj.add(name="foobar", password="", role_name="")
        assert "Must supply password" in str(exc.value)

    def test_add_err_email(self, apiobj):
        with pytest.raises(ApiError) as exc:
            apiobj.add(
                name="foobar", password="barfoo", role_name="", email=None, email_password_link=True
            )
        assert "Must supply email" in str(exc.value)

    def test_delete_admin(self, apiobj):
        with pytest.raises(ApiError) as exc:
            apiobj.delete_by_name(name="admin")

        assert "Unable to delete" in str(exc.value)

    def test_set_role(self, apiobj, temp_user):
        updated = apiobj.set_role(name=temp_user.user_name, role_name="Viewer")
        assert updated["role_name"] == "Viewer"

    def test_set_role_external(self, apiobj, monkeypatch):
        monkeypatch.setattr(apiobj, "get_by_name", get_by_name_external)
        with pytest.raises(ApiError) as exc:
            apiobj.set_role(name=USER_NAME, role_name="Viewer")

        assert "must be internal user" in str(exc.value)

    def test_set_first_last(self, apiobj, temp_user):
        updated = apiobj.set_first_last(name=temp_user.user_name, first=USER_NAME, last=USER_NAME)
        assert updated["first_name"] == USER_NAME
        assert updated["last_name"] == USER_NAME

    def test_set_first_last_external(self, apiobj, monkeypatch):
        monkeypatch.setattr(apiobj, "get_by_name", get_by_name_external)
        with pytest.raises(ApiError) as exc:
            apiobj.set_first_last(name=USER_NAME, first=USER_NAME, last=USER_NAME)

        assert "must be internal user" in str(exc.value)

    def test_set_password(self, apiobj, temp_user):
        updated = apiobj.set_password(name=temp_user.user_name, password=USER_NAME)
        assert updated["password"] == SETTING_UNCHANGED

    def test_set_password_external(self, apiobj, monkeypatch):
        monkeypatch.setattr(apiobj, "get_by_name", get_by_name_external)
        with pytest.raises(ApiError) as exc:
            apiobj.set_password(name=USER_NAME, password=USER_NAME)

        assert "must be internal user" in str(exc.value)

    def test_set_email(self, apiobj, temp_user):
        updated = apiobj.set_email(name=temp_user.user_name, email="badwolf@badwolf.com")
        assert updated["password"] == SETTING_UNCHANGED

    def test_set_email_external(self, apiobj, monkeypatch):
        monkeypatch.setattr(apiobj, "get_by_name", get_by_name_external)
        with pytest.raises(ApiError) as exc:
            apiobj.set_email(name=USER_NAME, email=USER_NAME)

        assert "must be internal user" in str(exc.value)

    def test_set_ignore_role_assignment_rules(self, apiobj, temp_user):
        with pytest.raises(ApiError) as exc:
            apiobj.set_ignore_role_assignment_rules(name=temp_user.user_name, enabled=True)
        assert "must be external user" in str(exc.value)

    def test_get_password_reset_link(self, apiobj, temp_user):
        link = apiobj.get_password_reset_link(name=temp_user.user_name)
        assert isinstance(link, str)
        assert "https://" in link

    def test_email_password_reset_link(self, apiobj, smtp_setup, temp_user):
        smtp_setup[0]()
        apiobj.set_email(name=temp_user.user_name, email=EMAIL)
        link, used_email = apiobj.email_password_reset_link(name=temp_user.user_name)
        assert used_email == EMAIL
        assert "https://" in link

    def test_email_password_reset_link_custom(self, apiobj, smtp_setup, temp_user):
        smtp_setup[0]()
        link, used_email = apiobj.email_password_reset_link(
            name=temp_user.user_name, email=EMAIL_ALT
        )
        assert used_email == EMAIL_ALT
        assert "https://" in link

    def test_email_password_reset_link_no_email_defined(self, apiobj, temp_user):
        with pytest.raises(ApiError) as exc:
            apiobj.email_password_reset_link(name=temp_user.user_name)
        assert "no email address defined" in str(exc.value)
