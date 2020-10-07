# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.enforcements."""
import pytest

from axonius_api_client.constants.system import User
from axonius_api_client.exceptions import ResponseNotOk

from ..utils import random_string


class TestSignup:
    @pytest.fixture(scope="class")
    def apiobj(self, api_signup):
        return api_signup


class TestSignupPrivate(TestSignup):
    def test_signup_get(self, apiobj):
        data = apiobj._signup_get()
        assert isinstance(data, dict)
        signup = data.pop("signup")
        assert isinstance(signup, bool)
        assert not data

    def test_signup(self, apiobj):
        data = apiobj._signup_post(password="x", company_name="x", contact_email="x")
        exp = {
            "additional_data": None,
            "message": "Signup already completed",
            "status": "error",
        }
        assert data == exp


class TestSignupPublic(TestSignup):
    def test_is_signed_up(self, apiobj):
        data = apiobj.is_signed_up
        assert isinstance(data, bool) and data

    def test_signup(self, apiobj):
        with pytest.raises(ResponseNotOk):
            apiobj.signup(password="x", company_name="x", contact_email="x")

    def test_use_password_reset_token(self, apiobj, api_system_users, temp_user):
        token = api_system_users.get_password_reset_link(name=temp_user[User.NAME])
        password = random_string(12)
        user = apiobj.use_password_reset_token(token=token, password=password)
        assert user == temp_user[User.NAME]

        with pytest.raises(ResponseNotOk) as exc:
            apiobj.use_password_reset_token(token=token, password=random_string(12))
        assert "token is expired" in str(exc.value)

        token = api_system_users.get_password_reset_link(name=temp_user[User.NAME])
        with pytest.raises(ResponseNotOk) as exc:
            apiobj.use_password_reset_token(token=token, password=password)
        assert "password must be different" in str(exc.value)
