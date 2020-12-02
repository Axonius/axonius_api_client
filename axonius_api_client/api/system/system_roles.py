# -*- coding: utf-8 -*-
"""API for working with system roles."""
import copy
from typing import List, Optional

from cachetools import TTLCache, cached

from ...constants.system import Role
from ...exceptions import ApiError, NotFoundError
from ...parsers.system import parse_cat_actions, parse_roles
from ...parsers.tables import tablize_roles
from ...tools import coerce_str_to_csv, json_dump
from ..mixins import ModelMixins
from ..routers import API_VERSION, Router


class SystemRoles(ModelMixins):
    """API for working with system roles.

    Examples:
        * Get all roles: :meth:`get`
        * Get a role by name: :meth:`get_by_name`
        * Get a role by uuid: :meth:`get_by_uuid`
        * Add a role: :meth:`add`
        * Change the name of a role: :meth:`set_name`
        * Change the permissions of a role: :meth:`set_perms`
        * Delete a role: :meth:`delete_by_name`
        * Get a user readable version of the permissions for a role: :meth:`pretty_perms`
    """

    def get(self) -> List[dict]:
        """Get all roles in the system.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> roles = client.system_roles.get()
            >>> [x['name'] for x in roles]
            ['Admin', 'Viewer', 'Restricted', 'No Access', 'abc']

        """
        return parse_roles(roles=self._get())

    def get_by_name(self, name: str) -> dict:
        """Get a role by name.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> role = client.system_roles.get_by_name(name="Admin")
            >>> role["uuid"]
            '5f76721bebd8d8b5459b56c8'

        Args:
            name: name of role to get

        Raises:
            :exc:`NotFoundError`: if role not found
        """
        roles = self.get()
        found = [x for x in roles if x[Role.NAME] == name]
        if found:
            return found[0]

        err = f"Role with name of {name!r} not found"
        raise NotFoundError(tablize_roles(roles=roles, cat_actions=self.cat_actions, err=err))

    def get_by_uuid(self, uuid: str) -> dict:
        """Get a role by uuid.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> role = client.system_roles.get_by_name(name="5f76721bebd8d8b5459b56c8")
            >>> role["name"]
            'Admin'

        Args:
            uuid: uuid of role to get

        Raises:
            :exc:`NotFoundError`: if role not found
        """
        roles = self.get()
        found = [x for x in roles if x[Role.UUID] == uuid]
        if found:
            return found[0]

        err = f"Role with uuid of {uuid!r} not found"
        raise NotFoundError(tablize_roles(roles=roles, cat_actions=self.cat_actions, err=err))

    def add(self, name: str, **kwargs):
        """Add a role.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            Create a role with the default permissions (none except dashboard view)

            >>> role = client.system_roles.add(name="test1")

            Create a role with specific permissions:

            >>> role = client.system_roles.add(
            ...     name="test2", adapters="get", users_assets="get,saved_queries.run"
            ... )

            Create a role with all permissions for all categories:

            >>> role = client.system_roles.add(
            ...     name="test2",
            ...     adapters="all",
            ...     dashboard="all",
            ...     devices_assets="all",
            ...     enforcements="all",
            ...     instances="all",
            ...     reports="all",
            ...     settings="all",
            ...     users_assets="all",
            ... )

        Args:
            name: name of role to add
            **kwargs: keys as categories, values as list or CSV of actions to allow for category

        Raises:
            :exc:`ApiError`: if role already exists matching name
        """
        try:
            self.get_by_name(name=name)
            raise ApiError(f"Role with name of {name!r} already exists")
        except NotFoundError:
            pass

        perms = self.cat_actions_to_perms(grant=True, src=f"add role {name!r}", **kwargs)
        self._add(name=name, permissions=perms)
        return self.get_by_name(name=name)

    def set_name(self, name: str, new_name: str) -> dict:
        """Change the name of a role.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> role = client.system_roles.set_name(name="test1", new_name="test3")
            >>> role["name"]
            'test3'

        Args:
            name: name of role to update
            new_name: new name of role
        """
        roles = self.get()
        found_new = [x for x in roles if x[Role.NAME] == new_name]
        if found_new:
            raise ApiError(f"Role with new name {new_name!r} already exists!")

        if name == new_name:
            raise ApiError(f"New name {new_name!r} must be different than original name {name!r}")

        found = [x for x in roles if x[Role.NAME] == name]
        if not found:
            err = f"Role with name of {name!r} not found"
            raise NotFoundError(tablize_roles(roles=roles, cat_actions=self.cat_actions, err=err))

        role = found[0]
        self._check_predefined(role=role)
        self._update(uuid=role[Role.UUID], name=new_name, permissions=role[Role.PERMS])
        return self.get_by_name(name=new_name)

    def set_perms(self, name: str, grant: bool = True, **kwargs) -> dict:
        """Change the permissions of a role.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            Add all permissions for adapters to a role

            >>> role = client.system_roles.set_perms(name="test1", adapters="all")

            Remove all permissions for adapters to a role

            >>> role = client.system_roles.set_perms(name="test1", grant=False, adapters="all")

            Add all permissions for all categories to a role:

            >>> role = client.system_roles.set_perms(
            ...     name="test1",
            ...     adapters="all",
            ...     dashboard="all",
            ...     devices_assets="all",
            ...     enforcements="all",
            ...     instances="all",
            ...     reports="all",
            ...     settings="all",
            ...     users_assets="all",
            ... )

        Args:
            name: name of role to update
            grant: add or remove access to the categories and actions supplied
            **kwargs: keys as categories, values as list of actions to allow for category
        """
        role = self.get_by_name(name=name)
        self._check_predefined(role=role)
        perms_orig = role[Role.PERMS]
        perms_new = self.cat_actions_to_perms(
            role_perms=perms_orig, grant=grant, src=f"set permissions on role {name!r}", **kwargs
        )
        if perms_orig == perms_new:
            err = f"No permission changes for role {name!r}"
            supplied = f"Supplied changes: {json_dump(kwargs)}"
            pretty_perms = self.pretty_perms(role=role)
            raise ApiError("\n".join([err, pretty_perms, "", err, supplied]))
        self._update(uuid=role[Role.UUID], name=name, permissions=perms_new)
        return self.get_by_name(name=name)

    def delete_by_name(self, name: str) -> dict:
        """Delete a role.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> role = client.system_roles.delete_by_name(name="test1")

        Args:
            name: name of role to delete
        """
        role = self.get_by_name(name=name)
        self._check_predefined(role=role)
        self._delete(uuid=role[Role.UUID])
        return role

    def pretty_perms(self, role: dict) -> str:
        """Get a user readable version of the permissions for a role.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            Pretty print a roles permission sets:

            >>> print(client.system_roles.pretty_perms(role=role))
            adapters             Adapters
            connections.delete   Delete connection              False
            connections.post     Edit connections               False
            (...trimmed...)

        Args:
            role: role returned from :meth:`get_by_name`, :meth:`get`, or :meth:`get_by_uuid`
        """
        lines = []
        role_perms = role[Role.PERMS_FLAT]
        cats = self.cat_actions[Role.CATS]
        acts = self.cat_actions[Role.ACTS]
        lens = self.cat_actions[Role.LENS]
        len_acts = lens[Role.ACTS]
        len_acts_desc = lens[Role.ACTS_DESC]

        for category, actions in acts.items():
            cat_desc = cats[category]
            cat_role_acts = role_perms[category]
            lines += ["", "-" * 70, f"{category:<{len_acts + 2}} {cat_desc}"]
            for action, action_desc in actions.items():
                cat_role_act = cat_role_acts[action]
                lines.append(
                    f"  {action:<{len_acts}} {action_desc:<{len_acts_desc}} {cat_role_act}"
                )
        return "\n".join(lines)

    def _get(self):
        """Direct API method to get all roles."""
        path = self.router.roles
        return self.request(method="get", path=path)

    def _add(self, name, permissions):
        """Direct API method to add a role.

        Args:
            name: name of new role
            permissions: permissions for new role
        """
        data = {"name": name, "permissions": permissions}
        path = self.router.roles
        return self.request(method="put", path=path, json=data)

    def _update(self, uuid, name, permissions):
        """Direct API method to update a roles permissions.

        Args:
            name: name of role to update
            permissions: permissions to update on new role
        """
        data = {"name": name, "permissions": permissions, "uuid": uuid}
        path = self.router.roles_by_uuid.format(uuid=uuid)
        return self.request(method="post", path=path, json=data, error_json_invalid=False)

    def _delete(self, uuid):
        """Direct API method to delete a role.

        Args:
            name: name of role to delete
        """
        path = self.router.roles_by_uuid.format(uuid=uuid)
        return self.request(method="delete", path=path, error_json_invalid=False)

    def _get_labels(self):
        """Direct API method to get role labels."""
        path = self.router.roles_labels
        return self.request(method="get", path=path)

    @property
    def router(self) -> Router:
        """Router for this API model."""
        return API_VERSION.system

    @property
    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def cat_actions(self) -> dict:
        """Get permission categories and their actions."""
        data = parse_cat_actions(raw=self._get_labels())
        if not self.instances.has_cloud_compliance:  # pragma: no cover
            data[Role.CATS].pop(Role.COMP)
            data[Role.ACTS].pop(Role.COMP)
        return data

    def _check_predefined(self, role: dict):
        """Check if a role is predefined.

        Args:
            role: role to check

        Raises:
            :exc:`ApiError`: if role is a predefined role
        """
        name = role["name"]
        uuid = role["uuid"]
        predefined = role.get("predefined", False)
        if predefined:
            raise ApiError(f"Unable to change predefined role {name!r} with uuid {uuid!r}")

    def cat_actions_to_perms(
        self,
        role_perms: Optional[dict] = None,
        grant: bool = True,
        src: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Create an updated set of role permissions based on categories and actions.

        Args:
            role_perms: permissions of a role to update
            grant: add or remove access to the actions supplied
            **kwargs: keys as categories, values as list of actions to allow for category
        """

        def add(value, overwrite):
            """Add an action for a category to the role perms."""
            if category not in role_perms:
                role_perms[category] = {}

            if "." in action:
                sub_category, sub_action = action.split(".", 1)
                if sub_category not in role_perms[category]:
                    role_perms[category][sub_category] = {}
                if sub_action not in role_perms[category][sub_category] or overwrite:
                    self.LOG.debug(f"{src} category {category!r} action {action!r} to {value}")
                    role_perms[category][sub_category][sub_action] = value
            else:
                if action not in role_perms[category] or overwrite:
                    self.LOG.debug(f"{src} category {category!r} action {action!r} to {value}")
                    role_perms[category][action] = value

        cats = self.cat_actions[Role.CATS]
        acts = self.cat_actions[Role.ACTS]

        role_perms = role_perms or {}
        role_perms = copy.deepcopy(role_perms)

        for category, actions in acts.items():
            for action in actions:
                add(value=False, overwrite=False)

        for category, actions in kwargs.items():
            if category not in cats:
                valid = [f"{k}: {v}" for k, v in cats.items()]
                valid = "\n - " + "\n - ".join(valid)
                raise ApiError(f"Invalid category {category!r}, valid:{valid}")

            actions = coerce_str_to_csv(value=actions)
            cat_acts = acts[category]

            if Role.ALL in actions:
                for action in cat_acts:
                    add(value=grant, overwrite=True)
                continue

            for action in actions:
                if action not in cat_acts:
                    valid = [f"{k}: {v}" for k, v in cat_acts.items()]
                    valid = "\n - " + "\n - ".join(valid)
                    raise ApiError(
                        f"Invalid action {action!r} for category {category!r}, valid:{valid}"
                    )

                add(value=grant, overwrite=True)
        return role_perms

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        from .instances import Instances

        self.instances: Instances = Instances(auth=self.auth)
        """Work with instances"""
