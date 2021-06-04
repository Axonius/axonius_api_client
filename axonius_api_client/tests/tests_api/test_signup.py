# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.enforcements."""
import pytest

from axonius_api_client.api import json_api
from axonius_api_client.exceptions import ResponseNotOk

from ..meta import EMAIL
from ..utils import random_string


class TestSignup:
    """Pass."""


class TestSignupPrivate(TestSignup):
    def test_signup_get(self, api_client):
        data = api_client.signup._get()
        assert isinstance(data, json_api.generic.BoolValue)
        assert data.value is True

    def test_signup(self, api_client):
        with pytest.raises(ResponseNotOk) as exc:
            api_client.signup._perform(password="x", company_name="x", contact_email=EMAIL)

        assert "Signup already completed" in str(exc.value)


class TestSignupPublic(TestSignup):
    def test_is_signed_up(self, api_client):
        data = api_client.signup.is_signed_up
        assert isinstance(data, bool) and data

    def test_signup(self, api_client):
        with pytest.raises(ResponseNotOk) as exc:
            api_client.signup.signup(password="x", company_name="x", contact_email=EMAIL)
        assert "Signup already completed" in str(exc.value)

    def test_use_password_reset_token(self, api_client, temp_user):
        token = api_client.system_users.get_password_reset_link(name=temp_user.user_name)
        password = random_string(12)

        user = api_client.signup.use_password_reset_token(token=token, password=password)
        assert user.user_name == temp_user.user_name

        val = api_client.signup.validate_password_reset_token(token=token)
        assert val is False

        token2 = api_client.system_users.get_password_reset_link(name=temp_user.user_name)

        with pytest.raises(ResponseNotOk) as exc:
            api_client.signup.use_password_reset_token(token=token2, password=password)

        assert "password must be different" in str(exc.value)
