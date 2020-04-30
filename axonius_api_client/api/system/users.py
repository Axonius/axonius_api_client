# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
from ...exceptions import ApiError, NotFoundError
from ..mixins import ChildMixins
from ..parsers.config import parse_unchanged


class Users(ChildMixins):
    """User Role controls."""

    def add(
        self, name, password, role_name, first_name=None, last_name=None, email=None,
    ):
        """Pass."""
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
        self._add(user=user)
        return self.get_by_name(name=name)

    def get(self):
        """Pass."""
        users = self._get()
        roles = self.parent.roles.get()
        for user in users:
            for role in roles:
                if role["uuid"] == user["role_id"]:
                    user["role_obj"] = role
                    break

        return users

    def get_by_name(self, name):
        """Pass."""
        users = self.get()

        valid = [x["user_name"] for x in users]

        if name not in valid:
            valid = "\n" + "\n".join(valid)
            raise NotFoundError(f"User name {name!r} not found, valid users:{valid}")

        return [x for x in users if x["user_name"] == name][0]

    def update(
        self,
        name,
        first_name=None,
        last_name=None,
        password=None,
        email=None,
        role_name=None,
    ):
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

    def delete(self, name):
        """Pass."""
        user = self.get_by_name(name=name)
        return self._delete(uuid=user["uuid"])

    def _get(self, limit=None, skip=None):
        """Pass."""
        data = {}

        if limit is not None:
            data["limit"] = limit

        if skip is not None:
            data["skip"] = skip

        path = self.router.users
        return self.request(method="get", path=path, params=data)

    def _add(self, user):
        """Pass."""
        path = self.router.users
        return self.request(method="put", path=path, json=user)

    def _delete(self, uuid):
        """Pass."""
        path = self.router.user.format(uuid=uuid)
        return self.request(method="delete", path=path)

    def _update(self, uuid, user):
        """Pass."""
        path = self.router.user.format(uuid=uuid)
        return self.request(
            method="post", path=path, json=user, error_json_invalid=False
        )
