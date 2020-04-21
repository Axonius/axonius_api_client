# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
from ...constants import DEFAULT_PERM, VALID_PERMS
from ...exceptions import ApiError, NotFoundError
from ..mixins import ChildMixins


class Roles(ChildMixins):
    """Child API object to work with Roles."""

    def set_default(self, name):
        """Set the default role for external users.

        Args:
            name (:obj:`str`): name of role to set as the default role for external users

        Returns:
            :obj:`dict`: metadata of default role that was set as new default
        """
        role = self.get(name=name)
        self._set_default(name=name)
        return role

    def get_default(self):
        """Get the default role for external users.

        Returns:
            :obj:`dict`: metadata of default role
        """
        name = self._get_default()
        return self.get(name=name)

    def get(self, name=None):
        """Pass."""
        roles = self._get()
        if name:
            role_names = self.get_names(roles=roles)
            if name not in role_names:
                valid = "\n" + "\n".join(role_names)
                raise NotFoundError(f"Role not found {name!r}, valid roles:{valid}")
            return [x for x in roles if x["name"] == name][0]
        return roles

    def get_names(self, roles=None):
        """Pass."""
        roles = roles if roles else self.get()
        return [x["name"] for x in roles]

    def add(
        self,
        name,
        adapters=DEFAULT_PERM,
        dashboard=DEFAULT_PERM,
        devices=DEFAULT_PERM,
        enforcements=DEFAULT_PERM,
        instances=DEFAULT_PERM,
        reports=DEFAULT_PERM,
        settings=DEFAULT_PERM,
        users=DEFAULT_PERM,
    ):
        """Pass."""
        names = self.get_names()
        if name in names:
            raise ApiError(f"Role named {name!r} already exists")

        permissions = self._check_valid_perms(
            adapters=adapters,
            dashboard=dashboard,
            devices=devices,
            enforcements=enforcements,
            instances=instances,
            reports=reports,
            settings=settings,
            users=users,
        )
        self._add(name=name, permissions=permissions)
        return self.get(name=name)

    def update(
        self,
        name,
        adapters=DEFAULT_PERM,
        dashboard=DEFAULT_PERM,
        devices=DEFAULT_PERM,
        enforcements=DEFAULT_PERM,
        instances=DEFAULT_PERM,
        reports=DEFAULT_PERM,
        settings=DEFAULT_PERM,
        users=DEFAULT_PERM,
    ):
        """Pass."""
        names = self.get_names()
        if name not in names:
            raise NotFoundError(f"Role named {name!r} does not exist")

        permissions = self._check_valid_perms(
            adapters=adapters,
            dashboard=dashboard,
            devices=devices,
            enforcements=enforcements,
            instances=instances,
            reports=reports,
            settings=settings,
            users=users,
        )
        self._update(name=name, permissions=permissions)
        return self.get(name=name)

    def delete(self, name):
        """Pass."""
        names = self.get_names()
        if name not in names:
            raise NotFoundError(f"Role named {name!r} does not exist")
        self._delete(name=name)
        return self.get()

    def _get_default(self):
        """Direct API method to get the current default role for external users.

        Returns:
            :obj:`str`: current default role for external users
        """
        path = self.router.roles_default
        return self.request(method="get", path=path, error_json_invalid=False)

    def _set_default(self, name):
        """Direct API method to set the default role for external users.

        Args:
            name (:obj:`str`): name of role to set as the default role for external users
        """
        data = {"name": name}
        path = self.router.roles_default
        return self.request(method="post", path=path, json=data)

    def _get(self):
        """Direct API method to get known roles.

        Returns:
            :obj:`list` of :obj:`str`: known roles
        """
        path = self.router.roles
        return self.request(method="get", path=path)

    def _add(self, name, permissions):
        """Direct API method to add a role.

        Args:
            name (:obj:`str`): name of new role
            permissions (:obj:`dict`): permissions for new role
        """
        data = {"name": name, "permissions": permissions}
        path = self.router.roles
        return self.request(method="put", path=path, json=data)

    def _update(self, name, permissions):
        """Direct API method to update a roles permissions.

        Args:
            name (:obj:`str`): name of role to update
            permissions (:obj:`dict`): permissions to update on new role
        """
        data = {"name": name, "permissions": permissions}
        path = self.router.roles
        return self.request(
            method="post", path=path, json=data, error_json_invalid=False
        )

    def _delete(self, name):
        """Direct API method to delete a role.

        Args:
            name (:obj:`str`): name of role to delete
        """
        data = {"name": name}
        path = self.router.roles
        return self.request(
            method="delete", path=path, json=data, error_json_invalid=False
        )

    def _check_valid_perm(self, name, value):
        """Pass."""
        if value not in VALID_PERMS:
            valids = "\n" + "\n".join(VALID_PERMS)
            msg = f"Invalid permission {value!r} for {name!r} - Must be one of:{valids}"
            raise ApiError(msg)

    def _check_valid_perms(
        self,
        adapters,
        dashboard,
        devices,
        enforcements,
        instances,
        reports,
        settings,
        users,
    ):
        """Pass."""
        self._check_valid_perm(name="adapters", value=adapters)
        self._check_valid_perm(name="dashboard", value=dashboard)
        self._check_valid_perm(name="devices", value=devices)
        self._check_valid_perm(name="enforcements", value=enforcements)
        self._check_valid_perm(name="instances", value=instances)
        self._check_valid_perm(name="reports", value=reports)
        self._check_valid_perm(name="settings", value=settings)
        self._check_valid_perm(name="users", value=users)

        return {
            "Adapters": adapters,
            "Dashboard": dashboard,
            "Devices": devices,
            "Enforcements": enforcements,
            "Instances": instances,
            "Reports": reports,
            "Settings": settings,
            "Users": users,
        }
