#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Base example for setting up the API client."""
import csv
import dataclasses
import datetime
import io
from typing import Generator, List, Optional, Type, Union

import click
import tabulate

import axonius_api_client as axonapi
from axonius_api_client.api import ApiEndpoint
from axonius_api_client.api.json_api.base import BaseModel, BaseSchema
from axonius_api_client.api.json_api.custom_fields import SchemaDatetime, get_field_dc_mm
from axonius_api_client.api.mixins import ModelMixins

# from axonius_api_client.api.models import (ApiEndpoint, Model, BaseModel,
#                                            BaseSchema)
from axonius_api_client.cli import cli, grp_adapters
from axonius_api_client.cli.context import CONTEXT_SETTINGS
from axonius_api_client.cli.options import AUTH, add_options
from axonius_api_client.constants.api import TABLE_FORMAT
from axonius_api_client.exceptions import NotFoundError
from axonius_api_client.parsers.tables import tablize
from axonius_api_client.tools import coerce_bool, coerce_int, dt_now, dt_parse, json_dump, listify

CLI_MODE: bool = True
"""This controls whether to use the click cli or run as a standard program."""


@dataclasses.dataclass
class AdapterFetchHistory(BaseModel):
    """AdapterFetchHistory container."""

    adapter: dict
    adapter_discovery_id: str
    client: str
    duration: str
    instance: str
    realtime: bool
    status: str
    end_time: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    start_time: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    devices_count: Optional[int] = None
    users_count: Optional[int] = None
    ignored_users_count: Optional[int] = None
    ignored_devices_count: Optional[int] = None
    error: Optional[str] = None

    @classmethod
    def columns(cls) -> List[str]:
        """Help function to create list of column names."""
        props = getattr(cls, "_table_properties", cls._str_properties)()
        return [cls._human_key(x) for x in props]

    @property
    def duration_delta(self) -> Optional[datetime.timedelta]:
        """Help function to calculate timedelta between two dates."""
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        if self.start_time:
            return dt_now() - self.start_time
        return None

    @property
    def adapter_name(self) -> str:
        """Pass."""
        return self.adapter["icon"]

    @property
    def adapter_friendly_name(self) -> str:
        """Pass."""
        return self.adapter["text"]

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "instance",
            "adapter_name",
            "adapter_friendly_name",
            "client",
            "start_time",
            "end_time",
            "duration",
            "status",
            "error",
            "devices_count",
            "users_count",
            "ignored_users_count",
            "ignored_devices_count",
        ]

    @staticmethod
    def _get_schema_cls() -> Optional[Type[BaseSchema]]:
        return None

    def to_tablize(self) -> dict:
        """Pass."""
        props = getattr(self, "_table_properties", self._str_properties)()
        return {self._human_key(k): getattr(self, k, None) for k in props}


class FetchHistory(ModelMixins):
    """Handle all the interactions."""

    def get(
        self, generator: bool = False, **kwargs
    ) -> Union[Generator[AdapterFetchHistory, None, None], List[AdapterFetchHistory]]:
        """Get all adapter history.

        Args:
            generator: return an iterator
        """
        gen = self.get_generator(**kwargs)
        return gen if generator else list(gen)

    def get_generator(
        self,
        date_from: Optional[Union[str, datetime.datetime]] = None,
        date_to: Optional[Union[str, datetime.datetime]] = None,
        past_minutes: Optional[int] = None,
        adapters: Optional[Union[str, List[str]]] = None,
        clients: Optional[Union[str, List[str]]] = None,
        statuses: Optional[Union[str, List[str]]] = None,
        exclude_realtime: bool = False,
    ) -> Generator[AdapterFetchHistory, None, None]:
        """Get adapter history using a generator."""

        def validate_adapter(obj):
            if not obj.endswith("_adapter"):
                obj = f"{obj}_adapter"
            valids = valid_enums["adapters_filter"]
            valid_names = [x["name"] for x in valids]
            if obj not in valid_names:
                err = f"Adapter with name of {obj!r} not found"
                raise NotFoundError(tablize(value=valids, err=err))
            return obj

        def validate_client(obj):
            valids = valid_enums["clients_filter"]
            if obj not in valids:
                err = f"Client with id of {obj!r} not found"
                valids = "\n  " + "\n  ".join(valids)
                raise NotFoundError(f"{err}, valid ids:{valids}\n{err}")
            return obj

        def validate_status(obj):
            valids = valid_enums["statuses_map"]
            obj = obj.lower()
            if obj not in valids:
                err = f"Status of {obj!r} is not valid"
                valids = "\n  " + "\n  ".join(list(valids))
                raise NotFoundError(f"{err}, valid statuses:{valids}\n{err}")
            return valids[obj]

        def fmt_time(obj: datetime.datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%SZ")

        valid_enums = None

        if date_from:
            date_from = fmt_time(dt_parse(obj=date_from))
        if date_to:
            date_to = fmt_time(dt_parse(obj=date_to))
        if past_minutes:
            past_minutes = coerce_int(obj=past_minutes)
            past_minutes = dt_now() - datetime.timedelta(seconds=past_minutes * 60)
            date_from = fmt_time(past_minutes)
            date_to = fmt_time(date_to or dt_now())

        if adapters:
            valid_enums = valid_enums or self.get_enums()
            adapters = [validate_adapter(x) for x in listify(adapters)]
        if clients:
            valid_enums = valid_enums or self.get_enums()
            clients = [validate_client(x) for x in listify(clients)]
        if statuses:
            valid_enums = valid_enums or self.get_enums()
            statuses = [validate_status(x) for x in listify(statuses)]

        exclude_realtime = coerce_bool(obj=exclude_realtime)

        offset = 0
        while True:
            rows = self._get(
                date_from=date_from,
                date_to=date_to,
                offset=offset,
                adapters_filter=adapters,
                clients_filter=clients,
                statuses_filter=statuses,
                exclude_realtime=exclude_realtime,
            )
            self.LOG.debug(f"Received page with {len(rows)} rows")

            offset += len(rows)

            if not rows:
                break

            for row in rows:
                yield row

    def _get(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        offset: int = 0,
        limit: int = 2000,
        adapters_filter: Optional[List[str]] = None,
        clients_filter: Optional[List[str]] = None,
        statuses_filter: Optional[List[str]] = None,
        exclude_realtime: bool = False,
    ) -> List[AdapterFetchHistory]:
        """Actual request to the server and returns the response object."""
        endpoint = ApiEndpoint(
            method="post",
            path="api/adapters/history",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=AdapterFetchHistory,
        )

        http_args = {
            "json": self._get_request_body(
                date_from=date_from,
                date_to=date_to,
                offset=offset,
                limit=limit,
                adapters_filter=adapters_filter,
                clients_filter=clients_filter,
                statuses_filter=statuses_filter,
                exclude_realtime=exclude_realtime,
            )
        }

        return endpoint.perform_request(http=self.auth.http, http_args=http_args)

    @staticmethod
    def _get_request_body(
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        offset: int = 0,
        limit: int = 2000,
        adapters_filter: Optional[List[str]] = None,
        clients_filter: Optional[List[str]] = None,
        statuses_filter: Optional[List[str]] = None,
        exclude_realtime: bool = False,
    ) -> dict:
        """Help function to create the request body via the ApiEndpoint.perform_request call."""
        return {
            "data": {
                "type": "history_request_schema",
                "attributes": {
                    "date_from": date_from,
                    "date_to": date_to,
                    "page": {"offset": offset, "limit": limit},
                    "adapters_filter": adapters_filter or [],
                    "clients_filter": clients_filter or [],
                    "statuses_filter": statuses_filter or [],
                    "exclude_realtime": exclude_realtime,
                },
            }
        }

    def get_enums(self) -> dict:
        """Public method to get the enums used for filtering."""
        data = self._get_enums()
        data["adapters_filter"] = [
            {"name": x["id"], "friendly_name": x["name"]} for x in data["adapters_filter"]
        ]
        data["clients_filter"] = [x["id"] for x in data["clients_filter"]]
        data["statuses_map"] = {x.lower().replace(" ", "_"): x for x in data["statuses_filter"]}

        return data

    def _get_enums(self) -> dict:
        """Private method to get the enums used for filtering."""
        endpoint = ApiEndpoint(
            method="get",
            path="api/adapters/history/filters",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=None,
        )

        return endpoint.perform_request(http=self.auth.http)


if __name__ == "__main__" and CLI_MODE:
    # This is the entry point for the CLI mode.
    # It patches in additional functionality to the CLI and then executes the original CLI script.

    # Add the extra options and flags to the command line.
    @click.command(context_settings=CONTEXT_SETTINGS)
    @add_options(AUTH)
    @click.option(
        "--date-from",
        "-df",
        "date_from",
        help="Only fetch items starting from this date",
        metavar="DATE",
        required=False,
        default=None,
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--date-to",
        "-dt",
        "date_to",
        help="Only fetch items up until this date",
        metavar="DATE",
        required=False,
        default=None,
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--past-minutes",
        "-pm",
        "past_minutes",
        help="Only fetch items from the last N minutes (will override --date-from)",
        type=click.INT,
        required=False,
        default=None,
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--adapter",
        "-a",
        "adapters",
        help="Only fetch items from these adapters (multiple)",
        required=False,
        default=None,
        show_envvar=True,
        show_default=True,
        multiple=True,
    )
    @click.option(
        "--client",
        "-c",
        "clients",
        help="Only fetch items from these client IDs (multiple)",
        required=False,
        default=None,
        show_envvar=True,
        show_default=True,
        multiple=True,
    )
    @click.option(
        "--status",
        "-s",
        "statuses",
        help="Only fetch items with these statuses (multiple)",
        required=False,
        default=None,
        show_envvar=True,
        show_default=True,
        multiple=True,
    )
    @click.option(
        "--exclude-realtime",
        "-er",
        "exclude_realtime",
        help="Do not include any real-time adapters",
        required=False,
        type=click.BOOL,
        default=False,
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--export-format",
        "-xf",
        "export_format",
        type=click.Choice(["json", "str", "csv", "table"]),
        help="Format to export data in",
        default="table",
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--table-format",
        "table_format",
        default=TABLE_FORMAT,
        help="Base format to use for --export-format=table",
        type=click.Choice(tabulate.tabulate_formats),
        show_envvar=True,
        show_default=True,
    )
    @click.pass_context
    def get_fetch_history(
        ctx,
        url: str,
        key: str,
        secret: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        past_minutes: Optional[int] = None,
        adapters: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        clients: Optional[List[str]] = None,
        exclude_realtime: bool = False,
        export_format: str = "table",
        table_format: str = TABLE_FORMAT,
    ):
        """Process business_units assets using regex searches against fields."""
        client = ctx.obj.start_client(url=url, key=key, secret=secret)
        client.adapters.fetch_history = FetchHistory(auth=client.AUTH)

        with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
            data = client.adapters.fetch_history.get(
                date_from=date_from,
                date_to=date_to,
                past_minutes=past_minutes,
                adapters=adapters,
                statuses=statuses,
                clients=clients,
                exclude_realtime=exclude_realtime,
            )

        if export_format == "json":
            rows = [x.to_dict() for x in data]
            content = json_dump(rows)
            click.secho(content)
            ctx.exit(0)

        if export_format == "str":
            rows = [str(x) for x in data]
            joiner = "\n\n{}\n".format("-" * 80)
            content = joiner.join(rows)
            click.secho(content)
            ctx.exit(0)

        if export_format == "csv":
            rows = [x.to_tablize() for x in data]
            columns = AdapterFetchHistory.columns()
            stream = io.StringIO()
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writerow(dict(zip(columns, columns)))
            writer.writerows(rows)
            content = stream.getvalue()
            stream.close()
            click.secho(content)

        if export_format == "table":
            rows = [x.to_tablize() for x in data]
            content = tablize(value=rows, fmt=table_format)
            click.secho(content)

        ctx.exit(1)

    grp_adapters.adapters.add_command(get_fetch_history)
    cli()


if __name__ == "__main__" and not CLI_MODE:
    client_args = {}

    # --- get the URL, API key, API secret, & certwarn from the default ".env" file
    client_args.update(axonapi.get_env_connect())

    # 0--- OR override OS env vars with the values from a custom .env file
    # client_args.update(axonapi.get_env_connect(ax_env="/path/to/envfile", override=True))

    # --- OR supply them here in the script
    # client_args["url"] = "10.20.0.94"
    # client_args["key"] = ""
    # client_args["secret"] = ""

    # client_args["log_console"] = True  # enable logging to console
    # client_args["log_request_attrs"] = "all"  # log all request attributes
    # client_args["log_request_body"] = True  # log all request bodies
    # client_args["log_response_attrs"] = "all"  # log all response attributes
    # client_args["log_response_body"] = True  # log all response bodies

    client = axonapi.Connect(**client_args)  # create a client

    # client.activity_logs          # get audit logs
    # client.adapters               # get adapters and update adapter settings
    # client.adapters.cnx           # CRUD for adapter connections
    # client.cnx                    # CRUD for adapter connections
    # client.dashboard              # get/start/stop discovery cycles
    # client.devices                # get device assets
    # client.devices.fields         # get field schemas for device assets
    # client.devices.labels         # add/remove/get tags for device assets
    # client.devices.saved_queries  # CRUD for saved queries for device assets
    # client.enforcements           # work with Enforcement Center
    # client.instances              # get instances and instance meta data
    # client.meta                   # get product meta data
    # client.openapi                # work with OpenAPI Specification
    # client.remote_support         # enable/disable remote support settings
    # client.settings_global        # get/update global system settings
    # client.settings_gui           # get/update gui system settings
    # client.settings_ip            # get/update identity provider system settings
    # client.settings_lifecycle     # get/update lifecycle system settings
    # client.signup                 # perform initial signup and use password reset tokens
    # client.system_roles           # CRUD for system roles
    # client.system_users           # CRUD for system users
    # client.users                  # get user assets
    # client.users.fields           # get field schemas for user assets
    # client.users.labels           # add/remove/get tags for user assets
    # client.users.saved_queries    # CRUD for saved queries for user assets

    client.adapters.fetch_history = FetchHistory(auth=client.AUTH)

    client.start()  # connect to axonius
    j = client.jdump  # json dump helper

    history = client.adapters.fetch_history.get()
    tables = [x.to_tablize() for x in history]
    tabled = tablize(value=tables)
    print(tabled)
