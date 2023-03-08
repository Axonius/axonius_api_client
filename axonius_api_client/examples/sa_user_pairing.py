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
import csv
import dataclasses
import datetime
import pathlib
from collections.abc import MutableMapping
from typing import Dict, Generator, List, Optional, Union

import axonius_api_client as axonapi

ADMIN_PREFIX = "sa-"
USERNAME = "specific_data.data.username"

DISABLED = "adapters_data.active_directory_adapter.account_disabled"
# DISABLED = "adapters_data.csv_adapter.csv_account_disabled"
# DISABLED = "adapters_data.json_adapter.json_account_disabled"

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


class PropsDataToDict(axonapi.data.PropsData):
    """Pass."""

    def to_dict(self, dt_obj: bool = False) -> dict:
        """Pass."""

        def get_val(prop):
            value = getattr(self, prop)
            if not dt_obj and isinstance(value, datetime.datetime):
                return str(value)
            if isinstance(value, axonapi.data.PropsData):
                return value.to_dict()
            if isinstance(value, axonapi.data.BaseEnum):
                return value.value
            return value

        ret = {k: get_val(k) for k in self._properties}
        return ret


def normalize_bool(value: Union[str, bool]) -> bool:
    if isinstance(value, bool):
        return value

    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False


@dataclasses.dataclass
class UserMap(PropsDataToDict):
    """Pass."""

    username: str
    axonius_link: str

    @property
    def _properties(self):
        return ["username", "axonius_link", "other_user_name", "is_disabled", "usernames"]

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

        return self.raw.get(DISABLED)

    @property
    def axonius_id(self) -> str:
        """Pass."""

        return get_axon_id(asset=self.raw)

    @property
    def usernames(self) -> List[str]:
        """Pass."""

        return get_usernames(asset=self.raw)


@dataclasses.dataclass
class AdminMap(PropsDataToDict):
    """Pass."""

    admin: UserMap
    normal: Optional[UserMap] = None
    other: Optional[UserMap] = None

    @property
    def _properties(self):
        return ["admin", "normal", "other", "tag", "result"]

    @property
    def tag(self) -> Union[Tags, None]:
        """Pass."""

        normal_disabled = None
        admin_disabled = None

        if self.admin and self.admin.is_disabled:
            if isinstance(self.admin.is_disabled, (bool, str)):
                admin_disabled = normalize_bool(self.admin.is_disabled)

            elif isinstance(self.admin.is_disabled, list):
                if len(self.admin.is_disabled) == 1:
                    admin_disabled = normalize_bool(self.admin.is_disabled[0])
                else:
                    index = self.admin.usernames.index(self.admin.username)
                    admin_disabled = normalize_bool(self.admin.is_disabled[index])

        if self.normal and self.normal.is_disabled:
            if isinstance(self.normal.is_disabled, (bool, str)):
                normal_disabled = self.normal.is_disabled

            elif isinstance(self.normal.is_disabled, list):
                if len(self.normal.is_disabled) == 1:
                    normal_disabled = normalize_bool(self.normal.is_disabled[0])
                else:
                    index = self.normal.usernames.index(self.normal.username)
                    normal_disabled = normalize_bool(self.normal.is_disabled[index])

        if self.normal and normal_disabled and not admin_disabled:
            return Tags.disabled

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

        # return self.get_tag_actions(admin_maps=admin_maps)

        return admin_maps

    def get_users(self):
        """Pass."""

        return self.users.get(fields=USER_FIELDS, fields_default=False)

    def get_admin_maps(self, assets: List[dict]) -> Generator[AdminMap, None, None]:
        """Pass."""

        for asset in assets:
            admin_user_map = self.get_admin_user_map(asset=asset)

            if not admin_user_map:
                continue

            normal_user_map = self.get_normal_user_map(assets=assets, admin_user_map=admin_user_map)
            admin_map = AdminMap(raw=None, admin=admin_user_map, normal=normal_user_map)
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
                        raw=asset,
                    )

    def get_admin_user_map(self, asset: dict) -> Optional[UserMap]:
        """Pass."""

        usernames = get_usernames(asset=asset)
        for username in usernames:
            if username.startswith(ADMIN_PREFIX.lower()):
                return UserMap(
                    username=username,
                    axonius_link=self.get_axon_link(asset=asset),
                    raw=asset,
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


def flatten_dict(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def write_csv(results, path="sa_user_pairing.csv", fields=None, ignores=None):
    if ignores is None:
        ignores = []

    path = pathlib.Path(path)

    if not fields:
        fields = list(results[0].keys())

    if ignores:
        fields = [x for x in fields if x not in ignores]

    with path.open("w") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", quoting=csv.QUOTE_ALL)
        writer.writerow(dict(zip(fields, fields)))

        for result in results:
            flattened = flatten_dict(result.to_dict())

            for k, v in flattened.items():
                if isinstance(v, list):
                    if len(v) == 1:
                        flattened[k] = v[0]
                    else:
                        flattened[k] = "  - " + "\n  - ".join([str(x) for x in v])
            writer.writerow(flattened)

    print(f"wrote results to {path}")


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

    # fields = [
    #     'admin_username', 'admin_axonius_link', 'admin_other_user_name', 'admin_is_disabled', 'admin_usernames',
    #     'normal_username', 'normal_axonius_link', 'normal_other_user_name', 'normal_is_disabled', 'normal_usernames',
    #     'other', 'tag', 'result'
    # ]

    fields = [
        "admin_username",
        "admin_axonius_link",
        "admin_is_disabled",
        "admin_usernames",
        "normal_username",
        "normal_usernames",
        "normal_axonius_link",
        "normal_is_disabled",
        "tag",
    ]

    labels = axonapi.api.assets.labels.Labels(client.users)

    to_tag_missing: List[str] = [x.admin.axonius_id for x in admin_maps if x.tag is Tags.missing]
    processed = labels.add(to_tag_missing, [str(Tags.missing)])

    to_tag_disabled: List[str] = [x.admin.axonius_id for x in admin_maps if x.tag is Tags.disabled]
    processed = labels.add(to_tag_disabled, [str(Tags.disabled)])

    write_csv(admin_maps, fields=fields)
