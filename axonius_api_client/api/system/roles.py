# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
from ...constants import DEFAULT_PERM, VALID_PERMS
from ...exceptions import ApiError, NotFoundError
from ...tools import listify
from ..mixins import ChildMixins

ROLE_ACTIONS = [
    "delete",
    "post",
    "put",
    "run",
    "run_manual_discovery",
    "reset_api_key",
    "get_users_and_roles",
    "get",
    "post",
    "put",
    "run",
]


def parse_roles_labels(raw, role=None):
    """Pass."""
    # raw = {k.split(".")[1:]: v for k, v in raw.items()}
    # permissions = (role or {}).get("permissions", {})
    parsed = {}
    # parsed = {
    #     k[0]: {"actions": {}, "description": v, "parent": None}
    #     for k, v in raw.items()
    #     if len(k) == 1
    # }

    for perm, desc in raw.items():
        items = perm.split(".")[1:]
        category = items.pop(0)
        if not items:
            print(category)
            parsed[category] = {"actions": {}, "description": desc, "parent": None}

    # for perm, description in raw.items():
    #     items = perm.split(".")[1:]
    #     category = items.pop(0)
    #     category_perms = permissions.get(category, {})
    #     parsed[category] = parsed.get(
    #         category, {"actions": {}, "description": None, "parent": None}
    #     )

    #     if not items:
    #         parsed[category]["description"] = description
    #         continue

    #     action = items.pop(0)

    #     if action in ROLE_ACTIONS:
    #         parsed[category]["actions"][action] = {
    #             "description": description,
    #             "value": category_perms.get(action, False),
    #         }
    #         continue

    #     section = action
    #     section_perms = category_perms.get(section, {})

    #     parsed[section] = parsed.get(
    #         section,
    #         {
    #             "actions": {},
    #             "parent": category,
    #             "description": f"Section under {category}",
    #         },
    #     )

    #     if items:
    #         section_action = items.pop(0)

    #         if section_action in ROLE_ACTIONS:
    #             parsed[section]["actions"] = {
    #                 "description": description,
    #                 "value": section_perms.get(section_action, False),
    #             }

    return parsed


class Roles(ChildMixins):
    """Child API object to work with Roles."""

    def get_categories(self, role=None):
        """Pass."""
        labels = self._get_labels()
        return parse_roles_labels(raw=labels, role=role)

    def get(self):
        """Pass."""
        roles = self._get()
        return roles

    def get_by_name(self, name):
        """Pass."""
        roles = self.get()

        valid = [x["name"] for x in roles]

        if name not in valid:
            valid = "\n" + "\n".join(valid)
            raise NotFoundError(f"Role name {name!r} not found, valid roles:{valid}")

        return [x for x in roles if x["name"] == name][0]

    def get_by_uuid(self, uuid):
        """Pass."""
        roles = self.get()

        valid = [x["uuid"] for x in roles]

        if uuid not in valid:
            valid = "\n" + "\n".join(valid)
            raise NotFoundError(f"Role uuid {uuid!r} not found, valid roles:{valid}")

        return [x for x in roles if x["uuid"] == uuid][0]

    def validate_perms(self, **kwargs):
        """Pass."""
        perms = self.get_categories()

        for category, actions in kwargs.items():
            if category not in perms:
                valid = "\n" + "\n".join(list(perms))
                raise NotFoundError(f"Category {category!r} not found, valid: {valid}")
            actions = listify(actions)

    def add(self, name, **kwargs):
        """Pass."""
        roles = self.get()
        names = [x["user_name"] for x in roles]

        if name in names:
            raise ApiError(f"Role named {name!r} already exists")

        permissions = {}

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
        # role = self.get_by_name(name=name)

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

    # XXX predefined
    def delete(self, name):
        """Pass."""
        role = self.get_by_name(name=name)

        if role.get("predefined"):
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

    def _delete(self, uuid):
        """Direct API method to delete a role.

        Args:
            name (:obj:`str`): name of role to delete
        """
        path = self.router.roles_by_uuid.format(uuid=uuid)
        return self.request(method="delete", path=path, error_json_invalid=False)

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

    def _get_labels(self):
        """Pass."""
        path = self.router.roles_labels
        return self.request(method="get", path=path)
