# -*- coding: utf-8 -*-
"""API model for unauthenticated endpoints."""
from ..constants import LOG_LEVEL_API
from ..exceptions import ResponseNotOk
from ..http import Http
from ..logs import get_obj_log
from .routers import API_VERSION, Router


class Signup:
    """API model for unauthenticated endpoints."""

    @property
    def router(self) -> Router:
        """Router for this API model."""
        return API_VERSION.signup

    @property
    def is_signed_up(self) -> bool:
        """Check if signup process has been done."""
        return self._signup_get()["signup"]

    def signup(self, password: str, company_name: str, contact_email: str) -> dict:
        """Perform the initial signup."""
        response = self._signup_post(
            password=password, company_name=company_name, contact_email=contact_email
        )

        status = response.get("status")
        message = response.get("message")
        if status == "error":
            raise ResponseNotOk(f"{message}")
        return response  # pragma: no cover

    def _signup_get(self) -> dict:
        """Get the status of initial signup."""
        response = self.http(method="get", path=self.router.root)
        return response.json()

    def _signup_post(self, password: str, company_name: str, contact_email: str) -> dict:
        """Do the initial signup."""
        data = {
            "companyName": company_name,
            "contactEmail": contact_email,
            "userName": "admin",
            "newPassword": password,
            "confirmNewPassword": password,
        }
        response = self.http(method="post", path=self.router.root, json=data)
        return response.json()

    def __init__(self, url, **kwargs):
        """Pass."""
        log_level = kwargs.get("log_level", LOG_LEVEL_API)
        self.LOG = get_obj_log(obj=self, level=log_level)
        kwargs.setdefault("certwarn", False)
        self.http = Http(url=url, **kwargs)
