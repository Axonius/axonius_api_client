# -*- coding: utf-8 -*-
"""API for working with system users."""
from typing import List, Optional, Tuple, Union

from ...constants.system import Role, User
from ...exceptions import ApiError, NotFoundError
from ...parsers.system import parse_user
from ...parsers.tables import tablize_users
from ..mixins import ModelMixins
from ..routers import API_VERSION, Router


class SystemUsers(ModelMixins):
    """API for working with system users."""

    def get(self) -> List[dict]:
        """Get all users in the system.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> users = client.system_users.get()
            >>> [x['user_name'] for x in users]
            ['admin']

        """
        users = self._get()
        for user in users:
            role_obj = self.roles.get_by_uuid(uuid=user[User.ROLE_ID])
            parse_user(user=user, role_obj=role_obj)
        return users

    def get_by_name(self, name: str) -> dict:
        """Get a user by name.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> user = client.system_users.get_by_name(name="admin")
            >>> user["uuid"]
            '5f76721bebd8d8b5459b56c8'

        Args:
            name: user name

        Raises:
            :exc:`NotFoundError`: if user not found
        """
        users = self.get()
        found = [x for x in users if x[User.NAME] == name]
        if found:
            return found[0]

        err = f"User with name of {name!r} not found"
        raise NotFoundError(tablize_users(users=users, err=err))

    def get_by_uuid(self, uuid: str) -> dict:
        """Get a user by uuid.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> user = client.system_users.get_by_uuid(uuid="5f76721bebd8d8b5459b56cc")
            >>> user["name"]
            'administrator'

        Args:
            uuid: uuid

        Raises:
            :exc:`NotFoundError`: if user not found
        """
        users = self.get()
        found = [x for x in users if x[User.UUID] == uuid]
        if found:
            return found[0]

        err = f"User with uuid of {uuid!r} not found"
        raise NotFoundError(tablize_users(users=users, err=err))

    def add(
        self,
        name: str,
        password: str,
        role_name: str,
        first: Optional[str] = None,
        last: Optional[str] = None,
        email: Optional[str] = None,
    ) -> dict:
        """Create a user.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            Create a user with the Admin role

            >>> user = client.system_users.add(
            ...     name="test1",
            ...     password="test1",
            ...     role_name="Admin",
            ...     first="bad",
            ...     last="wolf",
            ...     email="badwolf@badwolf.com",
            ... )
            >>> user['uuid']
            '5f7ca7f1e4557d5cba415f12'

        Args:
            name: user name
            password: password
            role_name: role name
            first: first name
            last: last name
            email: email address

        Raises:
            :exc:`ApiError`: if user already exists matching name
        """
        role = self.roles.get_by_name(name=role_name)
        try:
            self.get_by_name(name=name)
            raise ApiError(f"User with name of {name!r} already exists")
        except NotFoundError:
            pass

        self._add(
            user_name=name,
            role_id=role[Role.UUID],
            password=password,
            first=first,
            last=last,
            email=email,
        )
        return self.get_by_name(name=name)

    def set_role(self, name: str, role_name: str) -> dict:
        """Change the role of a user.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> user = client.system_users.set_role(name='test1', role_name='Viewer')
            >>> user['role_name']
            'Viewer'

        Args:
            name: user name
            role_name: name of role
        """
        role = self.roles.get_by_name(name=role_name)
        return self._update_user_attr(
            name=name, must_be_internal=True, attr=User.ROLE_ID, value=role[Role.UUID]
        )

    def set_first_last(self, name: str, first: str, last: str) -> dict:
        """Change the first and last name of a user.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> user = client.system_users.set_first_last(name='test1', first='Bad', last='Wolf')
            >>> user['first_name']
            'Bad'
            >>> user['last_name']
            'Wolf'
            >>> user['full_name']
            'Bad Wolf'

        Args:
            name: user name
            first: first name
            last: last name
        """
        value = {User.FIRST_NAME: first, User.LAST_NAME: last}
        attr = f"{User.FIRST_NAME} and {User.LAST_NAME}"
        return self._update_user_attr(name=name, must_be_internal=True, attr=attr, value=value)

    def set_password(self, name: str, password: str) -> dict:
        """Change the password for a user.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> user = client.system_users.set_password(name='test1', password='super_secure')

        Args:
            name: user name
            password: password
        """
        return self._update_user_attr(
            name=name, must_be_internal=True, attr=User.PASSWORD, value=password
        )

    def set_email(self, name: str, email: str) -> dict:
        """Change the email address for a user.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> user = client.system_users.set_email(name='test1', email='bad@wolf.com')
            >>> user['email']
            'bad@wolf.com'

        Args:
            name: user name
            email: email
        """
        return self._update_user_attr(
            name=name, must_be_internal=True, attr=User.EMAIL, value=email
        )

    def set_ignore_role_assignment_rules(self, name: str, enabled: bool) -> dict:
        """Set the ignore role assignment rules flag of an external user.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> user = client.system_users.set_ignore_role_assignment_rules(
            ...     name='test1', enabled=True
            ... )

        Args:
            name: user name
            enabled: enable/disable the flag
        """
        return self._update_user_attr(
            name=name, must_be_internal=False, attr=User.IGNORE_RULES, value=enabled
        )

    def delete_by_name(self, name: str) -> str:
        """Delete a user by name.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> client.system_users.delete_by_name(name='test1')

        Args:
            name: user name

        Raises:
            :exc:`ApiError`: if name is "admin"
        """
        if name == User.ADMIN_NAME:
            raise ApiError(f"Unable to delete {name!r} user")

        user = self.get_by_name(name=name)
        return self._delete(uuid=user["uuid"])

    def get_password_reset_link(self, name: str) -> str:
        """Generate a password reset link for a user.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> link = client.system_users.get_password_reset_link(name='test1')
            >>> link
            'https://10.20.0.61/login?token=LUayznSkfLUjm3A2fIs_zAF-4CzcxRZc7DHOfhOkMRI'

        Notes:
            This link can be provided to the user and they can browse to it, or they can use
            ``axonshell tools axonshell tools use-password-reset-token`` or use
            :meth:`axonius_api_client.api.system.signup.Signup.use_password_reset_token`

        Args:
            name: user name

        """
        user = self.get_by_name(name=name)
        return self._tokens_generate(uuid=user[User.UUID])

    def email_password_reset_link(
        self,
        name: str,
        email: Optional[str] = None,
        for_new_user: bool = False,
    ) -> Tuple[str, str]:
        """Email a password reset link for a user.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            Use the email address defined in the users account

            >>> link, email_used = client.system_users.email_password_reset_link(name='test1')
            >>> link
            'https://10.20.0.61/login?token=V-YW8DnCverKTgvsToMAJwGPqXtQQeeNuBFkN4dE4ew'
            >>> email_used
            'jim@badwolf.com'

            Use a custom email address

            >>> link, email_used = client.system_users.email_password_reset_link(
            ...     name='test1', email='james@badwolf.com'
            ... )
            >>> link
            'https://10.20.0.61/login?token=V-YW8DnCverKTgvsToMAJwGPqXtQQeeNuBFkN4dE4ew'
            >>> email_used
            'james@badwolf.com'

            Use the template for a new user instead of password reset

            >>> link, email_used = client.system_users.email_password_reset_link(
            ...     name='test1', email='james@badwolf.com', for_new_user=True
            ... )

        Notes:
            This returns the password reset link like :meth:`get_password_reset_link` and the email
            address that was used to send the email.

        Args:
            name: user name
            email: use a custom email address to send the email instead of the users defined email
                address. required if the user has no defined email address.
            for_new_user: use the new user email template instead of the password reset email
                template

        """
        user = self.get_by_name(name=name)
        email = email or user.get("email")
        uuid = user[User.UUID]

        if not email:
            raise ApiError(
                f"User {name!r} has no email address defined, must supply a custom email address"
            )

        link = self._tokens_generate(uuid=uuid)
        self._tokens_notify(uuid=uuid, email=email, invite=for_new_user)
        return link, email

    def _get(self, limit: Optional[int] = None, skip: Optional[int] = None) -> List[dict]:
        """Direct API method to get all users.

        Args:
            limit: limit to N rows per page
            skip: start at row N
        """
        data = {}

        if limit is not None:
            data["limit"] = limit

        if skip is not None:
            data["skip"] = skip

        path = self.router.users
        return self.request(method="get", path=path, params=data)

    def _add(
        self,
        user_name: str,
        role_id: str,
        password: Optional[str] = None,
        auto_generated_password: bool = False,
        first: Optional[str] = None,
        last: Optional[str] = None,
        email: Optional[str] = None,
    ) -> str:
        """Direct API method to add a user.

        Args:
            user_name: user name
            password: password
            role_id: role UUID
            first: first name
            last: last name
            email: email address
            auto_generated_password: generate a password (unused!)
        """
        user = {}
        user["user_name"] = user_name
        user["first_name"] = first
        user["last_name"] = last
        user["password"] = password
        user["email"] = email
        user["role_id"] = role_id
        user["auto_generated_password"] = auto_generated_password

        path = self.router.users
        return self.request(method="put", path=path, json=user)

    def _delete(self, uuid: str) -> str:
        """Direct API method to delete a user.

        Args:
            uuid: user UUID
        """
        path = self.router.user.format(uuid=uuid)
        return self.request(method="delete", path=path)

    def _update(self, uuid: str, user: dict) -> dict:
        """Direct API method to update a user.

        Args:
            uuid: user UUID
            user: user metadata
        """
        path = self.router.user.format(uuid=uuid)
        return self.request(method="post", path=path, json=user)

    def _tokens_generate(self, uuid: str) -> str:
        """Direct API method to generate a password reset link for a user.

        Args:
            uuid: user UUID
        """
        path = self.router.tokens_generate
        data = {"user_id": uuid}
        return self.request(method="post", path=path, json=data, error_json_invalid=False)

    def _tokens_notify(self, uuid: str, email: str, invite: bool = False) -> str:
        """Direct API method to send a password reset link to a user.

        Args:
            uuid: user UUID
            email: email address to send link to
            invite: use welcome template instead of reset password template in email body
        """
        path = self.router.tokens_notify
        data = {"user_id": uuid, "email": email, "invite": invite}
        return self.request(method="POST", path=path, json=data)

    @property
    def router(self) -> Router:
        """Router for this API model."""
        return API_VERSION.system

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        from .system_roles import SystemRoles

        self.roles: SystemRoles = SystemRoles(auth=self.auth)
        """Work with roles"""

    def _update_user_attr(
        self, name: str, must_be_internal: bool, attr: str, value: Union[str, bool, dict]
    ) -> dict:
        """Set an attribute on a user.

        Args:
            name: user name
            must_be_internal: user must be internal or external for this attr to be set
            attr: attribute of user object to set
            value: value to set on attribute

        Raises:
            :exc:`ApiError`:

                * if user is external but must be internal for the attribute to be set
                * if user is internal but must be external for the attribute to be set
        """
        user = self.get_by_name(name=name)

        source = user.get(User.SOURCE, "")
        name = user[User.NAME]
        is_internal = source == User.INTERNAL

        pre = f"Unable to set {attr} for user {name!r} with source {source}"

        if isinstance(must_be_internal, bool):
            if is_internal and not must_be_internal:
                raise ApiError(f"{pre}, must be external user")

            if not is_internal and must_be_internal:
                raise ApiError(f"{pre}, must be internal user")

        if isinstance(value, dict):
            user.update(value)
        else:
            user[attr] = value

        self.LOG.debug(f"Updating user {name!r} attribute {attr!r}: {value!r}")
        self._update(uuid=user[User.UUID], user=user)
        return self.get_by_name(name=name)
