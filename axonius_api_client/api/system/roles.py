# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
import re

from ...exceptions import ApiError, NotFoundError
from ...tools import join_kv, longest_str, split_str
from ..mixins import ChildMixins
from ..parsers.roles import parse_permissions


class Roles(ChildMixins):
    """Child API object to work with Roles."""

    @property
    def permissions(self):
        """Pass."""
        if hasattr(self, "_permissions"):
            return self._permissions

        raw = self._get_labels()
        self._permissions = parse_permissions(raw=raw)
        return self._permissions

    def map_role_perms(self, role):
        """Pass."""
        perms = []

        for category, actions in role["permissions"].items():
            for action, action_value in actions.items():
                if not isinstance(action_value, dict):
                    perm = ".".join([category, action])
                    perm_obj = {
                        "role": role["name"],
                        "permission": perm,
                        "description": self.permissions[perm],
                        "value": action_value,
                    }
                    perms.append(perm_obj)
                    continue

                for sub_action, sub_action_value in action_value.items():
                    perm = ".".join([category, action, sub_action])
                    perm_obj = {
                        "role": role["name"],
                        "permission": perm,
                        "description": self.permissions[perm],
                        "value": sub_action_value,
                    }
                    perms.append(perm_obj)

        return sorted(perms, key=lambda x: x["permission"])

    def find_perm(self, perm):
        """Pass."""
        if not perm:
            return []

        matches = [x for x in self.permissions if re.match(perm, x, re.I)]

        if not matches:
            longest = longest_str(obj=self.permissions)
            tmpl = f"{{k:<{longest}}} {{v}}"
            valid = "\n  " + "\n  ".join(join_kv(obj=self.permissions, tmpl=tmpl))
            msg = f"Invalid permission supplied: {perm!r}"
            msg = f"{msg}\nValid permissions: {valid}\n\n{msg}"
            raise NotFoundError(msg)

        return list(set(matches))

    def _map_perm_role(self, perm, value, perms):
        """Pass."""
        if not perm:
            return perms

        perm_split = perm.split(".")
        category = perm_split.pop(0)

        if category not in perms:
            perms[category] = {}

        action = perm_split.pop(0)

        if perm_split:
            sub_action = perm_split.pop(0)

            if action not in perms[category]:
                perms[category][action] = {}

            if sub_action not in perms[category][action]:
                perms[category][action][sub_action] = value
        else:
            if action not in perms[category]:
                perms[category][action] = value

        return perms

    def map_perms_role(self, allow="", deny="", default=False, role=None):
        """Pass."""
        perms = {}

        deny_perms = [y for x in split_str(obj=deny) for y in self.find_perm(perm=x)]
        allow_perms = [y for x in split_str(obj=allow) for y in self.find_perm(perm=x)]

        for perm in deny_perms:
            self._map_perm_role(perm=perm, value=False, perms=perms)

        for perm in allow_perms:
            self._map_perm_role(perm=perm, value=True, perms=perms)

        if role:
            for perm in role["perms"]:
                self._map_perm_role(
                    perm=perm["permission"], value=perm["value"], perms=perms
                )

        for perm in self.permissions:
            self._map_perm_role(perm=perm, value=default, perms=perms)

        return perms

    def get(self):
        """Pass."""
        roles = self._get()
        for role in roles:
            role["perms"] = self.map_role_perms(role=role)
        return roles

    def get_by_name(self, name):
        """Pass."""
        roles = self.get()

        valid = [x["name"] for x in roles]

        if name not in valid:
            valid = "\n  " + "\n  ".join(valid)
            raise NotFoundError(f"Role name {name!r} not found, valid roles:{valid}")

        role = [x for x in roles if x["name"] == name][0]
        return role

    def get_by_uuid(self, uuid):
        """Pass."""
        roles = self.get()

        valid = [x["uuid"] for x in roles]

        if uuid not in valid:
            valid = "\n" + "\n".join(valid)
            raise NotFoundError(f"Role uuid {uuid!r} not found, valid roles:{valid}")

        role = [x for x in roles if x["uuid"] == uuid][0]
        return role

    def add(self, name, allow="", deny="", default=False):
        """Pass."""
        roles = self.get()
        names = [x["name"] for x in roles]

        if name in names:
            raise ApiError(f"Role named {name!r} already exists")

        permissions = self.map_perms_role(allow=allow, deny=deny, default=default)
        self._add(name=name, permissions=permissions)
        return self.get_by_name(name=name)

    def update(self, name, allow="", deny=""):
        """Pass."""
        role = self.get_by_name(name=name)

        if role.get("predefined", False):
            raise ApiError(f"Not allowed to update predefined role {name!r}")

        perms = self.map_perms_role(allow=allow, deny=deny, role=role)

        self._update(uuid=role["uuid"], name=role["name"], permissions=perms)
        return self.get_by_name(name=name)

    def delete(self, name):
        """Pass."""
        role = self.get_by_name(name=name)

        if role.get("predefined", False):
            raise ApiError(f"Not allowed to delete predefined role {name!r}")

        return self._delete(uuid=role["uuid"])

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

    def _update(self, uuid, name, permissions):
        """Direct API method to update a roles permissions.

        Args:
            name (:obj:`str`): name of role to update
            permissions (:obj:`dict`): permissions to update on new role
        """
        data = {"name": name, "permissions": permissions, "uuid": uuid}
        path = self.router.roles_by_uuid.format(uuid=uuid)
        return self.request(
            method="post", path=path, json=data, error_json_invalid=False
        )

    def _delete(self, uuid):
        """Direct API method to delete a role.

        Args:
            name (:obj:`str`): name of role to delete
        """
        path = self.router.roles_by_uuid.format(uuid=uuid)
        return self.request(method="delete", path=path, error_json_invalid=False)

    def _get_labels(self):
        """Pass."""
        path = self.router.roles_labels
        return self.request(method="get", path=path)
