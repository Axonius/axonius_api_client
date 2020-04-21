# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
from ...exceptions import ApiError, NotFoundError
from ..mixins import ChildMixins
from ..parsers.config import parse_unchanged


class Users(ChildMixins):
    """User Role controls."""

    def add(self, name, password, firstname="", lastname="", rolename=""):
        """Pass."""
        names = self.get_names()
        if name in names:
            raise ApiError(f"User named {name!r} already exists")

        if rolename:
            self.parent.roles.get(name=rolename)

        self._add(
            name=name,
            password=password,
            firstname=firstname,
            lastname=lastname,
            rolename=rolename,
        )
        return self.get(name=name)

    def get(self, name=None):
        """Pass."""
        users = self._get()
        if name:
            names = self.get_names(users=users)
            if name not in names:
                valid = "\n" + "\n".join(names)
                raise NotFoundError(f"User not found {name!r}, valid users:{valid}")
            return [x for x in users if x["user_name"] == name][0]
        return users

    def get_names(self, users=None):
        """Pass."""
        users = users if users else self.get()
        return [x["user_name"] for x in users]

    def update(self, name, firstname=None, lastname=None, password=None):
        """Pass."""
        user = self.get(name=name)

        one_of = [firstname, lastname, password]
        if not any(one_of):
            req = ", ".join(["firstname", "lastname", "password"])
            raise ApiError(f"Must supply at least one of: {req!r}")

        _, password = parse_unchanged(value=password)
        uuid = user["uuid"]

        self._update(
            uuid=uuid, firstname=firstname, lastname=lastname, password=password,
        )
        return self.get(name=name)

    def update_role(self, name, rolename):
        """Pass."""
        # XXX check if name == admin?
        user = self.get(name=name)
        role = self.parent.roles.get(name=rolename)

        uuid = user["uuid"]
        rolename = role["name"]
        permissions = role["permissions"]

        self._update_role(uuid=uuid, rolename=rolename, permissions=permissions)
        return self.get(name=name)

    def delete(self, name):
        """Pass."""
        user = self.get(name=name)
        self._delete(uuid=user["uuid"])
        return self.get()

    def _get(self, limit=None, skip=None):
        """Pass."""
        data = {}
        if limit is not None:
            data["limit"] = limit
        if skip is not None:
            data["skip"] = skip
        path = self.router.users
        return self.request(method="get", path=path, params=data)

    def _add(self, name, password, firstname="", lastname="", rolename=""):
        """Pass."""
        data = {
            "user_name": name,
            "password": password,
            "first_name": firstname,
            "last_name": lastname,
            "role_name": rolename,
        }
        path = self.router.users
        return self.request(method="put", path=path, json=data)

    def _delete(self, uuid):
        """Pass."""
        path = self.router.user.format(uuid=uuid)
        return self.request(method="delete", path=path)

    def _update(self, uuid, firstname, lastname, password):
        """Pass."""
        data = {}
        if firstname:
            data["first_name"] = firstname
        if lastname:
            data["last_name"] = lastname
        if password:
            data["password"] = password
        path = self.router.user.format(uuid=uuid)
        return self.request(
            method="post", path=path, json=data, error_json_invalid=False
        )

    def _update_role(self, uuid, rolename, permissions):
        """Pass."""
        data = {}
        data["role_name"] = rolename
        data["permissions"] = permissions
        path = self.router.user_role.format(uuid=uuid)
        return self.request(
            method="post", path=path, json=data, error_json_invalid=False
        )
