# -*- coding: utf-8 -*-
"""API model mixin for device and user assets."""
import datetime
import pathlib
import time
import types
import typing as t
import uuid

import cachetools

from ...constants.api import DEFAULT_CALLBACKS_CLS, MAX_PAGE_SIZE, PAGE_SIZE
from ...constants.fields import AXID
from ...exceptions import ApiError, NotFoundError, ResponseNotOk, StopFetch
from ...parsers.grabber import Grabber
from ...tools import PathLike, dt_now, dt_now_file, get_subcls, json_dump, listify
from ..api_endpoints import ApiEndpoint, ApiEndpoints
from ..asset_callbacks.tools import Base as BaseCallbacks
from ..asset_callbacks.tools import get_callbacks_cls
from ..json_api.assets import (
    AssetById,
    AssetRequest,
    AssetsPage,
    AssetTypeHistoryDates,
    Count,
    CountRequest,
    HistoryDates,
)
from ..mixins import ModelMixins
from ..wizards import Wizard, WizardCsv, WizardText
from .runner import ENFORCEMENT, Runner

GEN_TYPE = t.Union[t.Generator[dict, None, None], t.List[dict]]
HISTORY_DATES_OBJ_CACHE = cachetools.TTLCache(maxsize=1, ttl=300)
HISTORY_DATES_CACHE = cachetools.TTLCache(maxsize=1, ttl=300)


# noinspection PyAttributeOutsideInit,PyShadowingBuiltins
class AssetMixin(ModelMixins):
    """API model mixin for device and user assets.

    Examples:

        * Get count of assets: :meth:`count`
        * Get count of assets from a saved query: :meth:`count_by_saved_query`
        * Get assets: :meth:`get`
        * Get assets from a saved query: :meth:`get_by_saved_query`
        * Get the full data set for a single asset: :meth:`get_by_id`
        * Work with saved queries: :obj:`axonius_api_client.api.assets.saved_query.SavedQuery`
        * Work with fields: :obj:`axonius_api_client.api.assets.fields.Fields`
        * Work with tags: :obj:`axonius_api_client.api.assets.labels.Labels`

    See Also:
        This object is not usable directly, it only stores the logic that is common for working
        with the various asset types:

        * Device assets :obj:`axonius_api_client.api.assets.devices.Devices`
        * User assets :obj:`axonius_api_client.api.assets.users.Users`
    """

    ASSET_TYPE: str = ""

    @classmethod
    def asset_types(cls) -> t.List[str]:
        """Pass."""
        return [x.ASSET_TYPE for x in cls.asset_modules()]

    @classmethod
    def asset_modules(cls) -> t.List[t.Type["AssetMixin"]]:
        """Pass."""
        return get_subcls(AssetMixin)

    def run_enforcement(
        self,
        eset: ENFORCEMENT,
        ids: t.Union[str, t.List[str]],
        verify_and_run: bool = True,
        verified: bool = False,
        verify_count: bool = True,
        prompt: bool = False,
        do_echo: bool = False,
        refetch: bool = False,
        src_query: t.Optional[str] = None,
        src_fields: t.Optional[t.List[str]] = None,
        check_stdin: bool = True,
        grabber: t.Optional[Grabber] = None,
    ) -> Runner:
        """Run an enforcement set against a manually selected list of assets.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> WIZ: str = "simple os.type equals Windows"  # "query of assets to target"
            >>> ESET: str = "test"  # "name or uuid of enforcement set"

            Get a list of assets from a query and manually extract the IDs.
            We know assets are valid because we just got them, so we pass verified=True.
            >>> ITEMS: list[dict] = apiobj.get(wiz_entries=WIZ)
            >>> IDS: list[str] = list(map(lambda x: x['internal_axon_id'], ITEMS))
            >>> RUNNER: Runner = apiobj.run_enforcement(eset=ESET, ids=IDS, verified=True)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=None,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=None,
            )

        Args:
            eset (ENFORCEMENT): name, uuid, or Enforcement Set object to run
            ids (t.Union[str, t.List[str]]): Asset IDs to run Enforcement Set against,
                csv-like string or list of csv-like strings
            verify_and_run (bool, optional): if false, return the Runner object
                to use manually. if true, run :method:`Runner.verify_and_run`
                before returning the Runner object
            verified (bool): $ids already verified, just run $eset against $ids
            verify_count (bool): Verify that the count of $query equals the count of $ids
            prompt (bool): Prompt user for verification when applicable.
            do_echo (bool): Echo output to console as well as log
            refetch (bool): refetch $eset even if it is already a model
            src_query (str): query to use to get $ids
            src_fields (list): fields to use to get $ids
            check_stdin (bool): error if stdin is a TTY when prompting
            grabber: (grabber): Grabber used to get IDs

        Returns:
            Runner: Runner object used to verify and run $eset
        """
        runner = Runner(
            apiobj=self,
            eset=eset,
            ids=ids,
            verified=verified,
            verify_count=verify_count,
            prompt=prompt,
            do_echo=do_echo,
            refetch=refetch,
            src_query=src_query,
            src_fields=src_fields,
            grabber=grabber,
            check_stdin=check_stdin,
        )
        if verify_and_run:
            runner.verify_and_run()
        return runner

    def run_enforcement_from_items(
        self,
        eset: ENFORCEMENT,
        items: t.Union[str, t.List[str], dict, t.List[dict], types.GeneratorType],
        keys: t.Optional[t.Union[str, t.List[str]]] = None,
        do_echo_grab: bool = True,
        do_raise_grab: bool = False,
        **kwargs,
    ) -> Runner:
        """Get Asset IDs from a list of dicts or strs and run $eset against them.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> WIZ: str = "simple os.type equals Windows"  # "query of assets to target"
            >>> ESET: str = "test"  # "name or uuid of enforcement set"

            Get a list of assets from a query and use the grabber get the IDs.
            We know assets are valid because we just got them, so we pass verified=True.
            >>> ITEMS: list[dict] = apiobj.get(wiz_entries=WIZ)
            >>> RUNNER: Runner = apiobj.run_enforcement_from_items(eset=ESET, items=ITEMS,
            ... verified=True)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=None,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=Grabber(
              count_supplied=31,
              count_found=31,
              do_echo=True,
              do_raise=False,
              source=None,
            )

        Args:
            eset (ENFORCEMENT): name, uuid, or Enforcement Set object to run
            items (t.Union[str, t.List[str], dict, t.List[dict], types.GeneratorType]): list of
                strs or dicts to grab Asset IDs from
            keys (t.Union[str, t.List[str]]): additional keys for grabber to look for Asset IDs in
            do_echo_grab (bool, optional): Echo output of Asset ID grabber to console as well as log
            do_raise_grab (bool, optional): Throw an error if grabber fails to find an Asset ID
                in any items
            **kwargs: passed to :method:`run_enforcement`

        Returns:
            Runner: Runner object used to verify and run $eset
        """
        kwargs["grabber"] = grabber = Grabber(
            items=items,
            keys=keys,
            do_echo=do_echo_grab,
            do_raise=do_raise_grab,
            source=kwargs.pop("source", None),
        )
        kwargs["ids"] = grabber.axids
        return self.run_enforcement(eset=eset, **kwargs)

    def run_enforcement_from_json(
        self,
        eset: ENFORCEMENT,
        items: t.Union[str, bytes, t.IO, pathlib.Path],
        keys: t.Optional[t.Union[str, t.List[str]]] = None,
        do_echo_grab: bool = True,
        do_raise_grab: bool = False,
        **kwargs,
    ) -> Runner:
        """Get Asset IDs from a JSON string with a list of dicts and run $eset against them.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> WIZ: str = "simple os.type equals Windows"  # "query of assets to target"
            >>> ESET: str = "test"  # "name or uuid of enforcement set"

            Get a list of assets from a query and export the assets to a JSON str
            then run an enforcement against all asset IDs from the JSON str.
            We know assets are valid because we just got them, so we pass verified=True.
            >>> import io
            >>> FH = io.StringIO()
            >>> _ = apiobj.get(wiz_entries=WIZ, export="json", export_fd=FH, export_fd_close=False)
            >>> FH.seek(0)
            >>> ITEMS: str = FH.getvalue()
            >>> RUNNER: Runner = apiobj.run_enforcement_from_json(eset=ESET, items=ITEMS,
            ... verified=True)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=None,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=Grabber(
              count_supplied=31,
              count_found=31,
              do_echo=True,
              do_raise=False,
              source='from_json items type=str, length=15519 post_load type=list, length=31',
            ),
            )

            Get a list of assets from a query and export the assets to a JSON file
            then run an enforcement against all asset IDs from the JSON file.
            We know assets are valid because we just got them, so we pass verified=True.
            >>> import pathlib
            >>> PATH: pathlib.Path = pathlib.Path("data.json")
            >>> _ = apiobj.get(wiz_entries=WIZ, export="json", export_file=PATH)
            >>> RUNNER: Runner = apiobj.run_enforcement_from_json(eset=ESET, items=PATH,
            ... verified=True)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=None,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=Grabber(
              count_supplied=31,
              count_found=31,
              do_echo=True,
              do_raise=False,
              source='from_json items type=PosixPath, length=None post_load type=list, length=31',
            ),
            )

        Args:
            eset (ENFORCEMENT): name, uuid, or Enforcement Set object to run
            items (t.Union[str, bytes, t.IO, pathlib.Path]): json str, handle for file containing
                json str, or pathlib.Path of path containing json str
            keys (t.Union[str, t.List[str]]): additional keys for grabber to look for Asset IDs in
            do_echo_grab (bool, optional): Echo output of Asset ID grabber to console as well as log
            do_raise_grab (bool, optional): Throw an error if grabber fails to find an Asset ID
                in any items
            **kwargs: passed to :method:`run_enforcement`

        Returns:
            Runner: Runner object used to verify and run $eset
        """
        kwargs["grabber"] = grabber = Grabber.from_json(
            items=items,
            keys=keys,
            do_echo=do_echo_grab,
            do_raise=do_raise_grab,
            source=kwargs.pop("source", None),
        )
        kwargs["ids"] = grabber.axids
        return self.run_enforcement(eset=eset, **kwargs)

    def run_enforcement_from_jsonl(
        self,
        eset: ENFORCEMENT,
        items: t.Union[str, bytes, t.IO, pathlib.Path],
        keys: t.Optional[t.Union[str, t.List[str]]] = None,
        do_echo_grab: bool = True,
        do_raise_grab: bool = False,
        **kwargs,
    ) -> Runner:
        """Get Asset IDs from a JSONL string with one dict per line and run $eset against them.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> WIZ: str = "simple os.type equals Windows"  # "query of assets to target"
            >>> ESET: str = "test"  # "name or uuid of enforcement set"

            Get a list of assets from a query and export the assets to a JSONL str
            then run an enforcement against all asset IDs from the JSONL str.
            We know assets are valid because we just got them, so we pass verified=True.
            >>> import io
            >>> FH = io.StringIO()
            >>> _ = apiobj.get(wiz_entries=WIZ, export="json", json_flat=True,
            ... export_fd=FH, export_fd_close=False)
            >>> FH.seek(0)
            >>> RUNNER: Runner = apiobj.run_enforcement_from_jsonl(eset=ESET, items=FH,
            ... verified=True)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=None,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=Grabber(
              count_supplied=31,
              count_found=31,
              do_echo=True,
              do_raise=False,
              source='from_jsonl items type=StringIO, length=None post_load type=list, length=31',
            ),
            )

            Get a list of assets from a query and export the assets to a JSONL file
            then run an enforcement against all asset IDs from the JSONL file.
            We know assets are valid because we just got them, so we pass verified=True.
            >>> import pathlib
            >>> PATH = pathlib.Path("data.jsonl")
            >>> _ = apiobj.get(
            ...  wiz_entries=WIZ, export="json", json_flat=True, export_file=PATH,
            ... export_overwrite=True)
            >>> RUNNER: Runner = apiobj.run_enforcement_from_jsonl(eset=ESET, items=PATH,
            ... verified=True)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=None,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=Grabber(
              count_supplied=31,
              count_found=31,
              do_echo=True,
              do_raise=False,
              source='from_jsonl items type=PosixPath, length=None post_load type=list, length=31',
            ),
            )

        Args:
            eset (ENFORCEMENT): name, uuid, or Enforcement Set object to run
            items (t.Union[str, bytes, t.IO, pathlib.Path]): jsonl str, handle for file containing
                jsonl str, or pathlib.Path of path containing jsonl str
            keys (t.Union[str, t.List[str]]): additional keys for grabber to look for Asset IDs in
            do_echo_grab (bool, optional): Echo output of Asset ID grabber to console as well as log
            do_raise_grab (bool, optional): Throw an error if grabber fails to find an Asset ID
                in any items
            **kwargs: passed to :method:`run_enforcement`

        Returns:
            Runner: Runner object used to verify and run $eset
        """
        kwargs["grabber"] = grabber = Grabber.from_jsonl(
            items=items,
            keys=keys,
            do_echo=do_echo_grab,
            do_raise=do_raise_grab,
            source=kwargs.pop("source", None),
        )
        kwargs["ids"] = grabber.axids
        return self.run_enforcement(eset=eset, **kwargs)

    def run_enforcement_from_csv(
        self,
        eset: ENFORCEMENT,
        items: t.Union[str, bytes, t.IO, pathlib.Path],
        keys: t.Optional[t.Union[str, t.List[str]]] = None,
        do_echo_grab: bool = True,
        do_raise_grab: bool = False,
        load_args: t.Optional[dict] = None,
        **kwargs,
    ) -> Runner:
        """Get Asset IDs from a CSV string and run $eset against them.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> WIZ: str = "simple os.type equals Windows"  # "query of assets to target"
            >>> ESET: str = "test"  # "name or uuid of enforcement set"

            Get a list of assets from a query and export the assets to a JSONL str
            then run an enforcement against all asset IDs from the JSONL str.
            We can also use a CSV file exported from the GUI.
            We know assets are valid because we just got them, so we pass verified=True.

            >>> import io
            >>> FH: io.StringIO = io.StringIO()
            >>> _ = apiobj.get(wiz_entries=WIZ, export="csv", export_fd=FH, export_fd_close=False)
            >>> FH.seek(0)
            >>> ITEMS: str = axonapi.tools.bom_strip(FH.getvalue())
            >>> RUNNER: Runner = apiobj.run_enforcement_from_csv(eset=ESET, items=ITEMS,
            ... verified=True)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=None,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=Grabber(
              count_supplied=33,
              count_found=31,
              do_echo=True,
              do_raise=False,
              source='from_csv items type=str, length=6556 post_load type=list, length=33',
            ),
            )

            Get a list of assets from a query and export the assets to a CSV file
            then run an enforcement against all asset IDs from the CSV file.
            We can also use a CSV file exported from the GUI.
            We know assets are valid because we just got them, so we pass verified=True.
            >>> import pathlib
            >>> PATH: pathlib.Path = pathlib.Path("data.csv")
            >>> _ = apiobj.get(wiz_entries=WIZ, export="csv", export_file=PATH)
            >>> RUNNER: Runner = apiobj.run_enforcement_from_csv(eset=ESET, items=PATH,
            ... verified=True)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=None,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=Grabber(
              count_supplied=33,
              count_found=31,
              do_echo=True,
              do_raise=False,
              source='from_csv items type=PosixPath, length=None post_load type=list, length=33',
            ),
            )

        Args:
            eset (ENFORCEMENT): name, uuid, or Enforcement Set object to run
            items (t.Union[str, bytes, t.IO, pathlib.Path]): csv str, handle for file containing
                csv str, or pathlib.Path of path containing csv str
            keys (t.Union[str, t.List[str]]): additional keys for grabber to look for Asset IDs in
            do_echo_grab (bool, optional): Echo output of Asset ID grabber to console as well as log
            do_raise_grab (bool, optional): Throw an error if grabber fails to find an Asset ID
                in any items
            load_args: passed to :func:`pandas.read_csv`
            **kwargs: passed to :method:`run_enforcement`

        Returns:
            Runner: Runner object used to verify and run $eset
        """
        kwargs["grabber"] = grabber = Grabber.from_csv(
            items=items,
            keys=keys,
            do_echo=do_echo_grab,
            do_raise=do_raise_grab,
            load_args=load_args,
            source=kwargs.pop("source", None),
        )
        kwargs["ids"] = grabber.axids
        return self.run_enforcement(eset=eset, **kwargs)

    def run_enforcement_from_text(
        self,
        eset: ENFORCEMENT,
        items: t.Union[str, bytes, t.IO, pathlib.Path],
        keys: t.Optional[t.Union[str, t.List[str]]] = None,
        do_echo_grab: bool = True,
        do_raise_grab: bool = False,
        **kwargs,
    ) -> Runner:
        r"""Get Asset IDs from a text string and run $eset against them.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> WIZ: str = "simple os.type equals Windows"  # "query of assets to target"
            >>> ESET: str = "test"  # "name or uuid of enforcement set"

            Get a list of assets from a query and export the assets to a text file
            then run an enforcement against all asset IDs from the text file.
            All lines will have any non-alphanumeric characters removed from them and if a
            32 character alphanumeric string is found it is considered an Asset ID.
            We know assets are valid because we just got them, so we pass verified=True.
            >>> import pathlib
            >>> PATH: pathlib.Path = pathlib.Path("data.txt")
            >>> ITEMS: list[dict] = apiobj.get(wiz_entries=WIZ)
            >>> IDS: list[str] = list(map(lambda x: x['internal_axon_id'], ITEMS))
            >>> PATH.write_text('\n'.join(IDS))
            >>> RUNNER: Runner = apiobj.run_enforcement_from_text(
            ... eset=ESET, items=PATH, verified=True)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=None,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=Grabber(
              count_supplied=31,
              count_found=31,
              do_echo=True,
              do_raise=False,
              source='from_text items type=PosixPath, length=None',
            ),
            )

        Args:
            eset (ENFORCEMENT): name, uuid, or Enforcement Set object to run
            items (t.Union[str, bytes, t.IO, pathlib.Path]): text str, handle for file containing
                text str, or pathlib.Path of path containing text str
            keys (t.Union[str, t.List[str]]): n/a
            do_echo_grab (bool, optional): Echo output of Asset ID grabber to console as well as log
            do_raise_grab (bool, optional): Throw an error if grabber fails to find an Asset ID
                in any items
            **kwargs: passed to :method:`run_enforcement`

        Returns:
            Runner: Runner object used to verify and run $eset
        """
        kwargs["grabber"] = grabber = Grabber.from_text(
            items=items,
            keys=keys,
            do_echo=do_echo_grab,
            do_raise=do_raise_grab,
            source=kwargs.pop("source", None),
        )
        kwargs["ids"] = grabber.axids
        return self.run_enforcement(eset=eset, **kwargs)

    def run_enforcement_from_json_path(
        self,
        eset: ENFORCEMENT,
        path: PathLike,
        keys: t.Optional[t.Union[str, t.List[str]]] = None,
        do_echo_grab: bool = True,
        do_raise_grab: bool = False,
        **kwargs,
    ) -> Runner:
        """Get Asset IDs from a JSON file with a list of dicts and run $eset against them.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> ESET: str = "test"  # "name or uuid of enforcement set"

            Run an enforcement against all asset IDs from a JSON file.
            We are unsure if Asset IDs are still valid for this instance of Axonius, so
            we do not pass verified=True.
            >>> PATH: str = "data.json"
            >>> RUNNER: Runner = apiobj.run_enforcement_from_json_path(eset=ESET, path=PATH)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=31,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=Grabber(
              count_supplied=31,
              count_found=31,
              do_echo=True,
              do_raise=False,
              source='from_json_path /Users/jimbo/gh/Axonius/axonapi/data.json /
            from_json items type=PosixPath, length=None post_load
            type=list, length=31',
            ),
            )

        Args:
            eset (ENFORCEMENT): name, uuid, or Enforcement Set object to run
            path (PathLike): str or pathlib.Path of path containing json str
            keys (t.Union[str, t.List[str]]): additional keys for grabber to look for Asset IDs in
            do_echo_grab (bool, optional): Echo output of Asset ID grabber to console as well as log
            do_raise_grab (bool, optional): Throw an error if grabber fails to find an Asset ID
                in any items
            **kwargs: passed to :method:`run_enforcement`

        Returns:
            Runner: Runner object used to verify and run $eset
        """
        kwargs["grabber"] = grabber = Grabber.from_json_path(
            path=path,
            keys=keys,
            do_echo=do_echo_grab,
            do_raise=do_raise_grab,
            source=kwargs.pop("source", None),
        )
        kwargs["ids"] = grabber.axids
        return self.run_enforcement(eset=eset, **kwargs)

    def run_enforcement_from_jsonl_path(
        self,
        eset: ENFORCEMENT,
        path: PathLike,
        keys: t.Optional[t.Union[str, t.List[str]]] = None,
        do_echo_grab: bool = True,
        do_raise_grab: bool = False,
        **kwargs,
    ) -> Runner:
        """Get Asset IDs from a JSONL file with one dict per line and run $eset against them.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> ESET: str = "test"  # "name or uuid of enforcement set"

            Run an enforcement against all asset IDs from a JSONL file.
            We are unsure if Asset IDs are still valid for this instance, so
            we do not pass verified=True.
            >>> PATH: str = "data.jsonl"
            >>> RUNNER: Runner = apiobj.run_enforcement_from_jsonl_path(eset=ESET, path=PATH)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=31,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=Grabber(
              count_supplied=31,
              count_found=31,
              do_echo=True,
              do_raise=False,
              source='from_jsonl_path /Users/jimbo/gh/Axonius/axonapi/data.jsonl /
            from_jsonl items type=PosixPath, length=None post_load type=list, length=31',
            ),
            )

        Args:
            eset (ENFORCEMENT): name, uuid, or Enforcement Set object to run
            path (PathLike): str or pathlib.Path of path containing jsonl str
            keys (t.Union[str, t.List[str]]): additional keys for grabber to look for Asset IDs in
            do_echo_grab (bool, optional): Echo output of Asset ID grabber to console as well as log
            do_raise_grab (bool, optional): Throw an error if grabber fails to find an Asset ID
                in any items
            **kwargs: passed to :method:`run_enforcement`

        Returns:
            Runner: Runner object used to verify and run $eset
        """
        kwargs["grabber"] = grabber = Grabber.from_jsonl_path(
            path=path,
            keys=keys,
            do_echo=do_echo_grab,
            do_raise=do_raise_grab,
            source=kwargs.pop("source", None),
        )
        kwargs["ids"] = grabber.axids
        return self.run_enforcement(eset=eset, **kwargs)

    def run_enforcement_from_csv_path(
        self,
        eset: ENFORCEMENT,
        path: PathLike,
        keys: t.Optional[t.Union[str, t.List[str]]] = None,
        do_echo_grab: bool = True,
        do_raise_grab: bool = False,
        **kwargs,
    ) -> Runner:
        """Get Asset IDs from a CSV file and run $eset against them.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> ESET: str = "test"  # "name or uuid of enforcement set"

            Run an enforcement against all asset IDs from a JSONL file.
            We are unsure if Asset IDs are still valid for this instance,
            so we do not pass verified=True.
            >>> PATH: str = "data.csv"
            >>> RUNNER: Runner = apiobj.run_enforcement_from_csv_path(eset=ESET, path=PATH)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=31,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=Grabber(
              count_supplied=33,
              count_found=31,
              do_echo=True,
              do_raise=False,
              source='from_csv_path /Users/jimbo/gh/Axonius/axonapi/data.csv /
            from_csv items type=PosixPath, length=None post_load type=list, length=33',
            ),
            )

        Args:
            eset (ENFORCEMENT): name, uuid, or Enforcement Set object to run
            path (PathLike): str or pathlib.Path of path containing csv str
            keys (t.Union[str, t.List[str]]): additional keys for grabber to look for Asset IDs in
            do_echo_grab (bool, optional): Echo output of Asset ID grabber to console as well as log
            do_raise_grab (bool, optional): Throw an error if grabber fails to find an Asset ID
                in any items
            **kwargs: passed to :method:`run_enforcement`

        Returns:
            Runner: Runner object used to verify and run $eset
        """
        kwargs["grabber"] = grabber = Grabber.from_csv_path(
            path=path,
            keys=keys,
            do_echo=do_echo_grab,
            do_raise=do_raise_grab,
            source=kwargs.pop("source", None),
        )
        kwargs["ids"] = grabber.axids
        return self.run_enforcement(eset=eset, **kwargs)

    def run_enforcement_from_text_path(
        self,
        eset: ENFORCEMENT,
        path: PathLike,
        keys: t.Optional[t.Union[str, t.List[str]]] = None,
        do_echo_grab: bool = True,
        do_raise_grab: bool = False,
        **kwargs,
    ) -> Runner:
        """Get Asset IDs from a text file and run $eset against them.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> ESET: str = "test"  # "name or uuid of enforcement set"

            Run an enforcement against all asset IDs from a text file.
            All lines will have any non-alphanumeric characters removed from them and if a
            32 character alphanumeric string is found it is considered an Asset ID.
            We are unsure if Asset IDs are still valid for this instance, so
            we do not pass verified=True.
            >>> PATH: str = "data.txt"
            >>> RUNNER: Runner = apiobj.run_enforcement_from_text_path(eset=ESET, path=PATH)
            >>> print(RUNNER)
            Runner(
              state='Ran Enforcement Set against 31 supplied Asset IDs',
              eset='test',
              executed=True,
              count_ids=31,
              count_result=None,
              verified=True,
              verify_count=True,
              prompt=False,
              grabber=Grabber(
              count_supplied=31,
              count_found=31,
              do_echo=True,
              do_raise=False,
              source='from_text_path /Users/jimbo/gh/Axonius/axonapi/data.txt /
            from_text items type=PosixPath, length=None post_load type=generator, length=None',
            ),
            )

        Args:
            eset (ENFORCEMENT): name, uuid, or Enforcement Set object to run
            path (PathLike): str or pathlib.Path of path containing text str
            keys (t.Union[str, t.List[str]]): n/a
            do_echo_grab (bool, optional): Echo output of Asset ID grabber to console as well as log
            do_raise_grab (bool, optional): Throw an error if grabber fails to find an Asset ID
                in any items
            **kwargs: passed to :method:`run_enforcement`

        Returns:
            Runner: Runner object used to verify and run $eset
        """
        kwargs["grabber"] = grabber = Grabber.from_text_path(
            path=path,
            keys=keys,
            do_echo=do_echo_grab,
            do_raise=do_raise_grab,
            source=kwargs.pop("source", None),
        )
        kwargs["ids"] = grabber.axids
        return self.run_enforcement(eset=eset, **kwargs)

    @property
    def enforcements(self):
        """Work with enforcements."""
        if not hasattr(self, "_enforcements"):
            from ..enforcements import Enforcements

            self._enforcements: Enforcements = Enforcements(auth=self.auth)
        return self._enforcements

    # noinspection PyUnusedLocal
    def count(
        self,
        query: t.Optional[str] = None,
        history_date: t.Optional[t.Union[str, datetime.timedelta, datetime.datetime]] = None,
        history_days_ago: t.Optional[int] = None,
        history_exact: bool = False,
        wiz_entries: t.Optional[t.Union[t.List[dict], t.List[str], dict, str]] = None,
        wiz_parsed: t.Optional[t.List[dict]] = None,
        history_date_parsed: t.Optional[str] = None,
        use_cache_entry: bool = False,
        use_heavy_fields_collection: bool = False,
        frontend_sent_time: t.Optional[datetime.datetime] = None,
        query_id: t.Optional[t.Union[str, uuid.UUID]] = None,
        saved_query_id: t.Optional[str] = None,
        request_obj: t.Optional[CountRequest] = None,
        http_args: t.Optional[dict] = None,
        sleep: t.Optional[t.Union[int, float]] = 0.5,
        **kwargs,
    ) -> int:
        """Get the count of assets from a query.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            Get count of all assets
            >>> path: int = apiobj.count()
            Get count of all assets for a given date
            >>> path: int = apiobj.count(history_date="2020-09-29")
            Get count of assets matching a query built by the GUI query wizard
            >>> use_query: str = '(specific_data.data.name == "test")'
            >>> path: int = apiobj.count(query=use_query)
            Get count of assets matching a query built by the API client query wizard
            >>> entries: str = 'simple name equals test'
            >>> path: int = apiobj.count(wiz_entries=entries)
            Same as above but using a list of dicts instead of a string for wiz_entries
            >>> entries: t.List[dict] = [{'type': 'simple', 'path': 'name equals test'}]
            >>> path: int = apiobj.count(wiz_entries=entries)

        Args:
            query: only return the count of assets that match the query
            history_date: return asset count for a given historical date
            history_days_ago: return asset count for a given historical date that is N days ago
            history_exact: if True, return the exact asset count for a given historical date
                if False, return the asset count for the closest historical date
            wiz_entries: build a query from the entries and return the count of
                assets that match the query
            wiz_parsed: previously parsed wiz_entries
            history_date_parsed: previously parsed history_date
            use_cache_entry: if True, use the last query that was run to get the count
            use_heavy_fields_collection: if True, use the HEAVV fields collection to get the count
            frontend_sent_time: time that the query was sent from the frontend
            query_id: ID to identify this query
            saved_query_id: ID of saved query that count is being issued for
            request_obj: request object to use instead of building one
            http_args: args to pass to http request
            sleep: time to sleep between requests
            **kwargs: sent to :meth:`build_count_request`
        """
        request_obj = self.build_count_request(
            request_obj=request_obj,
            filter=query,
            history=history_date_parsed,
            use_cache_entry=use_cache_entry,
            saved_query_id=saved_query_id,
            query_id=query_id,
            use_heavy_fields_collection=use_heavy_fields_collection,
            frontend_sent_time=frontend_sent_time,
            **kwargs,
        )
        if not isinstance(http_args, dict):
            http_args = {}
        if not isinstance(wiz_parsed, dict):
            wiz_parsed = self.get_wiz_entries(wiz_entries=wiz_entries)
        if isinstance(wiz_parsed, dict):
            wiz_query: t.Optional[str] = wiz_parsed.get("query")
            if isinstance(wiz_query, str) and wiz_query:
                request_obj.filter = wiz_query
        if not history_date_parsed and not request_obj.history:
            request_obj.history = self.get_history_date(
                date=history_date, days_ago=history_days_ago, exact=history_exact
            )
        count: t.Optional[int] = None
        while not isinstance(count, int):
            response: Count = self._count(request_obj=request_obj, http_args=http_args)
            count: t.Optional[int] = response.value
            if isinstance(count, int):
                break
            request_obj.use_cache_entry = True
            if isinstance(sleep, (int, float)):
                time.sleep(sleep)
        return count

    def count_by_saved_query(self, name: str, **kwargs) -> int:
        """Get the count of assets for a query defined in a saved query.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            Get count of assets returned from a saved query
            >>> count: int = apiobj.count_by_saved_query(name="test")
            Get count of assets returned from a saved query for a given date
            >>> count: int = apiobj.count_by_saved_query(name="test", history_date="2020-09-29")

        Args:
            name: saved query to get count of assets from
            kwargs: supplied to :meth:`count`
        """
        sq = self.saved_query.get_by_multi(sq=name)
        _view: dict = sq.get("view", {})
        _query: dict = _view.get("query", {})
        kwargs["query"]: t.Optional[str] = _query.get("filter")
        kwargs["saved_query_id"] = sq["id"]
        return self.count(**kwargs)

    def get(self, generator: bool = False, **kwargs) -> GEN_TYPE:
        r"""Get assets from a query.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            Get all assets with the default fields defined in the API client
            >>> assets: list[dict] = apiobj.get()
            Get all assets using a generator
            >>> assets: list[dict] = list(apiobj.get(generator=True))
            Get all assets and include more fields
            >>> fields: list[str] = ["os.type", "aws:aws_device_type"]
            >>> assets: list[dict] = apiobj.get(fields=fields)
            Get all assets and include fields that fuzzy match names and no default fields
            >>> fields_fuzzy: list[str] = ["last", "os"]
            >>> assets: list[dict] = apiobj.get(fields_fuzzy=fields_fuzzy, fields_default=False)
            Get all assets and include fields that regex match names a
            >>> fields_regex: list[str] = ["^os\."]
            >>> assets: list[dict] = apiobj.get(fields_regex=fields_regex)
            Get all assets and include all root fields for an adapter
            >>> assets: list[dict] = apiobj.get(fields_root="aws")
            Get all assets for a given date in history and sort the rows on a field
            >>> assets: list[dict] = apiobj.get(history_date="2020-09-29", sort_field="name")
            Get all assets with details of which adapter connection provided the aggregated data
            >>> assets: list[dict] = apiobj.get(include_details=True)
            Get assets matching a query built by the GUI query wizard
            >>> query: str ='(specific_data.data.name == "test")'
            >>> assets: list[dict] = apiobj.get(query=query)
            Get assets matching a query built by the API client query wizard
            >>> wiz_entries: list[dict] = [{'type': 'simple', 'path': 'name equals test'}]
            >>> assets: list[dict] = apiobj.get(wiz_entries=wiz_entries)

        See Also:
            This method is used by all other get* methods under the hood and their kwargs are
            passed through to this method and passed to :meth:`get_generator` which are then passed
            to whatever callback is used based on the ``export`` argument.

            If ``export`` is not supplied, see
            :meth:`axonius_api_client.api.asset_callbacks.base.Base.args_map`.

            If ``export`` equals ``json``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_json.Json.args_map`.

            If ``export`` equals ``csv``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_csv.Csv.args_map`.

            If ``export`` equals ``json_to_csv``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_json_to_csv.JsonToCsv.args_map`.

            If ``export`` equals ``table``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_table.Table.args_map`.

            If ``export`` equals ``xlsx``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_xlsx.Xlsx.args_map`.

            :obj:`axonius_api_client.constants.asset_helpers.ASSET_HELPERS` for a list of
            helpers that translate between GUI titles, API request attributes, and saved query
            paths.

        Args:
            generator: return an iterator for assets that will yield rows as they are fetched
            **kwargs: passed to :meth:`get_generator`
        """
        gen = self.get_generator(**kwargs)
        return gen if generator else list(gen)

    def get_generator(
        self,
        query: t.Optional[str] = None,
        fields: t.Optional[t.Union[t.List[str], str]] = None,
        fields_manual: t.Optional[t.Union[t.List[str], str]] = None,
        fields_regex: t.Optional[t.Union[t.List[str], str]] = None,
        fields_regex_root_only: bool = True,
        fields_fuzzy: t.Optional[t.Union[t.List[str], str]] = None,
        fields_default: bool = True,
        fields_root: t.Optional[str] = None,
        fields_error: bool = True,
        max_rows: t.Optional[int] = None,
        max_pages: t.Optional[int] = None,
        row_start: int = 0,
        page_size: int = MAX_PAGE_SIZE,
        page_start: int = 0,
        page_sleep: int = 0,
        export: str = DEFAULT_CALLBACKS_CLS,
        sort_field: t.Optional[str] = None,
        sort_descending: bool = False,
        history_date: t.Optional[t.Union[str, datetime.timedelta, datetime.datetime]] = None,
        history_days_ago: t.Optional[int] = None,
        history_exact: bool = False,
        wiz_entries: t.Optional[t.Union[t.List[dict], t.List[str], dict, str]] = None,
        wiz_parsed: t.Optional[dict] = None,
        file_date: t.Optional[str] = None,
        use_heavy_fields_collection: bool = False,
        sort_field_parsed: t.Optional[str] = None,
        search: t.Optional[str] = None,
        history_date_parsed: t.Optional[str] = None,
        field_filters: t.Optional[t.List[dict]] = None,
        excluded_adapters: t.Optional[t.List[dict]] = None,
        asset_excluded_adapters: t.Optional[t.List[dict]] = None,
        asset_filters: t.Optional[t.List[dict]] = None,
        expressions: t.Optional[t.List[dict]] = None,
        fields_parsed: t.Optional[t.Union[dict, t.List[str]]] = None,
        include_details: bool = False,
        include_notes: bool = False,
        use_cursor: bool = True,
        cursor_id: t.Optional[str] = None,
        saved_query_id: t.Optional[str] = None,
        query_id: t.Optional[t.Union[str, uuid.UUID]] = None,
        is_refresh: bool = False,
        null_for_non_exist: bool = False,
        source_component: t.Optional[str] = None,
        frontend_sent_time: t.Optional[datetime.datetime] = None,
        filter_out_non_existing_fields: bool = True,
        complex_fields_preview_limit: t.Optional[int] = None,
        max_field_items: t.Optional[int] = None,
        initial_count: t.Optional[int] = None,
        request_obj: t.Optional[AssetRequest] = None,
        export_templates: t.Optional[dict] = None,
        http_args: t.Optional[dict] = None,
        **kwargs,
    ) -> t.Generator[dict, None, None]:
        """Get assets from a query.

        See Also:
            If ``export`` is not supplied, see
            :meth:`axonius_api_client.api.asset_callbacks.base.Base.args_map`.

            If ``export`` equals ``json``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_json.Json.args_map`.

            If ``export`` equals ``csv``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_csv.Csv.args_map`.

            If ``export`` equals ``json_to_csv``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_json_to_csv.JsonToCsv.args_map`.

            If ``export`` equals ``table``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_table.Table.args_map`.

            If ``export`` equals ``xlsx``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_xlsx.Xlsx.args_map`.

            :obj:`axonius_api_client.constants.asset_helpers.ASSET_HELPERS` for a list of
            helpers that translate between GUI titles, API request attributes, and saved query
            paths.

        Args:
            query: if supplied, only get the assets that match the query
            fields: fields to return for each asset (will be validated)
            fields_manual: fields to return for each asset (will NOT be validated)
            fields_regex: regex of fields to return for each asset
            fields_regex_root_only: only match fields_regex values against root fields
            fields_fuzzy: string to fuzzy match of fields to return for each asset
            fields_default: include the default fields in :attr:`fields_default`
            fields_root: include all fields of an adapter that are not complex sub-fields
            fields_error: throw validation errors on supplied fields
            fields_parsed: previously parsed fields
            max_rows: only return N rows
            max_pages: only return N pages
            row_start: start at row N
            page_size: fetch N rows per page
            page_start: start at page N
            page_sleep: sleep for N seconds between each page fetch
            export: export assets using a callback method
            include_notes: include any defined notes for each adapter
            include_details: include details fields showing the adapter source of agg values
            saved_query_id: ID of saved query this fetch is associated with
            expressions: expressions used by query wizard to create query
            sort_field: sort the returned assets on a given field
            sort_descending: reverse the sort of the returned assets
            history_date: return assets for a given historical date
            history_days_ago: return assets for a history date N days ago
            history_exact: Use the closest match for history_date and history_days_ago
            wiz_entries: wizard expressions to create query from
            file_date: string to use in filename templates for {DATE}
            wiz_parsed: parsed output from a query wizard
            sort_field_parsed: previously parsed sort field
            history_date_parsed: previously parsed history date
            initial_count: previously fetched initial count
            search: search string to use for this query
            use_heavy_fields_collection: unknown
            use_cursor: use cursor based pagination
            field_filters: field filters to apply to this query
            excluded_adapters: adapters to exclude from this query
            asset_excluded_adapters: adapters to exclude from this query
            asset_filters: asset filters to apply to this query
            cursor_id: cursor ID to use for this query
            query_id: query ID to use for this query
            is_refresh: is this a refresh query
            null_for_non_exist: return null for non existent fields
            source_component: source component to use for this query
            export_templates: filename template replacement mappings
            filter_out_non_existing_fields: filter out fields that do not exist
            complex_fields_preview_limit: limit the number of complex fields to preview
            max_field_items: max number of items to return for a field
            frontend_sent_time: frontend sent time to use for this query
            http_args: http args to pass to :meth:`axonius_api_client.http.Http.__call__` for each
                page fetched
            request_obj: request object to use for this query
            **kwargs: passed thru to the asset callback defined in ``export``
        """
        request_obj: AssetRequest = self.build_get_request(
            request_obj=request_obj,
            search=search,
            filter=query,
            history=history_date_parsed,
            sort=sort_field_parsed,
            field_filters=field_filters,
            excluded_adapters=excluded_adapters,
            asset_filters=asset_filters,
            expressions=expressions,
            include_details=include_details,
            include_notes=include_notes,
            use_cursor=use_cursor,
            cursor_id=cursor_id,
            saved_query_id=saved_query_id,
            query_id=query_id,
            source_component=source_component,
            frontend_sent_time=frontend_sent_time,
            filter_out_non_existing_fields=filter_out_non_existing_fields,
            is_refresh=is_refresh,
            null_for_non_exist=null_for_non_exist,
            max_field_items=max_field_items,
            complex_fields_preview_limit=complex_fields_preview_limit,
            use_heavy_fields_collection=use_heavy_fields_collection,
            asset_excluded_adapters=asset_excluded_adapters,
        )
        request_obj.get_metadata = True
        request_obj.use_cursor = use_cursor

        if not isinstance(http_args, dict):
            http_args: dict = {}

        if not isinstance(wiz_parsed, dict):
            wiz_parsed: dict = self.get_wiz_entries(wiz_entries=wiz_entries)

        if isinstance(wiz_parsed, dict):
            wiz_query: t.Optional[str] = wiz_parsed.get("query")
            wiz_expressions: t.Optional[t.List[dict]] = wiz_parsed.get("expressions")
            if isinstance(wiz_query, str) and wiz_query:
                query = wiz_query
            if isinstance(wiz_expressions, list) and wiz_expressions:
                request_obj.expressions = wiz_expressions

        if not isinstance(fields_parsed, (list, tuple)):
            fields_parsed = self.fields.validate(
                fields=fields,
                fields_manual=fields_manual,
                fields_regex=fields_regex,
                fields_regex_root_only=fields_regex_root_only,
                fields_default=fields_default,
                fields_root=fields_root,
                fields_fuzzy=fields_fuzzy,
                fields_error=fields_error,
            )

        if not isinstance(sort_field_parsed, str):
            request_obj.sort = sort_field_parsed = self.get_sort_field(
                field=sort_field, descending=sort_descending
            )

        if not isinstance(history_date_parsed, (str, datetime.datetime)):
            request_obj.history = history_date_parsed = self.get_history_date(
                date=history_date, days_ago=history_days_ago, exact=history_exact
            )

        if not isinstance(initial_count, int):
            initial_count: int = self.count(
                query=query,
                frontend_sent_time=request_obj.frontend_sent_time,
                history_date_parsed=history_date_parsed,
                query_id=request_obj.query_id,
                saved_query_id=request_obj.saved_query_id,
                use_heavy_fields_collection=request_obj.use_heavy_fields_collection,
            )

        if not isinstance(file_date, str):
            file_date: str = dt_now_file()

        if not isinstance(export_templates, dict):
            export_templates = {}

        export_templates.setdefault("{DATE}", file_date)
        export_templates.setdefault("{HISTORY_DATE}", history_date_parsed or file_date)

        store: dict = {
            "export": export,
            "query": query,
            "fields_parsed": fields_parsed,
            "fields": fields,
            "fields_regex": fields_regex,
            "fields_regex_root_only": fields_regex_root_only,
            "fields_fuzzy": fields_fuzzy,
            "fields_default": fields_default,
            "fields_root": fields_root,
            "fields_error": fields_error,
            "sort_field_parsed": sort_field_parsed,
            "sort_field": sort_field,
            "sort_descending": sort_descending,
            "history_date_parsed": history_date_parsed,
            "history_date": history_date,
            "history_days_ago": history_days_ago,
            "history_exact": history_exact,
            "include_details": include_details,
            "include_notes": include_notes,
            "max_rows": max_rows,
            "max_pages": max_pages,
            "page_size": page_size,
            "page_sleep": page_sleep,
            "page_start": page_start,
            "row_start": row_start,
            "initial_count": initial_count,
            "export_templates": export_templates,
            "request_obj": request_obj,
        }
        state: dict = AssetsPage.create_state(
            max_pages=max_pages,
            max_rows=max_rows,
            page_sleep=page_sleep,
            page_size=page_size,
            page_start=page_start,
            row_start=row_start,
            initial_count=initial_count,
        )
        callbacks_cls: t.Type[BaseCallbacks] = get_callbacks_cls(export=export)
        callbacks: BaseCallbacks = callbacks_cls(
            apiobj=self, getargs=kwargs, state=state, store=store
        )
        self.LAST_CALLBACKS: BaseCallbacks = callbacks
        callbacks.start()
        self.LOG.info(f"STARTING FETCH store={json_dump(store)}")
        self.LOG.debug(f"STARTING FETCH state={json_dump(state)}")

        while not state["stop_fetch"]:
            request_obj.filter = store["query"]
            request_obj.fields = {self.ASSET_TYPE: store["fields_parsed"]}
            request_obj.include_details = store["include_details"]
            request_obj.include_notes = store["include_notes"]
            request_obj.set_offset(state["rows_offset"])
            request_obj.set_limit(state["page_size"])

            try:
                start_dt: datetime.datetime = dt_now()
                page: AssetsPage = self._get(request_obj=request_obj, http_args=http_args)

                if request_obj.use_cursor:
                    request_obj.cursor_id = page.cursor
                state: dict = page.process_page(state=state, start_dt=start_dt, apiobj=self)
                for row in page.assets:
                    state: dict = page.start_row(state=state, apiobj=self, row=row)
                    yield from listify(obj=callbacks.process_row(row=row))
                    state: dict = page.process_row(state=state, apiobj=self, row=row)
                state: dict = page.process_loop(state=state, apiobj=self)
                time.sleep(state["page_sleep"])
            except StopFetch as exc:
                self.LOG.debug(f"Received {type(exc)}: {exc.reason}")
                break
        self.LOG.info(f"FINISHED FETCH store={json_dump(store)}")
        self.LOG.debug(f"FINISHED FETCH state={json_dump(state)}")
        callbacks.stop()

    def get_by_saved_query(
        self,
        name: str,
        include_fields: bool = True,
        include_excluded_adapters: bool = True,
        include_asset_excluded_adapters: bool = True,
        include_field_filters: bool = True,
        include_asset_filters: bool = True,
        **kwargs,
    ) -> GEN_TYPE:
        """Get assets that would be returned by a saved query.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
            ``apiobj`` is ``client.devices`` or ``client.users``
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities

            Get assets from a saved query with complex fields flattened
            >>> assets: t.List[dict] = apiobj.get_by_saved_query(name="test", field_flatten=True)

        See Also:
            :obj:`axonius_api_client.constants.asset_helpers.ASSET_HELPERS` for a list of
            helpers that translate between GUI titles, API request attributes, and saved query
            paths.

        Args:
            name: name of saved query to get assets from
            include_fields: include fields from saved query
            include_excluded_adapters: include column filters for excluded adapters from saved query
            include_asset_excluded_adapters: include column filters for asset excluded adapters
                from saved query
            include_field_filters: include column filters for field filters from saved query
            include_asset_filters: include column filters for asset filters from saved query
            **kwargs: passed to :meth:`get`
        """
        sq = self.saved_query.get_by_multi(sq=name)
        _view: dict = sq.get("view", {})
        _query: dict = _view.get("query", {})

        kwargs["saved_query_id"] = sq["id"]
        kwargs["query"] = _query.get("filter")
        kwargs["expressions"] = _query.get("expressions")

        if include_fields:
            kwargs["fields_manual"] = _view.get("fields")

        if include_excluded_adapters:
            kwargs["excluded_adapters"] = _view.get("colExcludedAdapters")

        if include_asset_excluded_adapters:
            kwargs["asset_excluded_adapters"] = _view.get("assetExcludeAdapters")

        if include_field_filters:
            kwargs["field_filters"] = _view.get("fieldFilters")

        if include_asset_filters:
            kwargs["asset_filters"] = _view.get("assetFilters")

        if kwargs.get("fields_manual"):
            kwargs.setdefault("fields_default", False)

        return self.get(**kwargs)

    def get_wiz_entries(
        self, wiz_entries: t.Optional[t.Union[t.List[dict], t.List[str], dict, str]] = None
    ) -> t.Optional[dict]:
        """Build a query and expressions.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities

            None is returned if no wiz_entries are passed
            >>> items = None
            >>> parsed = apiobj.get_wiz_entries(wiz_entries=items)
            >>> print(parsed)
            None

            A string or list of strings will be parsed into a query and expressions:
            >>> items = "simple hostname contains test"
            >>> parsed = apiobj.get_wiz_entries(wiz_entries=items)
            >>> client.jdump(parsed)
           {
              "expressions": [
                {
                  "bracketWeight": 0,
                  "children": [
                    {
                      "condition": "",
                      "expression": {
                        "compOp": "",
                        "field": "",
                        "filteredAdapters": null,
                        "value": null
                      },
                      "i": 0
                    }
                  ],
                  "compOp": "contains",
                  "field": "specific_data.data.hostname",
                  "fieldType": "axonius",
                  "filter": "(\"specific_data.data.hostname\" == regex(\"test\", \"i\"))",
                  "filteredAdapters": null,
                  "leftBracket": false,
                  "logicOp": "",
                  "not": false,
                  "rightBracket": false,
                  "value": "test"
                }
              ],
              "query": "(\"specific_data.data.hostname\" == regex(\"test\", \"i\"))"
            }

            A dict or list of dicts will be parsed into a query and expressions
            >>> items = {"type": "simple", "value": "hostname contains test"}
            >>> parsed = client.devices.get_wiz_entries(items)
            >>> # same output as above

        Args:
            wiz_entries: list of dicts or list of strings or single dict or single string
        """
        wiz_entries = listify(wiz_entries) if wiz_entries else []
        if not wiz_entries:
            return None

        if all([isinstance(x, dict) for x in wiz_entries]):
            return self.wizard.parse(entries=wiz_entries)

        if all([isinstance(x, str) for x in wiz_entries]):
            return self.wizard_text.parse(content=wiz_entries)

        raise ApiError("wiz_entries must be a single or list of dict or str")

    def get_sort_field(
        self, field: t.Optional[str] = None, descending: bool = False, validate: bool = True
    ) -> t.Optional[str]:
        """Build the parsed sort field based off of field and descending.

        Args:
            field: field to sort by
            descending: if True, sort descending
            validate: if True, validate field name

        Returns:
            field (prefixed with - if descending), None if field is None
        """
        if isinstance(field, str) and field:
            if validate:
                field = self.fields.get_field_name(value=field)
            field = f"-{field}" if descending else field
        else:
            field = None
        return field

    def get_history_date(
        self,
        date: t.Optional[t.Union[str, datetime.timedelta, datetime.datetime]] = None,
        days_ago: t.Optional[int] = None,
        exact: bool = False,
    ) -> t.Optional[str]:
        """Get a history date.

        Args:
            date: date to get
            days_ago: days ago to get
            exact: if True, do not round to the nearest day

        Returns:
            date in YYYY-MM-DD format or None
        """
        if date is not None or days_ago is not None:
            return self.history_dates_obj().get_date(date=date, days_ago=days_ago, exact=exact)
        return None

    def get_by_id(self, id: str) -> dict:
        """Get the full data set of all adapters for a single asset.

        Examples:
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> assets: list[dict] = apiobj.get(max_rows=1)
            >>> asset_id: str = assets[0]["internal_axon_id"]
            >>> asset: dict = apiobj.get_by_id(id=as)

        Args:
            id: internal_axon_id of asset to get all data set for

        Raises:
            :exc:`NotFoundError`: if id is not found

        """
        try:
            return self._get_by_id(id=id).to_dict()
        except ResponseNotOk as exc:
            if exc.response.status_code == 404:
                asset_type = self.ASSET_TYPE
                msg = f"Failed to find {asset_type} asset with internal_axon_id of {id!r}"
                raise NotFoundError(msg)
            raise  # pragma: no cover

    @property
    def fields_default(self) -> t.List[dict]:
        """Fields to use by default for getting assets."""
        raise NotImplementedError  # pragma: no cover

    def destroy(self, destroy: bool, history: bool) -> dict:  # pragma: no cover
        """Delete ALL assets.

        Notes:
            Enable the ``Enable API destroy endpoints`` setting under
            ``Settings > Global Settings > API Settings > Enable advanced API settings``
            for this method to function.

        Args:
            destroy: Must be true in order to actually perform the delete
            history: Also delete all historical information
        """
        return self._destroy(destroy=destroy, history=history)

    def get_by_values(
        self,
        values: t.List[str],
        field: str,
        not_flag: bool = False,
        pre: str = "",
        post: str = "",
        field_manual: bool = False,
        **kwargs,
    ) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where field in values.

        Notes:
            It is better to use :attr:`wizard`, :attr:`wizard_text`, or :attr:`wizard_csv`
            to build queries!

        Args:
            values: list of values that must match `field`
            field: name of field to query against
            not_flag: prefix query with 'not'
            pre: query to add to the beginning of the query
            post: query to add to the end of the query
            field_manual: consider supplied field as a fully qualified field name
            **kwargs: passed to :meth:`get`
        """
        field = self.fields.get_field_name(value=field, field_manual=field_manual)

        match = listify(values)
        match = [f"'{x.strip()}'" for x in match]
        match = ", ".join(match)

        inner = f"{field} in [{match}]"

        kwargs["query"] = self._build_query(
            inner=inner,
            pre=pre,
            post=post,
            not_flag=not_flag,
        )

        return self.get(**kwargs)

    def get_by_value_regex(
        self,
        value: str,
        field: str,
        cast_insensitive: bool = True,
        not_flag: bool = False,
        pre: str = "",
        post: str = "",
        field_manual: bool = False,
        **kwargs,
    ) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where field regex matches a value.

        Notes:
            It is better to use :attr:`wizard`, :attr:`wizard_text`, or :attr:`wizard_csv`
            to build queries!

        Args:
            value: regex that must match `field`
            field: name of field to query against
            cast_insensitive: ignore case when performing the regex match
            not_flag: prefix query with 'not'
            pre: query to add to the beginning of the query
            post: query to add to the end of the query
            field_manual: consider supplied field as a fully qualified field name
            **kwargs: passed to :meth:`get`
        """
        field = self.fields.get_field_name(value=field, field_manual=field_manual)
        flags = ', "i"' if cast_insensitive else ""
        inner = f'{field} == regex("{value}"{flags})'
        kwargs["query"] = self._build_query(
            inner=inner,
            pre=pre,
            post=post,
            not_flag=not_flag,
        )
        return self.get(**kwargs)

    def get_by_value(
        self,
        value: str,
        field: str,
        not_flag: bool = False,
        pre: str = "",
        post: str = "",
        field_manual: bool = False,
        **kwargs,
    ) -> GEN_TYPE:  # pragma: no cover
        """Build a query to get assets where field equals a value.

        Notes:
            It is better to use :attr:`wizard`, :attr:`wizard_text`, or :attr:`wizard_csv`
            to build queries!

        Args:
            value: value that must equal `field`
            field: name of field to query against
            not_flag: prefix query with 'not'
            pre: query to add to the beginning of the query
            post: query to add to the end of the query
            field_manual: consider supplied field as a fully qualified field name
            **kwargs: passed to :meth:`get`
        """
        field = self.fields.get_field_name(value=field, field_manual=field_manual)

        inner = f'{field} == "{value}"'

        kwargs["query"] = self._build_query(
            inner=inner,
            pre=pre,
            post=post,
            not_flag=not_flag,
        )

        return self.get(**kwargs)

    @cachetools.cached(cache=HISTORY_DATES_OBJ_CACHE)
    def history_dates_obj(self) -> AssetTypeHistoryDates:
        """Pass."""
        return self._history_dates().parsed[self.ASSET_TYPE]

    @cachetools.cached(cache=HISTORY_DATES_CACHE)
    def history_dates(self) -> dict:
        """Get all known historical dates."""
        return self._history_dates().value[self.ASSET_TYPE]

    def _build_query(
        self, inner: str, not_flag: bool = False, pre: str = "", post: str = ""
    ) -> str:  # pragma: no cover
        """Query builder with basic functionality.

        Notes:
            It is better to use :attr:`wizard`, :attr:`wizard_text`, or :attr:`wizard_csv`
            to build queries!

        Args:
            inner: inner query portion to wrap in parens and prefix with not
            not_flag: prefix query with 'not'
            pre: query to add to the beginning of the query
            post: query to add to the end of the query
        """
        if not_flag:
            inner = f"(not ({inner}))"
        else:
            inner = f"({inner})"

        lines = [pre, inner, post]
        query = " ".join([x.strip() for x in lines if x.strip()]).strip()

        self.LOG.debug(f"Built query: {query!r}")
        return query

    @staticmethod
    def build_get_request(
        request_obj: t.Optional[AssetRequest] = None,
        offset: t.Optional[int] = 0,
        limit: t.Optional[int] = PAGE_SIZE,
        remove_unknown_arguments: bool = True,
        warn_unknown_arguments: bool = True,
        **kwargs,
    ) -> AssetRequest:
        """Build a request object for a get assets request.

        Args:
            request_obj: request object to use
            offset: offset to start at
            limit: number of assets to return
            remove_unknown_arguments: remove unknown arguments from kwargs
            warn_unknown_arguments: warn about unknown arguments
            **kwargs: passed to :meth:`load_request`
        """
        if not isinstance(request_obj, AssetRequest):
            api_endpoint: ApiEndpoint = ApiEndpoints.assets.get
            request_obj: AssetRequest = api_endpoint.load_request(
                remove_unknown_arguments=remove_unknown_arguments,
                warn_unknown_arguments=warn_unknown_arguments,
                **kwargs,
            )
            request_obj.set_limit(limit)
            request_obj.set_offset(offset)
        return request_obj

    @staticmethod
    def build_count_request(
        request_obj: t.Optional[CountRequest] = None,
        remove_unknown_arguments: bool = True,
        warn_unknown_arguments: bool = True,
        **kwargs,
    ) -> CountRequest:
        """Build a request object for a get asset count request.

        Args:
            request_obj: request object to use
            remove_unknown_arguments: remove unknown arguments from kwargs
            warn_unknown_arguments: warn about unknown arguments
            **kwargs: passed to :meth:`load_request`
        """
        if not isinstance(request_obj, CountRequest):
            api_endpoint: ApiEndpoint = ApiEndpoints.assets.count
            kwargs, _ = CountRequest.remove_unknown_arguments(
                kwargs=kwargs,
                remove_unknown_arguments=remove_unknown_arguments,
                warn_unknown_arguments=warn_unknown_arguments,
            )
            request_obj: CountRequest = api_endpoint.load_request(**kwargs)
        return request_obj

    @property
    def data_scopes(self):
        """Work with data scopes."""
        if not hasattr(self, "_data_scopes"):
            from ..system import DataScopes

            self._data_scopes: DataScopes = DataScopes(auth=self.auth)
        return self._data_scopes

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        from ..adapters import Adapters
        from ..asset_callbacks import Base
        from ..system import Instances
        from .fields import Fields
        from .labels import Labels
        from .saved_query import SavedQuery

        self.adapters: Adapters = Adapters(auth=self.auth, **kwargs)
        """Adapters API model for cross reference."""

        self.instances: Instances = Instances(auth=self.auth, **kwargs)
        """Adapters API model for cross reference."""

        self.labels: Labels = Labels(parent=self)
        """Work with labels (tags)."""

        self.tags = self.labels
        """Alias for :attr:`labels`."""

        self.saved_query: SavedQuery = SavedQuery(parent=self)
        """Work with saved queries."""

        self.fields: Fields = Fields(parent=self)
        """Work with fields."""

        self.wizard: Wizard = Wizard(apiobj=self)
        """Query wizard builder."""

        self.wizard_text: WizardText = WizardText(apiobj=self)
        """Query wizard builder from text."""

        self.wizard_csv: WizardCsv = WizardCsv(apiobj=self)
        """Query wizard builder from CSV."""

        self.LAST_GET: t.Optional[dict] = None
        """Request object sent for last :meth:`_get` request"""

        self.LAST_COUNT: t.Optional[dict] = None
        """Request object sent for last :meth:`_count` request"""

        self.LAST_GET_REQUEST_OBJ: t.Optional[AssetRequest] = None
        """Request data model sent for last :meth:`_get` request"""

        self.LAST_COUNT_REQUEST_OBJ: t.Optional[CountRequest] = None
        """Request data model sent for last :meth:`_count` request"""

        self.LAST_CALLBACKS: t.Optional[Base] = None
        """Callbacks object used for last :meth:`get` request."""

        super(AssetMixin, self)._init(**kwargs)

    def _get(
        self,
        request_obj: t.Optional[AssetRequest] = None,
        offset: t.Optional[int] = 0,
        limit: t.Optional[int] = PAGE_SIZE,
        http_args: t.Optional[dict] = None,
        **kwargs,
    ) -> AssetsPage:
        """Private API method to get a page of assets using a request object.

        Args:
            request_obj: request object to use
            offset: offset to start at
            limit: number of assets to return
            http_args: arguments to pass to :meth:`requests.Session.request`
            **kwargs: passed to :meth:`build_get_request`
        """
        request_obj: AssetRequest = self.build_get_request(
            request_obj=request_obj, offset=offset, limit=limit, **kwargs
        )
        self.LOG.debug(f"Getting {self.ASSET_TYPE} assets with request {json_dump(request_obj)}")
        self.LAST_GET_REQUEST_OBJ: AssetRequest = request_obj
        self.LAST_GET: dict = request_obj.to_dict()
        api_endpoint: ApiEndpoint = ApiEndpoints.assets.get
        response: AssetsPage = api_endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            asset_type=self.ASSET_TYPE,
            http_args=http_args,
        )
        return response

    def _count(
        self,
        request_obj: t.Optional[CountRequest] = None,
        http_args: t.Optional[dict] = None,
        **kwargs,
    ) -> Count:
        """Direct API method to get the count of assets using a request object.

        Args:
            request_obj: request object to use
            http_args: Arguments to pass to the HTTP request
            kwargs: Arguments to pass to :meth:`build_count_request`
        """
        request_obj = self.build_count_request(request_obj=request_obj, **kwargs)
        self.LOG.debug(
            f"Getting count of {self.ASSET_TYPE} assets with request {json_dump(request_obj)}"
        )
        self.LAST_COUNT_REQUEST_OBJ: CountRequest = request_obj
        self.LAST_COUNT: dict = request_obj.to_dict()
        api_endpoint: ApiEndpoint = ApiEndpoints.assets.count
        response: Count = api_endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            asset_type=self.ASSET_TYPE,
            http_args=http_args,
        )
        return response

    def _get_by_id(self, id: str) -> AssetById:
        """Private API method to get the full metadata of all adapters for a single asset.

        Args:
            id: asset to get all metadata for
        """
        asset_type = self.ASSET_TYPE
        api_endpoint = ApiEndpoints.assets.get_by_id
        return api_endpoint.perform_request(
            http=self.auth.http, asset_type=asset_type, internal_axon_id=id
        )

    def _destroy(self, destroy: bool, history: bool) -> dict:  # pragma: no cover
        """Private API method to destroy ALL assets.

        Args:
            destroy: Must be true in order to actually perform the delete
            history: Also delete all historical information
        """
        asset_type = self.ASSET_TYPE
        api_endpoint = ApiEndpoints.assets.destroy
        request_obj = api_endpoint.load_request(
            destroy=destroy,
            history=history,
        )

        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=asset_type
        )

    def _history_dates(self) -> HistoryDates:
        """Private API method to get all known historical dates."""
        api_endpoint = ApiEndpoints.assets.history_dates
        return api_endpoint.perform_request(http=self.auth.http)

    def _run_enforcement(
        self,
        name: str,
        ids: t.List[str],
        include: bool = True,
        fields: t.Optional[t.List[str]] = None,
        query: t.Optional[str] = "",
    ) -> None:
        """Run an enforcement set manually against a list of assets internal_axon_ids.

        Args:
            name (str): Name of enforcement set to execute
            ids (t.List[str]): internal_axon_id's of assets to run enforcement set against
            include (bool, optional): select IDs in DB or IDs NOT in DB
            fields (t.Optional[t.List[str]], optional): list of fields used to select assets
            query (str, optional): filter used to select assets

        Returns:
            TYPE: Empty response
        """
        fields = listify(fields)
        ids = listify(ids)
        query = query if isinstance(query, str) and query.strip() else ""

        asset_type = self.ASSET_TYPE
        selection = {"ids": ids, "include": include}

        view_sort = {"field": "", "desc": True}
        view_colfilters = []
        view = {"fields": fields, "sort": view_sort, "colFilters": view_colfilters}
        # view does not seem to be really used in back end, but front end sends it
        # duplicating the front end concept for now

        api_endpoint = ApiEndpoints.assets.run_enforcement
        request_obj = api_endpoint.load_request(
            name=name, selection=selection, view=view, filter=query
        )

        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=asset_type
        )

    FIELD_TAGS: str = "labels"
    """Field name for getting tabs (labels)."""

    FIELD_AXON_ID: str = AXID.name
    """Field name for asset unique ID."""

    FIELD_ADAPTERS: str = "adapters"
    """Field name for list of adapters on an asset."""

    FIELD_ADAPTER_LEN: str = "adapter_list_length"
    """Field name for count of adapters on an asset."""

    FIELD_LAST_SEEN: str = "specific_data.data.last_seen"
    """Field name for last time an adapter saw the asset."""

    FIELD_MAIN: str = FIELD_AXON_ID
    """Field name of the main identifier."""

    FIELD_SIMPLE: str = FIELD_AXON_ID
    """Field name of a simple field."""

    FIELD_COMPLEX: str = None
    """Field name of a complex field."""

    FIELD_COMPLEX_SUB: str = None
    """Field name of a complex sub field."""

    FIELDS_API: t.List[str] = [
        FIELD_AXON_ID,
        FIELD_ADAPTERS,
        FIELD_TAGS,
        FIELD_ADAPTER_LEN,
    ]
    """Field names that are always returned by the REST API no matter what fields are selected"""

    wizard: str = None
    """:obj:`axonius_api_client.api.wizards.wizard.Wizard`: Query wizard for python objects."""

    wizard_text: str = None
    """:obj:`axonius_api_client.api.wizards.wizard_text.WizardText`: Query wizard for text files."""

    wizard_csv = None
    """:obj:`axonius_api_client.api.wizards.wizard_csv.WizardCsv`: Query wizard for CSV files."""
