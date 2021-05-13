# -*- coding: utf-8 -*-
"""API for working with system roles."""
import copy
from typing import Generator, List, Optional, Union

from ...exceptions import ApiError, NotFoundError
from ...parsers.tables import tablize_roles
from ...tools import coerce_str_to_csv, json_dump
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..mixins import ModelMixins


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

    @staticmethod
    def _parse_cat_actions(raw: dict) -> dict:
        """Parse the permission labels into a layered dict."""
        return json_api.system_roles.parse_cat_actions(raw=raw)

    def get(self, generator: bool = False) -> Union[Generator[dict, None, None], List[dict]]:
        """Get Axonius system roles.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> roles = client.system_roles.get()
            >>> [x['name'] for x in roles]
            ['Admin', 'Viewer', 'Restricted', 'No Access', 'abc']

        Args:
            generator: return an iterator for objects that will yield rows as they are fetched

        """
        gen = self.get_generator()
        return gen if generator else list(gen)

    def get_generator(self) -> Generator[dict, None, None]:
        """Get Axonius system roles using a generator."""
        rows = self._get()
        for row in rows:
            yield row.to_dict_old()

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
        found = [x for x in roles if x["name"] == name]
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
        found = [x for x in roles if x["uuid"] == uuid]
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
        found_new = [x for x in roles if x["name"] == new_name]
        if found_new:
            raise ApiError(f"Role with new name {new_name!r} already exists!")

        if name == new_name:
            raise ApiError(f"New name {new_name!r} must be different than original name {name!r}")

        found = [x for x in roles if x["name"] == name]
        if not found:
            err = f"Role with name of {name!r} not found"
            raise NotFoundError(tablize_roles(roles=roles, cat_actions=self.cat_actions, err=err))

        role = found[0]
        self._check_predefined(role=role)
        self._update(uuid=role["uuid"], name=new_name, permissions=role["permissions"])
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
        perms_orig = role["permissions"]
        perms_new = self.cat_actions_to_perms(
            role_perms=perms_orig, grant=grant, src=f"set permissions on role {name!r}", **kwargs
        )

        if perms_orig == perms_new:
            err = f"No permission changes for role {name!r}"
            supplied = f"Supplied changes: {json_dump(kwargs)}"
            pretty_perms = self.pretty_perms(role=role)
            raise ApiError("\n".join([err, pretty_perms, "", err, supplied]))
        self._update(uuid=role["uuid"], name=name, permissions=perms_new)
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
        self._delete(uuid=role["uuid"])
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
        role_perms = role["permissions_flat"]
        cat_actions = self.cat_actions
        cats = cat_actions["categories"]
        acts = cat_actions["actions"]
        lens = cat_actions["lengths"]
        len_acts = lens["actions"]
        len_acts_desc = lens["actions_desc"]

        for category, actions in acts.items():
            if category not in role_perms:
                continue

            cat_desc = cats[category]
            cat_role_acts = role_perms[category]
            lines += ["", "-" * 70, f"{category:<{len_acts + 2}} {cat_desc}"]
            for action, action_desc in actions.items():
                cat_role_act = cat_role_acts[action]
                lines.append(
                    f"  {action:<{len_acts}} {action_desc:<{len_acts_desc}} {cat_role_act}"
                )
        return "\n".join(lines)

    def _get(self) -> List[json_api.system_roles.SystemRole]:
        """Direct API method to get all users.

        Args:
            limit: limit to N rows per page
            offset: start at row N
        """
        api_endpoint = ApiEndpoints.system_roles.get
        return api_endpoint.perform_request(http=self.auth.http)

    def _add(self, name: str, permissions: dict) -> json_api.system_roles.SystemRole:
        """Direct API method to add a role.

        Args:
            name: name of new role
            permissions: permissions for new role
        """
        api_endpoint = ApiEndpoints.system_roles.create
        request_obj = api_endpoint.load_request(name=name, permissions=permissions)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _update(self, uuid: str, name: str, permissions: dict) -> json_api.system_roles.SystemRole:
        """Direct API method to update a roles permissions.

        Args:
            name: name of role to update
            permissions: permissions to update on new role
        """
        api_endpoint = ApiEndpoints.system_roles.update
        request_obj = api_endpoint.load_request(name=name, permissions=permissions, uuid=uuid)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _delete(self, uuid: str) -> json_api.system_roles.SystemRole:
        """Direct API method to delete a role.

        Args:
            name: name of role to delete
        """
        api_endpoint = ApiEndpoints.system_roles.delete
        request_obj = api_endpoint.load_request(uuid=uuid)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _get_labels(self) -> dict:
        """Direct API method to get role labels."""
        api_endpoint = ApiEndpoints.system_roles.perms
        return api_endpoint.perform_request(http=self.auth.http)

    @property
    def cat_actions(self) -> dict:
        """Get permission categories and their actions."""
        return json_api.system_roles.cat_actions(http=self.auth.http)

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

        cats = self.cat_actions["categories"]
        acts = self.cat_actions["actions"]

        role_perms = role_perms or {}
        role_perms = copy.deepcopy(role_perms)

        for category, actions in acts.items():
            for action in actions:
                add(value=False, overwrite=False)

        for category, actions in kwargs.items():
            category = category.lower()
            if category not in cats:
                valid = [f"{k}: {v}" for k, v in cats.items()]
                valid = "\n - " + "\n - ".join(valid)
                raise ApiError(f"Invalid category {category!r}, valid:{valid}")

            actions = coerce_str_to_csv(value=actions)
            actions = [x.lower().strip() for x in actions]
            cat_acts = acts[category]

            if "all" in actions:
                for action in cat_acts:
                    add(value=grant, overwrite=True)
                continue

            if "none" in actions:
                for action in cat_acts:
                    add(value=False, overwrite=True)
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
