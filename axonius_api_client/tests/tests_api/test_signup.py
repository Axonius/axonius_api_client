# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.enforcements."""
import pytest

from axonius_api_client.api import json_api
from axonius_api_client.exceptions import ApiError, ResponseNotOk

from ..meta import EMAIL
from ..utils import random_string


class TestSignupPrivate:
    def test_signup_get(self, api_signup):
        data = api_signup._get()
        assert isinstance(data, json_api.generic.BoolValue)
        assert data.value is True

    def test_signup(self, api_signup):
        with pytest.raises(ResponseNotOk) as exc:
            api_signup._perform(password="x", company_name="x", contact_email=EMAIL)

        assert "Signup already completed" in str(exc.value)

    def test_status(self, api_signup):
        ret = api_signup._status()
        assert isinstance(ret, json_api.signup.SystemStatus)
        assert str(ret)


class TestSignupPublic:
    def test_is_signed_up(self, api_signup):
        data = api_signup.is_signed_up
        assert isinstance(data, bool)

    def test_is_licensed(self, api_signup):
        data = api_signup.is_licensed
        assert isinstance(data, bool)

    def test_is_expired(self, api_signup):
        data = api_signup.is_expired
        assert isinstance(data, bool)

    def test_indication_color(self, api_signup):
        data = api_signup.indication_color
        assert isinstance(data, str)

    def test_login_options(self, api_signup):
        data = api_signup.login_options
        assert isinstance(data, dict) and data

    def test_system_status(self, api_signup):
        ret = api_signup.system_status
        assert isinstance(ret, json_api.signup.SystemStatus)
        assert str(ret)

    def test_signup(self, api_signup):
        if api_signup.is_signed_up:
            with pytest.raises(ResponseNotOk) as exc:
                api_signup.signup(password="x", company_name="x", contact_email=EMAIL)
            assert "Signup already completed" in str(exc.value)

    def test_use_password_reset_token(self, api_signup, api_system_users, temp_user):
        token = api_system_users.get_password_reset_link(name=temp_user.user_name)

        val = api_signup.validate_password_reset_token(token=token)
        assert val is True

        password = random_string(12)

        user = api_signup.use_password_reset_token(token=token, password=password)
        assert user.user_name == temp_user.user_name

        val = api_signup.validate_password_reset_token(token=token)
        assert val is False

        token2 = api_system_users.get_password_reset_link(name=temp_user.user_name)
        with pytest.raises(ResponseNotOk) as exc:
            api_signup.use_password_reset_token(token=token2, password=password)

        assert "password must be different" in str(exc.value)

    def test_use_password_reset_token_invalid(self, api_signup):
        with pytest.raises(ApiError) as exc:
            api_signup.use_password_reset_token(token="BAD WOLF", password=random_string(12))
        assert "Password reset token is not valid" in str(exc.value)
