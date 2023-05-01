# -*- coding: utf-8 -*-
"""API for working with system users."""
import typing as t

import cachetools

from ...constants.api import MAX_PAGE_SIZE
from ...exceptions import ApiError, NotFoundError
from ...parsers.tables import tablize_users
from ...tools import coerce_bool
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..mixins import ModelMixins

CACHE_GET: cachetools.TTLCache = cachetools.TTLCache(maxsize=1024, ttl=60)
MODEL = json_api.system_users.SystemUser


class SystemUsers(ModelMixins):
    """API for working with system users."""

    def get(self, generator: bool = False) -> t.Union[t.Generator[dict, None, None], t.List[dict]]:
        """Get Axonius system users.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> users = client.system_users.get()
            >>> [x['user_name'] for x in users]
            ['admin']

        Args:
            generator: return an iterator for objects that will yield rows as they are fetched

        """
        gen = self.get_generator()
        return gen if generator else list(gen)

    def get_generator(self) -> t.Generator[dict, None, None]:
        """Get Axonius system users using a generator."""
        offset = 0

        while True:
            rows = self._get(offset=offset)
            offset += len(rows)

            if not rows:
                break

            for row in rows:
                yield row.to_dict_old()

    def get_cached_single(self, value: t.Union[str, dict, MODEL]) -> MODEL:
        """Pass."""
        name = MODEL._get_attr_value(value=value, attr="user_name")
        uuid = MODEL._get_attr_value(value=value, attr="uuid")
        items = self.get_cached()
        for item in items:
            if name == item.user_name or uuid == item.uuid:
                return item

        err = f"No user found with name of {name!r} or UUID of {uuid!r}"
        raise NotFoundError(tablize_users(users=[x.to_dict_old() for x in items], err=err))

    @cachetools.cached(cache=CACHE_GET)
    def get_cached(self) -> t.List[MODEL]:
        """Get Axonius system users using a cache mechanism."""
        offset = 0
        ret = []
        while True:
            rows = self._get(offset=offset)
            offset += len(rows)
            ret += rows
            if not rows:
                break
        return ret

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
        found = [x for x in users if x["user_name"] == name]
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
        found = [x for x in users if x["uuid"] == uuid]
        if found:
            return found[0]

        err = f"User with uuid of {uuid!r} not found"
        raise NotFoundError(tablize_users(users=users, err=err))

    def add(
        self,
        name: str,
        password: str,
        role_name: str,
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        generate_password_link: bool = False,
        email_password_link: bool = False,
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
            name: username
            password: password
            role_name: role name
            first_name: first name
            last_name: last name
            email: email address
            generate_password_link: create a password reset link
            email_password_link: email the password reset link to a users configured email address

        Raises:
            :exc:`ApiError`: if user already exists matching name
        """
        if not any([password, generate_password_link, email_password_link]):
            raise ApiError("Must supply password, generate_password_link, or email_password_link")

        if email_password_link and not email:
            raise ApiError("Must supply email if email_password_link is True")

        role = self.roles.get_by_name(name=role_name)

        try:
            self.get_by_name(name=name)
            raise ApiError(f"User with name of {name!r} already exists")
        except NotFoundError:
            pass

        self._add(
            user_name=name,
            role_id=role["uuid"],
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            auto_generated_password=generate_password_link,
        )

        new_user = self.get_by_name(name)

        if generate_password_link or email_password_link:  # pragma: no cover
            password_reset_link = self.get_password_reset_link(name)
            new_user["password_reset_link"] = password_reset_link
            if email_password_link:
                try:
                    self.email_password_reset_link(
                        name, email=email, for_new_user=True, link=password_reset_link
                    )
                except Exception as exc:
                    new_user["email_password_link_error"] = (
                        getattr(getattr(exc, "response", None), "text", None) or exc
                    )

        return new_user

    def set_role(self, name: str, role_name: str) -> dict:
        """Change the role of a user.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> user = client.system_users.set_role(name='test1', role_name='Viewer')
            >>> user['role_name']
            'Viewer'

        Args:
            name: username
            role_name: name of role
        """
        role = self.roles.get_by_name(name=role_name)
        return self._update_user_attr(
            name=name, must_be_internal=True, attr="role_id", value=role["uuid"]
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
            name: username
            first: first name
            last: last name
        """
        value = {"first_name": first, "last_name": last}
        attr = "first_name and last_name"
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
            name=name, must_be_internal=True, attr="password", value=password
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
        return self._update_user_attr(name=name, must_be_internal=True, attr="email", value=email)

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
            name=name,
            must_be_internal=False,
            attr="ignore_role_assignment_rules",
            value=coerce_bool(obj=enabled),
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
        if name == "admin":
            raise ApiError(f"Unable to delete {name!r} user")

        user = self.get_by_name(name=name)
        return self._delete(uuid=user["uuid"]).document_meta

    def get_password_reset_link(self, name: str) -> str:
        """Generate a password reset link for a user.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> link = client.system_users.get_password_reset_link(name='test1')
            >>> link
            'https://10.20.0.61/login?token=LUayznSkfLUjm3A2fIs_zAF-4CzcxRZc7DHOfhOkMRI'

        Notes:
            This link can be provided to the user. They can browse to it, or they can use
            `axonshell tools use-password-reset-token` or use
            :meth:`axonius_api_client.api.system.signup.Signup.use_password_reset_token`

        Args:
            name: username

        """
        user = self.get_by_name(name=name)
        return self._tokens_generate(uuid=user["uuid"], user_name=user["user_name"])

    def email_password_reset_link(
        self, name: str, email: t.Optional[str] = None, for_new_user: bool = False, link: str = ""
    ) -> t.Tuple[str, str]:
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
            name: username
            email: use a custom email address to send the email instead of the users defined email
                address. required if the user has no defined email address.
            for_new_user: use the new user email template instead of the password reset email
                template
            link: use the specified password reset link vs a newly generated one
        """
        user = self.get_by_name(name=name)
        email = email or user.get("email")

        if not email:
            raise ApiError(
                f"User {name!r} has no email address defined, must supply a custom email address"
            )

        if not link:
            link = self._tokens_generate(uuid=user["uuid"], user_name=user["user_name"])
        self._tokens_notify(uuid=user["uuid"], email=email, invite=for_new_user)
        return link, email

    def _get(self, limit: int = MAX_PAGE_SIZE, offset: int = 0, **kwargs) -> t.List[MODEL]:
        """Direct API method to get all users.

        Args:
            limit: limit to N rows per page
            offset: start at row N
        """
        api_endpoint = ApiEndpoints.system_users.get
        kwargs.setdefault("page", {"limit": limit, "offset": offset})
        request_obj = api_endpoint.load_request(**kwargs)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _add(
        self,
        user_name: str,
        role_id: str,
        password: t.Optional[str] = None,
        auto_generated_password: bool = False,
        first_name: str = "",
        last_name: str = "",
        email: str = "",
    ) -> MODEL:
        """Direct API method to add a user.

        Args:
            user_name: user name
            password: password
            role_id: role UUID
            first_name: first name
            last_name: last name
            email: email address
            auto_generated_password: generate a password
        """
        api_endpoint = ApiEndpoints.system_users.create
        request_obj = api_endpoint.load_request(
            user_name=user_name,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
            role_id=role_id,
            auto_generated_password=auto_generated_password,
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _delete(self, uuid: str) -> MODEL:
        """Direct API method to delete a user.

        Args:
            uuid: user UUID
        """
        api_endpoint = ApiEndpoints.system_users.delete
        request_obj = api_endpoint.load_request(uuid=uuid)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _update(
        self,
        uuid: str,
        user_name: str,
        role_id: str,
        password: str,
        first_name: t.Optional[str] = None,
        last_name: t.Optional[str] = None,
        email: t.Optional[str] = None,
        last_updated: t.Optional[str] = None,
        source: t.Optional[str] = None,
        pic_name: t.Optional[str] = None,
        ignore_role_assignment_rules: t.Optional[bool] = None,
        **kwargs,
    ) -> MODEL:
        """Direct API method to update a user.

        Args:
            uuid: user UUID
            user: user metadata
        """
        api_endpoint = ApiEndpoints.system_users.update
        request_obj = api_endpoint.load_request(
            user_name=user_name,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
            role_id=role_id,
            uuid=uuid,
            last_updated=last_updated,
            source=source,
            pic_name=pic_name,
            ignore_role_assignment_rules=ignore_role_assignment_rules,
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _tokens_generate(self, uuid: str, user_name: str) -> str:
        """Direct API method to generate a password reset link for a user.

        Args:
            uuid: user UUID
        """
        api_endpoint = ApiEndpoints.password_reset.create
        request_obj = api_endpoint.load_request(
            user_id=uuid,
            user_name=user_name,
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _tokens_notify(self, uuid: str, email: str, invite: bool = False) -> str:
        """Direct API method to send a password reset link to a user.

        Args:
            uuid: user UUID
            email: email address to send link to
            invite: use welcome template instead of reset password template in email body
        """
        api_endpoint = ApiEndpoints.password_reset.send
        request_obj = api_endpoint.load_request(
            user_id=uuid,
            email=email,
            invite=invite,
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        from .system_roles import SystemRoles

        self.roles: SystemRoles = SystemRoles(auth=self.auth)
        """Work with roles"""

    def _update_user_attr(
        self, name: str, must_be_internal: bool, attr: str, value: t.Union[str, bool, dict]
    ) -> dict:
        """Set an attribute on a user.

        Args:
            name: username
            must_be_internal: user must be internal or external for this attr to be set
            attr: attribute of user object to set
            value: value to set on attribute

        Raises:
            :exc:`ApiError`:

                * if user is external but must be internal for the attribute to be set
                * if user is internal but must be external for the attribute to be set
        """
        user = self.get_by_name(name=name)

        source = user.get("source", "")
        name = user["user_name"]
        is_internal = source == "internal"

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
        self._update(**user)
        return self.get_by_name(name=name)
