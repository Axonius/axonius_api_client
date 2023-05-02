# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import typing as t
import pytest

from axonius_api_client.auth import AuthApiKey, AuthCredentials, AuthModel, AuthNull
from axonius_api_client.exceptions import InvalidCredentials, NotLoggedIn
from axonius_api_client.http import Http
from ..utils import get_connect

BAD_CREDS = "bad wolf"


# noinspection PyMethodMayBeStatic
class AuthBase:
    """Base class for auth tests."""

    def test_str(self, auth_valid: dict, auth_cls: t.Type[AuthModel]):
        auth: AuthModel = auth_cls(**auth_valid)
        assert isinstance(auth.fields, list)
        assert "url" in str(auth)
        assert "url" in repr(auth)

    def test_logout(self, auth_valid: dict, auth_cls: t.Type[AuthModel]):
        auth: AuthModel = auth_cls(**auth_valid)

        action = auth.logout()
        assert action is False
        assert auth.is_logged_in is False

        action = auth.login()
        assert action is True
        assert auth.is_logged_in is True

        action = auth.logout()
        assert action is True
        assert auth.is_logged_in is False

        action = auth.logout()
        assert action is False

    def test_login_already_logged_in(self, auth_valid: dict, auth_cls: t.Type[AuthModel]):
        auth: AuthModel = auth_cls(**auth_valid)

        action = auth.login()
        assert action is True
        assert auth.is_logged_in is True

        action = auth.login()
        assert action is False
        assert auth.is_logged_in is True

    def test_login_invalid_credentials(self, auth_invalid: dict, auth_cls: t.Type[AuthModel]):
        auth: AuthModel = auth_cls(**auth_invalid)
        with pytest.raises(InvalidCredentials):
            auth.login()

    def test_not_logged_in(self, auth_invalid: dict, auth_cls: t.Type[AuthModel]):
        auth: AuthModel = auth_cls(**auth_invalid)
        with pytest.raises(NotLoggedIn):
            auth.check_login()


class TestNull(AuthBase):
    @pytest.fixture()
    def auth_valid(self, arg_url_http: Http) -> dict:
        """Get credentials from command line args."""
        return {"http": arg_url_http}

    @pytest.fixture()
    def auth_invalid(self, arg_url_http: Http) -> dict:
        """Get credentials from command line args."""
        return {"http": arg_url_http}

    @pytest.fixture()
    def auth_cls(self) -> t.Type[AuthModel]:
        """Get the class to run tests against."""
        return AuthNull

    def test_login_invalid_credentials(self, auth_invalid: dict, auth_cls: t.Type[AuthModel]):
        auth: AuthModel = auth_cls(**auth_invalid)
        action = auth.login()
        assert action is True
        assert auth.is_logged_in is True


class TestCredentials(AuthBase):
    """Test suite for axonius_api_client.auth.AuthCredentials."""

    @pytest.fixture()
    def auth_valid(
        self, arg_url_http: Http, arg_key: str, arg_secret: str, arg_credentials: bool
    ) -> dict:
        """Get credentials from command line args."""
        if not arg_credentials:
            pytest.skip("credentials=False, skipping test")
        return {"http": arg_url_http, "username": arg_key, "password": arg_secret}

    @pytest.fixture()
    def auth_invalid(self, arg_url_http: Http) -> dict:
        """Get credentials from command line args."""
        return {"http": arg_url_http, "username": BAD_CREDS, "password": BAD_CREDS}

    @pytest.fixture()
    def auth_cls(self) -> t.Type[AuthModel]:
        """Get the class to run tests against."""
        return AuthCredentials


class TestApiKey(AuthBase):
    @pytest.fixture()
    def auth_valid(
        self, request, arg_url_http: Http, arg_key: str, arg_secret: str, arg_credentials: bool
    ) -> dict:
        """Get credentials from command line args."""
        if arg_credentials:
            client = get_connect(request)
            client.start()
            arg_key = client.api_keys["api_key"]
            arg_secret = client.api_keys["api_secret"]

        return {"http": arg_url_http, "key": arg_key, "secret": arg_secret}

    @pytest.fixture()
    def auth_invalid(self, arg_url_http: Http) -> dict:
        """Get credentials from command line args."""
        return {"http": arg_url_http, "key": BAD_CREDS, "secret": BAD_CREDS}

    @pytest.fixture()
    def auth_cls(self) -> t.Type[AuthModel]:
        """Get the class to run tests against."""
        return AuthApiKey
