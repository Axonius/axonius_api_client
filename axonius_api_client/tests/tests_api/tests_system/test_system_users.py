# -*- coding: utf-8 -*-
"""Test suite."""
import pytest

from axonius_api_client.constants.api import SETTING_UNCHANGED
from axonius_api_client.constants.system import Role, User
from axonius_api_client.exceptions import ApiError, NotFoundError

from ...meta import EMAIL, EMAIL_ALT, USER_NAME


def get_by_name_external(name):
    return {User.NAME: USER_NAME, User.SOURCE: "external"}


def cleanup(apiobj):
    try:
        apiobj.delete_by_name(name=USER_NAME)
    except Exception:
        pass


class TestSystemUsersPrivate:
    @pytest.fixture(scope="class")
    def apiobj(self, api_system_users):
        return api_system_users

    def test_get(self, apiobj):
        users = apiobj._get()
        assert isinstance(users, list) and users
        for user in users:
            assert isinstance(user, dict) and user

    def test_get_limit_skip(self, apiobj):
        users = apiobj._get(limit=1, skip=0)
        assert isinstance(users, list) and users
        assert len(users) == 1
        for user in users:
            assert isinstance(user, dict) and user

    def test_add_update_delete(self, apiobj):
        cleanup(apiobj)
        role_id = apiobj.roles.get_by_name(Role.R_ADMIN)[Role.UUID]
        user = apiobj._add(user_name=USER_NAME, role_id=role_id, password=USER_NAME)
        assert user[User.NAME] == USER_NAME

        user[User.FIRST_NAME] = USER_NAME
        updated = apiobj._update(uuid=user[User.UUID], user=user)["user"]
        assert updated[User.FIRST_NAME] == USER_NAME
        assert updated[User.UUID] == user[User.UUID]

        deleted = apiobj._delete(uuid=user[User.UUID])
        assert deleted == {User.NAME: USER_NAME}
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
        user_name = apiobj.get()[0][User.NAME]
        user = apiobj.get_by_name(name=user_name)
        assert user[User.NAME] == user_name

    def test_get_by_uuid(self, apiobj):
        user_uuid = apiobj.get()[0][User.UUID]
        user = apiobj.get_by_uuid(uuid=user_uuid)
        assert user[User.UUID] == user_uuid

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
        user = apiobj.add(name=USER_NAME, role_name=Role.R_ADMIN, password=USER_NAME)
        assert user[User.NAME] == USER_NAME
        assert user[User.PASSWORD] == SETTING_UNCHANGED

        deleted = apiobj.delete_by_name(name=USER_NAME)
        assert deleted == {User.NAME: USER_NAME}
        cleanup(apiobj)

    def test_add_exists(self, apiobj):
        user_name = apiobj.get()[0][User.NAME]
        with pytest.raises(ApiError) as exc:
            apiobj.add(name=user_name, role_name=Role.R_ADMIN, password=USER_NAME)

        assert "already exists" in str(exc.value)

    def test_delete_admin(self, apiobj):
        with pytest.raises(ApiError) as exc:
            apiobj.delete_by_name(name=User.ADMIN_NAME)

        assert "Unable to delete" in str(exc.value)

    def test_set_role(self, apiobj, temp_user):
        updated = apiobj.set_role(name=temp_user[User.NAME], role_name=Role.R_VIEWER)
        assert updated[User.ROLE_NAME] == Role.R_VIEWER

    def test_set_role_external(self, apiobj, monkeypatch):
        monkeypatch.setattr(apiobj, "get_by_name", get_by_name_external)
        with pytest.raises(ApiError) as exc:
            apiobj.set_role(name=USER_NAME, role_name=Role.R_VIEWER)

        assert "must be internal user" in str(exc.value)

    def test_set_first_last(self, apiobj, temp_user):
        updated = apiobj.set_first_last(name=temp_user[User.NAME], first=USER_NAME, last=USER_NAME)
        assert updated[User.FIRST_NAME] == USER_NAME
        assert updated[User.LAST_NAME] == USER_NAME

    def test_set_first_last_external(self, apiobj, monkeypatch):
        monkeypatch.setattr(apiobj, "get_by_name", get_by_name_external)
        with pytest.raises(ApiError) as exc:
            apiobj.set_first_last(name=USER_NAME, first=USER_NAME, last=USER_NAME)

        assert "must be internal user" in str(exc.value)

    def test_set_password(self, apiobj, temp_user):
        updated = apiobj.set_password(name=temp_user[User.NAME], password=USER_NAME)
        assert updated[User.PASSWORD] == SETTING_UNCHANGED

    def test_set_password_external(self, apiobj, monkeypatch):
        monkeypatch.setattr(apiobj, "get_by_name", get_by_name_external)
        with pytest.raises(ApiError) as exc:
            apiobj.set_password(name=USER_NAME, password=USER_NAME)

        assert "must be internal user" in str(exc.value)

    def test_set_email(self, apiobj, temp_user):
        updated = apiobj.set_email(name=temp_user[User.NAME], email="badwolf@badwolf.com")
        assert updated[User.PASSWORD] == SETTING_UNCHANGED

    def test_set_email_external(self, apiobj, monkeypatch):
        monkeypatch.setattr(apiobj, "get_by_name", get_by_name_external)
        with pytest.raises(ApiError) as exc:
            apiobj.set_email(name=USER_NAME, email=USER_NAME)

        assert "must be internal user" in str(exc.value)

    def test_set_ignore_role_assignment_rules(self, apiobj, temp_user):
        with pytest.raises(ApiError) as exc:
            apiobj.set_ignore_role_assignment_rules(name=temp_user[User.NAME], enabled=True)
        assert "must be external user" in str(exc.value)

    def test_get_password_reset_link(self, apiobj, temp_user):
        link = apiobj.get_password_reset_link(name=temp_user[User.NAME])
        assert isinstance(link, str)
        assert "https://" in link

    def test_email_password_reset_link(self, apiobj, smtp_setup, temp_user):
        smtp_setup[0]()
        apiobj.set_email(name=temp_user[User.NAME], email=EMAIL)
        link, used_email = apiobj.email_password_reset_link(name=temp_user[User.NAME])
        assert used_email == EMAIL
        assert "https://" in link

    def test_email_password_reset_link_custom(self, apiobj, smtp_setup, temp_user):
        smtp_setup[0]()
        link, used_email = apiobj.email_password_reset_link(
            name=temp_user[User.NAME], email=EMAIL_ALT
        )
        assert used_email == EMAIL_ALT
        assert "https://" in link

    def test_email_password_reset_link_no_email_defined(self, apiobj, temp_user):
        with pytest.raises(ApiError) as exc:
            apiobj.email_password_reset_link(name=temp_user[User.NAME])
        assert "no email address defined" in str(exc.value)
