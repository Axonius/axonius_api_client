# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.enforcements."""
import pytest

from axonius_api_client.api import json_api
from axonius_api_client.exceptions import ResponseNotOk

from ..meta import EMAIL
from ..utils import random_string


class TestSignup:
    @pytest.fixture(scope="class")
    def apiobj(self, api_signup):
        return api_signup


class TestSignupPrivate(TestSignup):
    def test_signup_get(self, apiobj):
        data = apiobj._get()
        assert isinstance(data, json_api.generic.BoolValue)
        assert data.value is True

    def test_signup(self, apiobj):
        with pytest.raises(ResponseNotOk) as exc:
            apiobj._perform(password="x", company_name="x", contact_email=EMAIL)

        assert "Signup already completed" in str(exc.value)


class TestSignupPublic(TestSignup):
    def test_is_signed_up(self, apiobj):
        data = apiobj.is_signed_up
        assert isinstance(data, bool) and data

    def test_signup(self, apiobj):
        with pytest.raises(ResponseNotOk) as exc:
            apiobj.signup(password="x", company_name="x", contact_email=EMAIL)
        assert "Signup already completed" in str(exc.value)

    def test_use_password_reset_token(self, apiobj, api_system_users, temp_user):
        token = api_system_users.get_password_reset_link(name=temp_user.user_name)
        password = random_string(12)

        user = apiobj.use_password_reset_token(token=token, password=password)
        assert user.user_name == temp_user.user_name

        val = apiobj.validate_password_reset_token(token=token)
        assert val is False

        token2 = api_system_users.get_password_reset_link(name=temp_user.user_name)

        with pytest.raises(ResponseNotOk) as exc:
            apiobj.use_password_reset_token(token=token2, password=password)

        assert "password must be different" in str(exc.value)
