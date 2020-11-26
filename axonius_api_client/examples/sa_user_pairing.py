#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base example for setting up the API client.

1. Pull all user assets
2. find all usernames that begin with "sa-"
3. for each "sa-" username, see if there is a matching username WITHOUT the "sa-"
    a. if there is NOT a matching user without "sa-", tag the "sa-" user asset
    b. if there IS a matching user without "sa-", check if the non "sa-" account is disabled
    c. if the non "sa-" account exists and is disabled, tag the "sa-" user asset
"""
import dataclasses
from typing import Dict, Generator, List, Optional, Union

import axonius_api_client as axonapi

ADMIN_PREFIX = "sa-"
USERNAME = "specific_data.data.username"
DISABLED = "adapters_data.active_directory_adapter.account_disabled"
AXON_ID = "internal_axon_id"
USER_FIELDS = [USERNAME, DISABLED]


def get_usernames(asset: dict) -> List[str]:
    """Pass."""
    usernames = axonapi.tools.listify(asset.get(USERNAME, []))
    return [x.lower().strip() for x in usernames if x.lower().strip()]


def get_axon_id(asset: dict) -> str:
    """Pass."""
    return asset[AXON_ID]


class Tags(axonapi.data.BaseEnum):
    """Pass."""

    missing: str = "Normal Account Not Found"
    disabled: str = "Normal Account Disabled"


@dataclasses.dataclass
class UserMap(axonapi.data.BaseData):
    """Pass."""

    username: str
    axonius_link: str
    asset: dict

    @property
    def other_user_name(self) -> str:
        """Pass."""
        username = self.username.lower()
        prefix = ADMIN_PREFIX.lower()
        if username.startswith(prefix):
            return axonapi.tools.strip_left(obj=username, fix=prefix).strip()

        return f"{prefix}{username}".strip()

    @property
    def is_disabled(self) -> Union[bool, None]:
        """Pass."""
        return self.asset.get(DISABLED)

    @property
    def axonius_id(self) -> str:
        """Pass."""
        return get_axon_id(asset=self.asset)

    @property
    def usernames(self) -> List[str]:
        """Pass."""
        return get_usernames(asset=self.asset)


@dataclasses.dataclass
class AdminMap(axonapi.data.BaseData):
    """Pass."""

    admin: UserMap
    normal: Optional[UserMap] = None
    other: Optional[UserMap] = None

    @property
    def tag(self) -> Tags:
        """Pass."""
        if self.normal and self.normal.is_disabled and not self.admin.is_disabled:
            return Tags.is_disabled

        if not self.normal:
            return Tags.missing

        return None

    @property
    def result(self) -> str:
        """Pass."""
        if not self.tag:
            return "No action taken"

        return f"tagged with: {self.tag.value!r}"


class CustomConnect(axonapi.Connect):
    """Pass."""

    def run(self):
        """Pass."""
        assets = self.get_users()
        admin_maps = list(self.get_admin_maps(assets=assets))
        return self.get_tag_actions(admin_maps=admin_maps)
        # XXX HERE
        return admin_maps

    def get_users(self):
        """Pass."""
        # stub code for now
        """
        return self.users.get(fields=USER_FIELDS, fields_default=False)
        """
        import json

        return json.load(open("/tmp/user_data.json"))

    def get_admin_maps(self, assets: List[dict]) -> Generator[AdminMap, None, None]:
        """Pass."""
        for asset in assets:
            admin_user_map = self.get_admin_user_map(asset=asset)

            if not admin_user_map:
                continue

            normal_user_map = self.get_normal_user_map(assets=assets, admin_user_map=admin_user_map)
            admin_map = AdminMap(admin=admin_user_map, normal=normal_user_map)
            yield admin_map

    def get_normal_user_map(self, assets: List[dict], admin_user_map: UserMap) -> UserMap:
        """Pass."""
        for asset in assets:
            usernames = get_usernames(asset=asset)
            for username in usernames:
                if username == admin_user_map.other_user_name:
                    return UserMap(
                        username=username,
                        axonius_link=self.get_axon_link(asset=asset),
                        asset=asset,
                    )

    def get_admin_user_map(self, asset: dict) -> Optional[UserMap]:
        """Pass."""
        usernames = get_usernames(asset=asset)

        for username in usernames:
            if username.startswith(ADMIN_PREFIX.lower()):
                return UserMap(
                    username=username,
                    axonius_link=self.get_axon_link(asset=asset),
                    asset=asset,
                )

        return None

    def get_axon_link(self, asset: dict, type: str = "users") -> str:
        """Pass."""
        return f"{self.HTTP.url}/{type}/{get_axon_id(asset)}"

    def get_tag_actions(self, admin_maps: List[AdminMap]) -> Dict[str, List[str]]:
        """Pass."""
        tag_actions = {}
        for admin_map in admin_maps:
            if not admin_map.tag:
                continue

            tag_actions[admin_map.tag.value] = tag_actions.get(admin_map.tag.value, [])
            tag_actions[admin_map.tag.value].append(admin_map.admin.axonius_id)
        return tag_actions


if __name__ == "__main__":
    # get the URL, API key, API secret, & certwarn from the default ".env" file
    client_args = axonapi.get_env_connect()

    # OR override OS env vars with the values from a custom .env file
    # client_args = axonapi.get_env_connect(ax_env="/path/to/envfile", override=True)

    # create a client using the url, key, and secret from OS env
    client = CustomConnect(**client_args)

    j = client.jdump  # json dump helper

    client.start()  # connect to axonius

    admin_maps = client.run()
