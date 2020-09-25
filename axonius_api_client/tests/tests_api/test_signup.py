# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.enforcements."""
import pytest

from axonius_api_client.exceptions import ResponseNotOk


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
