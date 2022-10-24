# -*- coding: utf-8 -*-
"""API model mixin for device and user assets."""
import datetime
import pathlib
import time
import types
import typing as t

import cachetools

from ...constants.api import DEFAULT_CALLBACKS_CLS, MAX_PAGE_SIZE, PAGE_SIZE
from ...constants.fields import AXID
from ...exceptions import ApiError, NotFoundError, ResponseNotOk, StopFetch
from ...parsers.grabber import Grabber
from ...tools import PathLike, dt_now, dt_now_file, get_subcls, json_dump, listify
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..asset_callbacks.tools import get_callbacks_cls
from ..mixins import ModelMixins
from ..wizards import Wizard, WizardCsv, WizardText
from .runner import ENFORCEMENT, Runner

GEN_TYPE = t.Union[t.Generator[dict, None, None], t.List[dict]]
HISTORY_DATES_OBJ_CACHE = cachetools.TTLCache(maxsize=1, ttl=300)
HISTORY_DATES_CACHE = cachetools.TTLCache(maxsize=1, ttl=300)


class AssetMixin(ModelMixins):
    """API model mixin for device and user assets.

    Examples:
        Create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
        ``apiobj`` is either ``client.devices`` or ``client.users``

        >>> apiobj = client.devices  # or client.users

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
    def asset_modules(cls) -> t.List["AssetMixin"]:
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
            '''Get a list of assets from a query and manually extract the IDs.
            We know assets are valid because we just got them, so we pass verified=True.
            '''
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            WIZ = "simple os.type equals Windows"  # "query of assets to target"
            ESET = "test"  # "name or uuid of enforcement set"
            ITEMS = apiobj.get(wiz_entries=WIZ)
            IDS = [x['internal_axon_id'] for x in ITEMS]
            runner = apiobj.run_enforcement(eset=ESET, ids=IDS, verified=True)
            print(runner)
            '''
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
            '''

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
            refetch (bool): refetch $eset even if it is a :obj:`json_api.enforcements.SetFull`
            check_stdin (bool): check if stdin is a TTY when prompting
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
            '''Get a list of assets from a query and use the grabber get the IDs.
            We know assets are valid because we just got them, so we pass verified=True.
            '''
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            WIZ = "simple os.type equals Windows"  # "query of assets to target"
            ESET = "test"  # "name or uuid of enforcement set"
            ITEMS = apiobj.get(wiz_entries=WIZ)
            runner = apiobj.run_enforcement_from_items(eset=ESET, items=ITEMS, verified=True)
            print(runner)
            '''
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
            ),
            )
            '''

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
            '''Get a list of assets from a query and export the assets to a JSON str
            then run an enforcement against all asset IDs from the JSON str.
            We know assets are valid because we just got them, so we pass verified=True.
            '''
            import io
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            WIZ = "simple os.type equals Windows"  # "query of assets to target"
            ESET = "test"  # "name or uuid of enforcement set"
            FH = io.StringIO()
            z = apiobj.get(wiz_entries=WIZ, export="json", export_fd=FH, export_fd_close=False)
            FH.seek(0)
            ITEMS = FH.getvalue()
            runner = apiobj.run_enforcement_from_json(eset=ESET, items=ITEMS, verified=True)
            print(runner)
            '''
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
            '''

            '''Get a list of assets from a query and export the assets to a JSON file
            then run an enforcement against all asset IDs from the JSON file.
            We know assets are valid because we just got them, so we pass verified=True.
            '''
            import pathlib
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            WIZ = "simple os.type equals Windows"  # "query of assets to target"
            ESET = "test"  # "name or uuid of enforcement set"
            PATH = pathlib.Path("data.json")
            z = apiobj.get(wiz_entries=WIZ, export="json", export_file=PATH, export_overwrite=True)
            runner = apiobj.run_enforcement_from_json(eset=ESET, items=PATH, verified=True)
            print(runner)
            '''
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
            '''

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
            '''Get a list of assets from a query and export the assets to a JSONL str
            then run an enforcement against all asset IDs from the JSONL str.
            We know assets are valid because we just got them, so we pass verified=True.
            '''
            import io
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            WIZ = "simple os.type equals Windows"  # "query of assets to target"
            ESET = "test"  # "name or uuid of enforcement set"
            FH = io.StringIO()
            z = apiobj.get(
              wiz_entries=WIZ, export="json", json_flat=True, export_fd=FH, export_fd_close=False)
            FH.seek(0)
            runner = apiobj.run_enforcement_from_jsonl(eset=ESET, items=FH, verified=True)
            print(runner)
            '''
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
            '''

            '''Get a list of assets from a query and export the assets to a JSONL file
            then run an enforcement against all asset IDs from the JSONL file.
            We know assets are valid because we just got them, so we pass verified=True.
            '''
            import pathlib
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            WIZ = "simple os.type equals Windows"  # "query of assets to target"
            ESET = "test"  # "name or uuid of enforcement set"
            PATH = pathlib.Path("data.jsonl")
            z = apiobj.get(
              wiz_entries=WIZ, export="json", json_flat=True, export_file=PATH,
              export_overwrite=True)
            runner = apiobj.run_enforcement_from_jsonl(eset=ESET, items=PATH, verified=True)
            print(runner)
            '''
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
            '''

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
            '''Get a list of assets from a query and export the assets to a JSONL str
            then run an enforcement against all asset IDs from the JSONL str.
            We can also use a CSV file exported from the GUI.
            We know assets are valid because we just got them, so we pass verified=True.
            '''
            from axonius_api_client.tools import bom_strip
            import io
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            WIZ = "simple os.type equals Windows"  # "query of assets to target"
            ESET = "test"  # "name or uuid of enforcement set"
            FH = io.StringIO()
            z = apiobj.get(wiz_entries=WIZ, export="csv", export_fd=FH, export_fd_close=False)
            FH.seek(0)
            ITEMS = bom_strip(FH.getvalue())
            runner = apiobj.run_enforcement_from_csv(eset=ESET, items=ITEMS, verified=True)
            print(runner)
            '''
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
            '''

            '''Get a list of assets from a query and export the assets to a CSV file
            then run an enforcement against all asset IDs from the CSV file.
            We can also use a CSV file exported from the GUI.
            We know assets are valid because we just got them, so we pass verified=True.
            '''
            import pathlib
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            WIZ = "simple os.type equals Windows"  # "query of assets to target"
            ESET = "test"  # "name or uuid of enforcement set"
            PATH = pathlib.Path("data.csv")
            z = apiobj.get(wiz_entries=WIZ, export="csv", export_file=PATH, export_overwrite=True)
            runner = apiobj.run_enforcement_from_csv(eset=ESET, items=PATH, verified=True)
            print(runner)
            '''
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
            '''

        Args:
            eset (ENFORCEMENT): name, uuid, or Enforcement Set object to run
            items (t.Union[str, bytes, t.IO, pathlib.Path]): csv str, handle for file containing
                csv str, or pathlib.Path of path containing csv str
            keys (t.Union[str, t.List[str]]): additional keys for grabber to look for Asset IDs in
            do_echo_grab (bool, optional): Echo output of Asset ID grabber to console as well as log
            do_raise_grab (bool, optional): Throw an error if grabber fails to find an Asset ID
                in any items
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
            '''Get a list of assets from a query and export the assets to a text file
            then run an enforcement against all asset IDs from the text file.
            All lines will have any non alpha-numeric characters removed from them and if a
            32 character alpha numeric string is found it is considered an Asset ID.
            We know assets are valid because we just got them, so we pass verified=True.
            '''
            import pathlib
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            WIZ = "simple os.type equals Windows"  # "query of assets to target"
            ESET = "test"  # "name or uuid of enforcement set"
            PATH = pathlib.Path("data.txt")
            ASSETS = apiobj.get(wiz_entries=WIZ)
            IDS = [x['internal_axon_id'] for x in ASSETS]
            PATH.write_text('\n'.join(IDS))
            runner = apiobj.run_enforcement_from_text(eset=ESET, items=PATH, verified=True)
            print(runner)
            '''
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
            '''

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
            '''Run an enforcement against all asset IDs from a JSON file.
            We are unsure if Asset IDs are still valid for this instance so
            we do not pass verified=True.
            '''
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            PATH = "data.json"
            ESET = "test"  # "name or uuid of enforcement set"
            runner = apiobj.run_enforcement_from_json_path(eset=ESET, path=PATH)
            print(runner)
            '''
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
            '''

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
            '''Run an enforcement against all asset IDs from a JSONL file.
            We are unsure if Asset IDs are still valid for this instance so
            we do not pass verified=True.
            '''
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            PATH = "data.jsonl"
            ESET = "test"  # "name or uuid of enforcement set"
            runner = apiobj.run_enforcement_from_jsonl_path(eset=ESET, path=PATH)
            print(runner)
            '''
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
            '''

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
            '''Run an enforcement against all asset IDs from a JSONL file.
            We are unsure if Asset IDs are still valid for this instance so
            we do not pass verified=True.
            '''
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            PATH = "data.csv"
            ESET = "test"  # "name or uuid of enforcement set"
            runner = apiobj.run_enforcement_from_csv_path(eset=ESET, path=PATH)
            print(runner)
            '''
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
            '''

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
            '''Run an enforcement against all asset IDs from a text file.
            All lines will have any non alpha-numeric characters removed from them and if a
            32 character alpha numeric string is found it is considered an Asset ID.
            We are unsure if Asset IDs are still valid for this instance so
            we do not pass verified=True.
            '''
            client = globals()['client']  # instance of axonius_api_client.Connect
            apiobj = client.devices  # client.devices, client.users, or client.vulnerabilities
            PATH = "data.txt"
            ESET = "test"  # "name or uuid of enforcement set"
            runner = apiobj.run_enforcement_from_text_path(eset=ESET, path=PATH)
            print(runner)
            '''
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
            '''

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
        """Work with data scopes."""
        if not hasattr(self, "_enforcements"):
            from ..enforcements import Enforcements

            self._enforcements: Enforcements = Enforcements(auth=self.auth)
        return self._enforcements

    def count(
        self,
        query: t.Optional[str] = None,
        history_date: t.Optional[t.Union[str, datetime.timedelta, datetime.datetime]] = None,
        history_days_ago: t.Optional[int] = None,
        history_exact: bool = False,
        wiz_entries: t.Optional[t.Union[t.List[dict], t.List[str], dict, str]] = None,
        use_cache_entry: bool = False,
        saved_query_id: t.Optional[str] = None,
        **kwargs,
    ) -> int:
        """Get the count of assets from a query.

        Examples:
            Get count of all assets

            >>> count = apiobj.count()

            Get count of all assets for a given date

            >>> count = apiobj.count(history_date="2020-09-29")

            Get count of assets matching a query built by the GUI query wizard

            >>> query='(specific_data.data.name == "test")'
            >>> count = apiobj.count(query=query)

            Get count of assets matching a query built by the API client query wizard

            >>> entries = [{'type': 'simple', 'value': 'name equals test'}]
            >>> count = apiobj.count(wiz_entries=entries)

        Args:
            query: if supplied, only return the count of assets that match the query
                if not supplied, the count of all assets will be returned
            history_date: return asset count for a given historical date
            wiz_entries: wizard expressions to create query from

        """
        wiz_parsed = self.get_wiz_entries(wiz_entries=wiz_entries)

        if isinstance(wiz_parsed, dict):
            if wiz_parsed.get("query"):
                query = wiz_parsed["query"]

        history_date = self.get_history_date(
            date=history_date, days_ago=history_days_ago, exact=history_exact
        )

        value = None

        while value is None:
            value = self._count(
                filter=query,
                history_date=history_date,
                use_cache_entry=use_cache_entry,
            ).value
            use_cache_entry = True

        return value

    def count_by_saved_query(self, name: str, **kwargs) -> int:
        """Get the count of assets for a query defined in a saved query.

        Examples:
            Get count of assets returned from a saved query

            >>> count = apiobj.count_by_saved_query(name="test")

            Get count of assets returned from a saved query for a given date

            >>> count = apiobj.count_by_saved_query(name="test", history_date="2020-09-29")

        Args:
            name: saved query to get count of assets from
            kwargs: supplied to :meth:`count`
        """
        sq = self.saved_query.get_by_name(value=name)
        kwargs["query"] = sq["view"]["query"]["filter"]
        kwargs["saved_query_id"] = sq["id"]
        return self.count(**kwargs)

    def get(self, generator: bool = False, **kwargs) -> GEN_TYPE:
        r"""Get assets from a query.

        Examples:
            Get all assets with the default fields defined in the API client

            >>> assets = apiobj.get()

            Get all assets using an iterator

            >>> assets = [x for x in apiobj.get(generator=True)]

            Get all assets with fields that equal names

            >>> assets = apiobj.get(fields=["os.type", "aws:aws_device_type"])

            Get all assets with fields that fuzzy match names and no default fields

            >>> assets = apiobj.get(fields_fuzzy=["last", "os"], fields_default=False)

            Get all assets with fields that regex match names a

            >>> assets = apiobj.get(fields_regex=["^os\."])

            Get all assets with all root fields for an adapter

            >>> assets = apiobj.get(fields_root="aws")

            Get all assets for a given date in history and sort the rows on a field

            >>> assets = apiobj.get(history_date="2020-09-29", sort_field="name")

            Get all assets with details of which adapter connection provided the agg data

            >>> assets = apiobj.get(include_details=True)

            Get assets matching a query built by the GUI query wizard

            >>> query='(specific_data.data.name == "test")'
            >>> assets = apiobj.get(query=query)

            Get assets matching a query built by the API client query wizard

            >>> entries=[{'type': 'simple', 'value': 'name equals test'}]
            >>> assets = apiobj.get(wiz_entries=entries)

        See Also:
            This method is used by all other get* methods under the hood and their kwargs are
            passed thru to this method and passed to :meth:`get_generator` which are then passed
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

        Args:
            generator: return an iterator for assets that will yield rows as they are fetched
            **kwargs: passed to :meth:`get_generator`
        """
        gen = self.get_generator(**kwargs)
        return gen if generator else list(gen)

    def get_wiz_entries(
        self, wiz_entries: t.Optional[t.Union[t.List[dict], t.List[str], dict, str]] = None
    ) -> t.Optional[dict]:
        """Pass."""
        wiz_entries = listify(wiz_entries) if wiz_entries else []
        if not wiz_entries:
            return None

        if all([isinstance(x, dict) for x in wiz_entries]):
            return self.wizard.parse(entries=wiz_entries)

        if all([isinstance(x, str) for x in wiz_entries]):
            return self.wizard_text.parse(content=wiz_entries)

        raise ApiError("wiz_entries must be a single or list of dict or str")

    def get_sort_field(
        self, field: t.Optional[str] = None, descending: bool = False
    ) -> t.Optional[str]:
        """Pass."""
        if isinstance(field, str) and field:
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
        """Pass."""
        if date is not None or days_ago is not None:
            return self.history_dates_obj().get_date(date=date, days_ago=days_ago, exact=exact)
        return None

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
        include_notes: bool = False,
        include_details: bool = False,
        sort_field: t.Optional[str] = None,
        sort_descending: bool = False,
        history_date: t.Optional[t.Union[str, datetime.timedelta, datetime.datetime]] = None,
        history_days_ago: t.Optional[int] = None,
        history_exact: bool = False,
        wiz_entries: t.Optional[t.Union[t.List[dict], t.List[str], dict, str]] = None,
        saved_query_id: t.Optional[str] = None,
        expressions: t.Optional[t.List[dict]] = None,
        http_args: t.Optional[dict] = None,
        **kwargs,
    ) -> t.Generator[dict, None, None]:
        """Get assets from a query.

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
            max_rows: only return N rows
            max_pages: only return N pages
            row_start: start at row N
            page_size: fetch N rows per page
            page_start: start at page N
            page_sleep: sleep for N seconds between each page fetch
            export: export assets using a callback method
            include_notes: include any defined notes for each adapter
            include_details: include details fields showing the adapter source of agg values
            sort_field: sort the returned assets on a given field
            sort_descending: reverse the sort of the returned assets
            history_date: return assets for a given historical date
            history_days_ago: return assets for a history date N days ago
            history_exact: Use the closest match for history_date and history_days_ago
            wiz_entries: wizard expressions to create query from
            **kwargs: passed thru to the asset callback defined in ``export``
        """
        wiz_parsed: t.Optional[dict] = kwargs.get(
            "_wiz_parsed", self.get_wiz_entries(wiz_entries=wiz_entries)
        )

        if isinstance(wiz_parsed, dict):
            if wiz_parsed.get("query"):
                query = wiz_parsed["query"]
            if wiz_parsed.get("expressions"):
                expressions = wiz_parsed["expressions"]

        fields_parsed: t.List[str] = kwargs.get(
            "_fields_parsed",
            self.fields.validate(
                fields=fields,
                fields_manual=fields_manual,
                fields_regex=fields_regex,
                fields_regex_root_only=fields_regex_root_only,
                fields_default=fields_default,
                fields_root=fields_root,
                fields_fuzzy=fields_fuzzy,
                fields_error=fields_error,
            ),
        )

        sort_field_parsed: t.Optional[str] = kwargs.get(
            "_sort_field_parsed", self.get_sort_field(field=sort_field, descending=sort_descending)
        )

        history_date_parsed: t.Optional[str] = kwargs.get(
            "_history_date_parsed",
            self.get_history_date(
                date=history_date, days_ago=history_days_ago, exact=history_exact
            ),
        )

        initial_count: int = kwargs.get(
            "_initial_count", self.count(query=query, history_date=history_date)
        )

        file_date: str = kwargs.get("_file_date", dt_now_file())
        export_templates: dict = {
            "{DATE}": file_date,
            "{HISTORY_DATE}": history_date_parsed or file_date,
        }

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
        }

        state = json_api.assets.AssetsPage.create_state(
            max_pages=max_pages,
            max_rows=max_rows,
            page_sleep=page_sleep,
            page_size=page_size,
            page_start=page_start,
            row_start=row_start,
            initial_count=initial_count,
        )

        callbacks_cls = get_callbacks_cls(export=export)
        callbacks = callbacks_cls(apiobj=self, getargs=kwargs, state=state, store=store)

        self.LAST_CALLBACKS = callbacks
        callbacks.start()

        self.LOG.info(f"STARTING FETCH store={json_dump(store)}")
        self.LOG.debug(f"STARTING FETCH state={json_dump(state)}")

        while not state["stop_fetch"]:
            try:
                start_dt = dt_now()

                page = self._get(
                    include_details=store["include_details"],
                    include_notes=store["include_notes"],
                    sort=store["sort_field_parsed"],
                    history_date=store["history_date_parsed"],
                    filter=store["query"],
                    fields=store["fields_parsed"],
                    cursor_id=state["page_cursor"],
                    offset=state["rows_offset"],
                    limit=state["page_size"],
                    saved_query_id=saved_query_id,
                    expressions=expressions,
                    always_cached_query=False,
                    use_cache_entry=False,
                    get_metadata=True,
                    use_cursor=True,
                    http_args=http_args,
                )

                state = page.process_page(state=state, start_dt=start_dt, apiobj=self)

                for row in page.assets:
                    state = page.start_row(state=state, apiobj=self, row=row)
                    yield from listify(obj=callbacks.process_row(row=row))
                    state = page.process_row(state=state, apiobj=self, row=row)

                state = page.process_loop(state=state, apiobj=self)

                time.sleep(state["page_sleep"])
            except StopFetch as exc:
                self.LOG.debug(f"Received {type(exc)}: {exc.reason}")
                break

        self.LOG.info(f"FINISHED FETCH store={json_dump(store)}")
        self.LOG.debug(f"FINISHED FETCH state={json_dump(state)}")

        callbacks.stop()

    def get_by_saved_query(self, name: str, **kwargs) -> GEN_TYPE:
        """Get assets that would be returned by a saved query.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
            ``apiobj`` is ``client.devices`` or ``client.users``

            >>> apiobj = client.devices

            Get assets from a saved query with complex fields flattened

            >>> assets = apiobj.get_by_saved_query(name="test", field_flatten=True)

        Notes:
            The query and the fields defined in the saved query will be used to
            get the assets.

        Args:
            name: name of saved query to get assets from
            **kwargs: passed to :meth:`get`
        """
        sq = self.saved_query.get_by_name(value=name)
        kwargs["query"] = sq["view"]["query"]["filter"]
        kwargs["fields_manual"] = sq["view"]["fields"]
        kwargs["saved_query_id"] = sq["id"]
        kwargs["expressions"] = sq["view"]["query"]["expressions"]
        kwargs.setdefault("fields_default", False)
        return self.get(**kwargs)

    def get_by_id(self, id: str) -> dict:
        """Get the full data set of all adapters for a single asset.

        Examples:
            >>> asset = apiobj.get_by_id(id="3d69adf54879faade7a44068e4ecea6e")

        Args:
            id: internal_axon_id of asset to get all data set for

        Raises:
            :exc:`NotFoundError`: if id is not found

        """
        try:
            return self._get_by_id(id=id).asset
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
            values: list of values that must match field
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
            value: regex that must match field
            field: name of field to query against
            case_insensitive: ignore case when performing the regex match
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
            value: value that must equal field
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
    def history_dates_obj(self) -> json_api.assets.AssetTypeHistoryDates:
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

        self.LAST_GET: dict = {}
        """Request object sent for last :meth:`get` request"""

        self.LAST_GET_REQUEST_OBJ: json_api.assets.AssetRequest = None
        """Request data model sent for last :meth:`get` request"""

        self.LAST_CALLBACKS: Base = None
        """Callbacks object used for last :meth:`get` request."""

        super(AssetMixin, self)._init(**kwargs)

    def _get(
        self,
        always_cached_query: bool = False,
        use_cache_entry: bool = False,
        include_details: bool = False,
        include_notes: bool = False,
        get_metadata: bool = True,
        use_cursor: bool = True,
        sort_descending: bool = False,
        history_date: t.Optional[str] = None,
        filter: t.Optional[str] = None,
        cursor_id: t.Optional[str] = None,
        sort: t.Optional[str] = None,
        excluded_adapters: t.Optional[dict] = None,
        field_filters: t.Optional[dict] = None,
        fields: t.Optional[dict] = None,
        saved_query_id: t.Optional[str] = None,
        expressions: t.Optional[t.List[dict]] = None,
        offset: int = 0,
        limit: int = PAGE_SIZE,
        http_args: t.Optional[dict] = None,
    ) -> json_api.assets.AssetsPage:
        """Private API method to get a page of assets.

        Args:
            always_cached_query (bool, optional): UNK
            use_cache_entry (bool, optional): UNK
            include_details (bool, optional): include details fields showing the adapter source
                of agg values
            include_notes (bool, optional): Description
            get_metadata (bool, optional): Description
            use_cursor (bool, optional): Description
            sort_descending (bool, optional): reverse the sort of the returned assets
            history_date (t.Optional[str], optional): return assets for a given historical date
            filter (t.Optional[str], optional): Description
            cursor_id (t.Optional[str], optional): Description
            sort (t.Optional[str], optional): Description
            excluded_adapters (t.Optional[dict], optional): Description
            field_filters (t.Optional[dict], optional): Description
            fields (t.Optional[dict], optional): CSV or list of fields to include in return
            offset (int, optional): Description
            limit (int, optional): Description

        """
        asset_type = self.ASSET_TYPE
        api_endpoint = ApiEndpoints.assets.get
        request_obj = api_endpoint.load_request(
            always_cached_query=always_cached_query,
            use_cache_entry=use_cache_entry,
            include_details=include_details,
            include_notes=include_notes,
            get_metadata=get_metadata,
            use_cursor=use_cursor,
            filter=filter,
            cursor_id=cursor_id,
            history=history_date,
            fields={self.ASSET_TYPE: listify(fields)},
            sort=sort,
            excluded_adapters=excluded_adapters or {},
            field_filters=field_filters or {},
            saved_query_id=saved_query_id,
            expressions=expressions or [],
        )
        request_obj.set_page(limit=limit, offset=offset)
        self.LAST_GET_REQUEST_OBJ = request_obj
        self.LAST_GET = request_obj.to_dict()
        http_args = http_args or {}
        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=asset_type, http_args=http_args
        )

    def _get_by_id(self, id: str) -> json_api.assets.AssetById:
        """Private API method to get the full metadata of all adapters for a single asset.

        Args:
            id: asset to get all metadata for
        """
        asset_type = self.ASSET_TYPE
        api_endpoint = ApiEndpoints.assets.get_by_id
        return api_endpoint.perform_request(
            http=self.auth.http, asset_type=asset_type, internal_axon_id=id
        )

    def _count(
        self,
        filter: t.Optional[str] = None,
        history_date: t.Optional[str] = None,
        use_cache_entry: bool = False,
        saved_query_id: t.Optional[str] = None,
    ) -> json_api.assets.Count:
        """Private API method to get the count of assets.

        Args:
            filter (t.Optional[str], optional): if supplied,
                only return the count of assets that match the query
            history_date (t.Optional[t.Union[str, timedelta, datetime]], optional): Description
            use_cache_entry (bool, optional): Description

        """
        asset_type = self.ASSET_TYPE
        api_endpoint = ApiEndpoints.assets.count
        request_obj = api_endpoint.load_request(
            use_cache_entry=use_cache_entry,
            filter=filter,
            saved_query_id=saved_query_id,
        )
        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=asset_type
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

    def _history_dates(self) -> json_api.assets.HistoryDates:
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
            name (str): Name of enforcement set to exectue
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
