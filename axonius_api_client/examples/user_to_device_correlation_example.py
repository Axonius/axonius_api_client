#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
from dataclasses import dataclass
from typing import Optional, Union

import click
from click.core import Context

import axonius_api_client as axonapi

USER_FIELDS = ["mssql:all", "active_directory:all", "cherwell_sql:all"]
DEVICE_FIELDS = ["mssql:all", "active_directory:all", "cherwell_sql:all"]

SHOW_IDS = False


@dataclass
class Device:
    axon_id: [str] = None
    found_via: Optional[str] = None

    cherwell_props: Optional["CherwellDeviceProps"] = None
    ad_props: Optional["ADDeviceProps"] = None

    def display(self):
        if self.cherwell_props and not self.ad_props:
            return [
                f"{self.cherwell_props.manufacturer} {self.cherwell_props.model} <{self.cherwell_props.serial_number}> [C]",
            ]
        elif self.ad_props and not self.cherwell_props:
            return [
                f"{self.ad_props.ad_distinguished_name} [AD]",
            ]
        elif self.cherwell_props and self.ad_props:
            return [
                f"{self.cherwell_props.manufacturer} {self.cherwell_props.model} <{self.cherwell_props.serial_number}> [C, AD]",
                f"{self.ad_props.ad_distinguished_name}",
            ]

    def __str__(self):
        return "\n".join(self.display())


@dataclass
class CherwellDeviceProps:
    owner: Optional[str] = None
    primary_user_email: Optional[str] = None
    primary_user_name: Optional[str] = None
    hostname: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    ips: Optional[str] = None
    mac: Optional[str] = None
    status: Optional[str] = None
    _attribution: Optional[str] = None
    _raw: Optional[dict] = None

    def from_raw(self, data):
        self.owner = data.get("owned_by", "")
        self.primary_user_email = data.get("primary_user_email", "")
        self.primary_user_name = data.get("primary_full_user_name", "")
        self.hostname = data.get("hostname", "")
        self.manufacturer = data.get("device_manufacturer", "")
        self.model = data.get("device_model", "")
        self.serial_number = data.get("device_serial", "")
        network_interfaces = data.get("network_interfaces")
        if network_interfaces and len(network_interfaces) >= 1:
            self.ips = network_interfaces[0].get("ips", [])
            self.mac = network_interfaces[0].get("mac", "")
        else:
            self.ips = []
            self.mac = ""
        self.status = data.get("asset_status", "")
        self._raw = data


@dataclass
class ADDeviceProps:
    id: Optional[str] = None
    ad_name: Optional[str] = None
    ad_distinguished_name: Optional[str] = None
    ad_object_category: Optional[str] = None
    ad_guid: Optional[str] = None
    ad_sid: Optional[str] = None
    _raw: Optional[dict] = None

    def from_raw(self, data):
        self.id = data.get("id")
        self.ad_name = data.get("ad_name")
        self.ad_distinguished_name = data.get("ad_distinguished_name")
        self.ad_object_category = data.get("ad_object_category")
        self.ad_guid = data.get("ad_guid")
        self.ad_sid = data.get("ad_sid")
        self._raw = data


@dataclass
class User:
    axon_id: [str] = None
    found_via: Optional[str] = None

    cherwell_props: Optional["CherwellUserProps"] = None
    ad_props: Optional["ADUserProps"] = None

    def display(self):
        if self.cherwell_props and not self.ad_props:
            return [
                f"{self.cherwell_props.first_name} {self.cherwell_props.last_name} <{self.cherwell_props.email}> [C]"
            ]
        elif self.ad_props and not self.cherwell_props:
            return [
                f"{self.ad_props.first_name} {self.ad_props.last_name} <{self.ad_props.email}> [AD]"
            ]
        elif self.cherwell_props and self.ad_props:
            return [
                f"{self.cherwell_props.first_name} {self.cherwell_props.last_name} <{self.cherwell_props.email}> [C, AD]"
            ]

    def __str__(self):
        return "\n".join(self.display())


@dataclass
class CherwellUserProps:
    employee_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    _raw: Optional[dict] = None

    def from_raw(self, data):
        self.employee_id = data.get("employee_id", "")
        self.first_name = data.get("first_name", "")
        self.last_name = data.get("last_name", "")
        self.full_name = data.get("full_name", "")
        self.email = data.get("mail", "")
        self._raw = data


@dataclass
class ADUserProps:
    employee_id: Optional[str] = None  # employee_id
    employee_number: Optional[str] = None  # employee_number
    account_name: Optional[str] = None  # ad_sAMAccountName
    first_name: Optional[str] = None  # first_name
    last_name: Optional[str] = None  # last_name
    full_name: Optional[str] = None  # ad_name
    email: Optional[str] = None  # ad_user_principal_name
    _raw: Optional[dict] = None

    def from_raw(self, data):
        self.employee_id = data.get("employee_id", "")
        self.employee_number = data.get("employee_number", "")
        self.account_name = data.get("ad_sAMAccountName", "")
        self.first_name = data.get("first_name", "")
        self.last_name = data.get("last_name", "")
        self.email = data.get("ad_user_principal_name", "")
        self._raw = data


def find_user(users, user_search_criteria):
    t, v = identify_type(user_search_criteria)

    user_matches = []

    for user in users:
        searched_user = User()

        searched_user.axon_id = user.get("internal_axon_id")
        searched_user.found_via = user_search_criteria

        mysql_cherwell = user.get("adapters_data.cherwell_sql_adapter")
        if mysql_cherwell:
            cherwell_props = user_prop_factory_iterator("cherwell", mysql_cherwell, t, v.lower())
            if cherwell_props:
                searched_user.cherwell_props = cherwell_props

        active_directory = user.get("adapters_data.active_directory_adapter")
        if active_directory:
            ad_props = user_prop_factory_iterator("ad", active_directory, t, v.lower())
            if ad_props:
                searched_user.ad_props = ad_props

        if (searched_user.cherwell_props or searched_user.ad_props) is not None:
            user_matches.append(searched_user)

    return user_matches


def user_prop_factory_iterator(source, user_obj, search_t, search_v):
    if isinstance(user_obj, list):
        if len(user_obj) == 1:
            return user_prop_factory(source, user_obj[0], search_t, search_v)
        elif len(user_obj) > 1:
            items = []
            for item in user_obj:
                i = user_prop_factory(source, item, search_t, search_v)
                if i:
                    items.append(i)
            if len(items) > 0:
                if len(items) == 1:
                    return items[0]
                else:
                    # return items
                    print(
                        "Too many results returned; please try to narrow the search criteria.",
                        file=sys.stderr,
                    )
                    sys.exit(1)
            else:
                return None
    else:
        return user_prop_factory(source, user_obj, search_t, search_v)


def user_prop_factory(source, user_obj, search_t, search_v):
    return_props = False
    if source == "cherwell":
        props = CherwellUserProps()
        props.from_raw(user_obj)
        if search_t == "email":
            if search_v.lower() == props.email.lower():
                return_props = True
        elif search_t == "name":
            if (
                search_v.lower() == props.full_name.lower()
                or search_v.lower() == " ".join([props.first_name, props.last_name]).lower()
            ):
                return_props = True
        elif search_t == "generic":
            email_parts = props.email.split("@")
            if email_parts and len(email_parts) > 1:
                if search_v.lower() == email_parts[0].lower():
                    return_props = True
        if return_props:
            return props
    elif source == "ad":
        props = ADUserProps()
        props.from_raw(user_obj)
        if search_t == "email":
            if search_v.lower() == props.email.lower():
                return_props = True
        elif search_t == "name":
            if (
                search_v.lower() == ", ".join([props.last_name, props.first_name]).lower()
                or search_v.lower() == " ".join([props.first_name, props.last_name]).lower()
            ):
                return_props = True
        elif search_t == "generic":
            email_parts = props.email.split("@")
            if email_parts and len(email_parts) > 1:
                if search_v.lower() == email_parts[0].lower():
                    return_props = True
            if search_v.lower() == props.account_name.lower():
                return_props = True
        if return_props:
            return props
    return None


def find_machine(machines, machine_search_criteria):
    t, v = identify_type(machine_search_criteria)

    device_matches = []

    for machine in machines:
        device = Device()

        device.axon_id = machine.get("internal_axon_id")
        device.found_via = machine_search_criteria

        mysql_cherwell = machine.get("adapters_data.cherwell_sql_adapter")
        if mysql_cherwell:
            cherwell_props = machine_prop_factory_iterator("cherwell", mysql_cherwell, t, v.lower())
            if cherwell_props:
                device.cherwell_props = cherwell_props

        if device.cherwell_props:  # if we matched on cherwell let's grab the AD data
            active_directory = machine.get("adapters_data.active_directory_adapter")
            if active_directory:
                active_directory_props = machine_prop_factory_iterator(
                    "active_directory", active_directory, t, v.lower()
                )
                if active_directory_props:
                    device.ad_props = active_directory_props

        if (device.cherwell_props or device.ad_props) is not None:
            device_matches.append(device)

    return device_matches


def machine_prop_factory_iterator(source, machine_obj, search_t, search_v):
    if isinstance(machine_obj, list):
        if len(machine_obj) == 1:
            return machine_prop_factory(source, machine_obj[0], search_t, search_v)
        elif len(machine_obj) > 1:
            items = []
            for item in machine_obj:
                i = machine_prop_factory(source, item, search_t, search_v)
                if i:
                    items.append(i)
            if len(items) > 0:
                if len(items) == 1:
                    return items[0]
                else:
                    if source == "cherwell":
                        in_use = []
                        retired = []
                        other = []

                        for m in items:
                            if m.status.lower() == "in use":
                                in_use.append(m)
                            elif m.status.lower() == "retired":
                                retired.append(m)
                            else:
                                other.append(m)

                        if len(in_use) == 0:
                            return None
                        elif len(in_use) == 1:
                            return in_use[0]
                        else:
                            print(
                                "Too many results returned; please try to narrow the search criteria.",
                                file=sys.stderr,
                            )
                            sys.exit(1)
                    else:
                        print(
                            "Too many results returned; please try to narrow the search criteria.",
                            file=sys.stderr,
                        )
                        sys.exit(1)

            else:
                return None
    else:
        return machine_prop_factory(source, machine_obj, search_t, search_v)


def machine_prop_factory(source, machine_obj, search_t, search_v):
    return_props = False
    if source == "cherwell":
        props = CherwellDeviceProps()
        props.from_raw(machine_obj)
        if search_t == "email":
            if search_v.lower() == props.primary_user_email.lower():
                return_props = True
        elif search_t == "name":
            if (
                search_v.lower() == props.primary_user_name.lower()
                or search_v == props.owner.lower()
            ):
                return_props = True
        elif search_t == "ip":
            if search_v in props.ips:
                return_props = True
        elif search_t == "mac":
            if search_v.lower() == props.mac.lower():
                return_props = True
        elif search_t == "generic":
            if is_email_prefix(search_v.lower(), props.primary_user_email.lower()):
                return_props = True
            if search_v.lower() == props.serial_number.lower():
                return_props = True
            if search_v.lower() == props.hostname.lower():
                return_props = True
        if return_props:
            return props
    elif source == "active_directory":
        # Since there is no data we can use to tie AD info to a user, we just need to return the AD object.
        props = ADDeviceProps()
        props.from_raw(machine_obj)
        return props
    return None


def determine_machine_attribution(machine: Device):
    t, v = identify_type(machine.found_via)
    if t == "email":
        if v == machine.cherwell_props.primary_user_email:
            return "primary"
    elif t == "name":
        if v == machine.cherwell_props.primary_user_name:
            return "primary"
        elif v == machine.cherwell_props.owner:
            return "owner"
    elif t == "generic":
        if is_email_prefix(v, machine.cherwell_props.primary_user_email):
            return "primary"


def identify_type(search: str):
    if "@" in search:
        return "email", search
    elif " " in search:
        return "name", search
    elif "." in search and len(search.split(".")) == 4:
        return "ip", search
    elif ":" in search and len(search.split(":")) == 6:
        return "mac", search
    else:
        return "generic", search


def is_email_prefix(search, email):
    if search and email:
        if "@" in email:
            email_parts = email.split("@")
            if search.lower() == email_parts[0].lower():
                return True
    return False


def three_way_mixer(
    first_label: str, first_value: str, second_label: str, second_value: str, offset: int
) -> str:
    if first_value and not second_value:
        return f"{' ' * offset}{first_label}: {first_value}"
    elif second_value and not first_value:
        return f"{' ' * offset}{second_label}: {second_value}"
    elif first_value and second_value:
        return f"{' ' * offset}{first_label}: {first_value}, {second_label}: {second_value}"


class CustomConnect(axonapi.Connect):
    """Pass."""

    def run(self, user_search_criteria=None, device_search_criteria=None):
        """Pass."""
        if user_search_criteria:
            user_matches = find_user(self.get_users(), user_search_criteria)
            self.user_search_cli_output(user_search_criteria, user_matches)

        elif device_search_criteria:
            machine_matches = find_machine(self.get_devices(), device_search_criteria)
            self.device_search_cli_output(device_search_criteria, machine_matches)

    def user_search_cli_output(self, user_search_criteria, user_matches):
        print("Searching For: ", user_search_criteria)

        if len(user_matches) > 0:
            print("Found Users:")
            for match in user_matches:
                print("    ", match)

            if SHOW_IDS:
                print()
                print([u.axon_id for u in user_matches])

            print()
        else:
            print("No Users Found")
            sys.exit(0)

        print("Looking For Machines:")

        machine_matches = []

        for match in user_matches:
            if match.cherwell_props:
                email = match.cherwell_props.email
                if email is not None:
                    matches = find_machine(self.get_devices(), email)
                    for m in matches:
                        machine_matches.append(m)

                machine_serials = []
                for i, m in enumerate(machine_matches):
                    serial = None
                    if m.cherwell_props:
                        serial = m.cherwell_props.serial_number
                    if serial:
                        if serial not in machine_serials:
                            machine_serials.append(serial)
                        else:
                            del machine_matches[i]

                if len(machine_matches) > 0:
                    print(f"Found Machines ({len(machine_matches)}):")
                    print("    Primary:")
                    for m in machine_matches:
                        if determine_machine_attribution(m) == "primary":
                            for part in m.display():
                                print(f"        {part}")
                            print(f"            Owner: {m.cherwell_props.owner}")
                            print(
                                three_way_mixer(
                                    "IPS:",
                                    ", ".join(m.cherwell_props.ips),
                                    "MAC",
                                    m.cherwell_props.mac,
                                    12,
                                )
                            )
                            print(f"            Found VIA: {m.found_via}")
                            print()

                    if SHOW_IDS:
                        print()
                        print([m.axon_id for m in machine_matches])

    def device_search_cli_output(self, device_search_criteria, machine_matches):
        print("Searching For: ", device_search_criteria)

        if len(machine_matches) > 0:
            print("Found Machines:")

            for m in machine_matches:
                for part in m.display():
                    print(f"    {part}")
                if m.cherwell_props:
                    if m.cherwell_props.primary_user_email:
                        if m.cherwell_props.primary_user_name:
                            print(
                                f"        Primary User: {m.cherwell_props.primary_user_name} <{m.cherwell_props.primary_user_email}>"
                            )
                        else:
                            print(f"        Primary User: {m.cherwell_props.primary_user_email}")
                        if m.cherwell_props.owner:
                            print(f"        Owner: {m.cherwell_props.owner}")
                    print(
                        three_way_mixer(
                            "IPS", ", ".join(m.cherwell_props.ips), "MAC", m.cherwell_props.mac, 8
                        )
                    )
                    print(f"        Found VIA: {m.found_via}")
                print()
            if SHOW_IDS:
                print()
                print([m.axon_id for m in machine_matches])

    def get_users(self):
        return self.users.get(fields=USER_FIELDS)

    def get_devices(self):
        return self.devices.get(fields=DEVICE_FIELDS)


class Mutex(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if: list = kwargs.pop("not_required_if")

        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs["help"] = (
            kwargs.get("help", "")
            + " Option is mutually exclusive with "
            + ", ".join(self.not_required_if)
            + "."
        ).strip()
        super(Mutex, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        current_opt: bool = self.name in opts
        for mutex_opt in self.not_required_if:
            if mutex_opt in opts:
                if current_opt:
                    raise click.UsageError(
                        "Illegal usage: '"
                        + str(self.name)
                        + "' is mutually exclusive with "
                        + str(mutex_opt)
                        + "."
                    )
                else:
                    self.prompt = None
        return super(Mutex, self).handle_parse_result(ctx, opts, args)


@click.command()
@click.option("--user", help="User to search.", cls=Mutex, not_required_if=["device"])
@click.option("--device", help="Device to search.", cls=Mutex, not_required_if=["user"])
@click.pass_context
def main(ctx: Context, user: str, device: str):
    if not user and not device:
        print(ctx.get_help())
        sys.exit(1)

    client_args = axonapi.get_env_connect()
    client = CustomConnect(**client_args)
    client.start()

    if user:
        client.run(user_search_criteria=user)
    elif device:
        client.run(device_search_criteria=device)


if __name__ == "__main__":
    main()
