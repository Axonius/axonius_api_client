# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
from typing import List, Optional

from ...exceptions import ApiError, NotFoundError
from ..mixins import ChildMixins
from ..parsers.config import parse_unchanged


class Users(ChildMixins):
    """User Role controls."""

    def add(
        self,
        name: str,
        role_name: str,
        password: Optional[str] = None,
        generate_password_link: bool = False,
        email_password_link: bool = False,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> dict:
        """Pass."""
        if not any([password, generate_password_link, email_password_link]):
            raise ApiError(
                "Must supply password, generate_password_link, or email_password_link"
            )

        if email_password_link and not email:
            raise ApiError("Must supply email if email_password_link is True")

        role = self.parent.roles.get_by_name(name=role_name)
        users = self.get()

        names = [x["user_name"] for x in users]

        if name in names:
            raise ApiError(f"User named {name!r} already exists")

        user = {}
        user["user_name"] = name
        user["first_name"] = first_name
        user["last_name"] = last_name
        user["password"] = password
        user["email"] = email
        user["role_id"] = role["uuid"]
        user["role_obj"] = role
        user["auto_generated_password"] = generate_password_link
        self._add(user=user)
        user_obj = self.get_by_name(name=name)

        if generate_password_link or email_password_link:
            password_reset_link = self._get_password_reset_link(uuid=user_obj["uuid"])
            if generate_password_link:
                user_obj["password_reset_link"] = password_reset_link

        if email_password_link:
            try:
                self._email_password_reset_link(
                    uuid=user_obj["uuid"], email=email, new_user=True
                )
                user_obj["email_password_link_error"] = None
            except Exception as exc:
                user_obj["email_password_link_error"] = (
                    getattr(getattr(exc, "response", None), "text", None) or exc
                )

        return user_obj

    def get(self) -> List[dict]:
        """Pass."""
        users = self._get()
        roles = self.parent.roles.get()
        for user in users:
            for role in roles:
                if role["uuid"] == user["role_id"]:
                    user["role_obj"] = role
                    break

        return users

    def get_by_name(self, name: str) -> dict:
        """Pass."""
        users = self.get()

        valid = [x["user_name"] for x in users]

        if name not in valid:
            valid = "\n" + "\n".join(valid)
            raise NotFoundError(f"User name {name!r} not found, valid users:{valid}")

        return [x for x in users if x["user_name"] == name][0]

    def update(
        self,
        name: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        password: Optional[str] = None,
        email: Optional[str] = None,
        role_name: Optional[str] = None,
    ) -> dict:
        """Pass."""
        user = self.get_by_name(name=name)

        one_of = [first_name, last_name, password, email, role_name]

        if all([x is None for x in one_of]):
            req = ", ".join(
                ["first_name", "last_name", "password", "email", "role_name"]
            )
            raise ApiError(f"Must supply at least one of: {req!r}")

        uuid = user["uuid"]

        if first_name is not None:
            user["first_name"] = first_name

        if last_name is not None:
            user["last_name"] = last_name

        if password is not None:
            _, password = parse_unchanged(value=password)
            user["password"] = password

        if email is not None:
            user["email"] = email

        if role_name is not None:
            role = self.parent.roles.get_by_name(name=role_name)
            user["role_id"] = role["uuid"]
            user["role_obj"] = role

        self._update(uuid=uuid, user=user)
        return self.get_by_name(name=name)

    def delete(self, name: str) -> str:
        """Pass."""
        user = self.get_by_name(name=name)
        return self._delete(uuid=user["uuid"])

    def get_password_reset_link(self, name: str) -> str:
        """Pass."""
        user = self.get_by_name(name=name)
        user["password_reset_link"] = self._get_password_reset_link(uuid=user["uuid"])
        return user

    def email_password_reset_link(
        self,
        name: str,
        email: Optional[str] = None,
        new_user: bool = False,
        generate_first: bool = True,
    ) -> str:
        """Pass."""
        user = self.get_by_name(name=name)
        user_email = user.get("email")
        email = email or user_email

        if not email:
            raise ApiError("User has no email address defined, must supply email")

        if generate_first:
            user["password_reset_link"] = self._get_password_reset_link(
                uuid=user["uuid"]
            )

        self._email_password_reset_link(uuid=user["uuid"], email=email, new_user=False)
        return email

    def _get(
        self, limit: Optional[int] = None, skip: Optional[int] = None
    ) -> List[dict]:
        """Pass."""
        data = {}

        if limit is not None:
            data["limit"] = limit

        if skip is not None:
            data["skip"] = skip

        path = self.router.users
        return self.request(method="get", path=path, params=data)

    def _add(self, user: dict) -> str:
        """Pass."""
        path = self.router.users
        return self.request(method="put", path=path, json=user)

    def _delete(self, uuid: str) -> str:
        """Pass."""
        path = self.router.user.format(uuid=uuid)
        return self.request(method="delete", path=path)

    def _update(self, uuid: str, user: dict) -> str:
        """Pass."""
        path = self.router.user.format(uuid=uuid)
        return self.request(
            method="post", path=path, json=user, error_json_invalid=False
        )

    def _get_password_reset_link(self, uuid: str) -> str:
        """Pass."""
        path = f"{self.router._base}/tokens/reset"
        data = {"user_id": uuid}
        return self.request(method="put", path=path, json=data, error_json_invalid=False)

    def _email_password_reset_link(
        self, uuid: str, email: str, new_user: bool = False
    ) -> str:
        """Pass."""
        path = f"{self.router._base}/tokens/notify"
        data = {"user_id": uuid, "email": email, "invite": new_user}
        return self.request(method="POST", path=path, json=data)
