# -*- coding: utf-8 -*-
"""API model mixin for device and user assets."""
import dataclasses
import logging
import textwrap
import typing as t

from ...constants.fields import AXID
from ...data import BaseData
from ...exceptions import RunnerError, RunnerWarning
from ...parsers.grabber import Grabber, Mixins
from ...tools import confirm, csv_able, is_str, listify, style_switch

# from .. import json_api
from ..json_api.enforcements import (
    EnforcementBasicModel,
    EnforcementFullModel,
    UpdateEnforcementResponseModel,
)

ENFORCEMENT: t.TypeVar = t.Union[
    str,
    dict,
    EnforcementBasicModel,
    EnforcementFullModel,
    UpdateEnforcementResponseModel,
]


NOTES: str = """# Run Enforcement via manual selection

## Required Arguments

- $eset (str): name or uuid of enforcement set to run
- $ids (list[str]): list of internal_axon_id's to run $eset against

## Optional Arguments

- $verify_count (bool): default=True
- $verified (bool): default=False
- $prompt (bool): default=True if running from axonshell else False
- $do_echo (bool): default=False
- $refetch (bool): default=False

## Calculations

- $ids_csv (str): comma separated list of $ids
- $query (str): build AQL like "internal_axon_id in [$ids_csv]"
- $count_result (int): get the count of $query from the API
- $count_ids (int): the count of supplied $ids
- $count_warn (int): 100
- $count_error (int): 100000
- $is_match (bool): $count_ids equals $count_result

## FlowTypes: VERIFY

- If not $verified and not $verify_count
  - ERROR(must supply verified or verify_count as True)
- If $count_ids is greater than $count_error
  - ERROR(Query length is over error limit - please create EC + SQ to run)
- If $count_ids is greater than $count_warn:
  - WARN(Query length is over warning limit - recommend create EC + SQ to run)
- If $verified:
  - set $state=user set $verified=True, skipping verification
  - RUN()
- If $verify_count:
  - GET_COUNT_RESULT()
  - $action=accept count match/mismatch and run $eset against $count_ids assets
  - If $prompt:
    - get $answer by prompting user for $action (default:$is_match)
    - If $answer=True:
      - set $verified=True
      - set $state=user chose to $action
      - RUN()
    - If $answer=False:
      - set $verified=False
      - set $state=user chose not to $action
      - ERROR($state)
  - If not $prompt:
    - If $is_match:
      - set $verified=True
      - set $state=WARN:runner set $verified=True because $is_match=True
      - RUN()
    - If not $is_match:
      - set $verified=False
      - set $state=re-run with $prompt=True or $verified=True to $action
      - ERROR($state)

## FlowTypes: RUN

- If verification has not been performed:
  - If $force=False: ERROR(not verified yet, must supply force=True)
  - if $force=True: RUN(running with force=True)
- If already run:
  - If $force=False: ERROR(already run, must supply force=True)
  - if $force=True: RUN(running with force=True)
- If $verified is False:
  - If $force=False: ERROR(verified is False, must supply force=True)
  - if $force=True: RUN(running with force=True)
- Send API request to execute
"""
NOTES_DOC: str = textwrap.indent(NOTES.lstrip(), prefix=" " * 8)


@dataclasses.dataclass
class Runner(BaseData, Mixins):
    f"""Run an Enforcement Set against a manually provided list of Asset IDs.

    Notes:
        {NOTES_DOC}

    Arguments:
        apiobj (:obj:`axonius_api_client.api.AssetMixin`): asset object to use
            for making calls
        eset (ENFORCEMENT): name, uuid, or Enforcement Set object to run
        ids (t.Union[str, t.List[str]]): Asset IDs to run Enforcement Set against,
            csv-like string or list of csv-like strings
        verified (bool): $ids already verified, just run $eset against $ids
        verify_count (bool): Verify that the count of $query equals the count of $ids
        prompt (bool): Prompt user for verification when applicable.
        do_echo (bool): Echo output to console as well as log
        refetch (bool): refetch $eset even if it is a model
    """

    apiobj: object
    """:obj`axonius_api_client.api.assets.asset_mixin.AssetMixin`"""

    eset: ENFORCEMENT
    """name, uuid, or Enforcement Set object to run"""

    ids: t.Union[str, t.List[str]]
    """Asset IDs to run $eset against, csv-like string or list of csv-like strings"""

    verified: bool = False
    """$ids already verified, just run $eset against $ids."""

    verify_count: bool = True
    """Check that the $count_result matches $count_ids."""

    prompt: bool = False
    """Prompt user when applicable."""

    do_echo: bool = False
    """Echo output to console as well as log"""

    refetch: bool = False
    """refetch $eset even if it is a model"""

    src_query: t.Optional[str] = None
    """direct api support, unknown"""

    src_fields: t.Optional[t.List[str]] = None
    """direct api support, unknown"""

    check_stdin: bool = True
    """Check if stdin is a TTY when prompting."""

    grabber: t.Optional[Grabber] = None
    """Grabber used to get IDs."""

    log: t.ClassVar[logging.Logger] = None
    result: t.ClassVar[str] = None
    _count_result: t.ClassVar[int] = None
    _initialized: t.ClassVar[bool] = False
    _executed: t.ClassVar[bool] = False
    _count_warn: t.ClassVar[int] = 100
    _count_error: t.ClassVar[int] = 100000
    _state: t.ClassVar[str] = "initializing"
    _states: t.ClassVar[t.Optional[t.List[str]]] = None
    _tall_n: t.ClassVar[str] = "Re-run with $verified=True or $verify_count=True"
    _tconfirm_pre: t.ClassVar[str] = "Are you sure you want to "
    _tcount_error_cond: t.ClassVar[str] = "error"
    _tcount_error_pre: t.ClassVar[str] = "Please use"
    _tcount_warn_cond: t.ClassVar[str] = "warning"
    _tcount_warn_pre: t.ClassVar[str] = "We recommend using"
    _tforce_n: t.ClassVar[str] = " -- not running due to force=False!"
    _tforce_y: t.ClassVar[str] = " -- running anyways due to force=True"
    _tno_ids: t.ClassVar[str] = "No valid Asset IDs supplied to $ids!!"
    _tran_pre: t.ClassVar[str] = "Ran Enforcement Set"
    _trun_notv: t.ClassVar[str] = "Verification has not been performed"
    _trun_pre: t.ClassVar[str] = "Running Enforcement Set"
    _trun_ran: t.ClassVar[str] = "Enforcement Set has already been run"
    _tstate_checked_limits: t.ClassVar[str] = "checked $count_warn/$count_error"
    _tstate_count_matches: t.ClassVar[str] = "runner set $verified=True because $is_match=True!"
    _tstate_count_mismatches: t.ClassVar[str] = "verification failed - $is_match=False"
    _tstate_verify_y: t.ClassVar[str] = "user supplied $verified=True - running Enforcement Set"
    _tchoice_y: t.ClassVar[str] = "user chose to"
    _tchoice_n: t.ClassVar[str] = "user chose NOT to"
    _tnotes: t.ClassVar[str] = NOTES
    _exc_cls: t.ClassVar[Exception] = RunnerError
    _warn_cls: t.ClassVar[Warning] = RunnerWarning

    def verify_and_run(self):
        """Verify $ids and run $eset."""
        self.init()
        self.verify()
        return self.run()

    def verify(self):
        """Evaluate $verify_count and $verified."""
        self.init()

        if not any([self.verified, self.verify_count]):
            self.spew(msgs=self._tall_n, exc=True)

        self.check_limits()

        if self.verified:
            self.state = self._tstate_verify_y
            self.spew(msgs=self.state)
            return

        if self.verify_count:
            self.check_count()

        return

    def run(self, force: bool = False):
        """Run the Enforcement Set.

        Args:
            force (bool, optional): if verified=False or already run, ignore and run anyway

        """
        self.init()
        self.state = self._tstate_run_eval

        sargs = {"exc": True}
        post = self._tforce_n

        if force:
            sargs = {"warn": True}
            post = self._tforce_y

        if not self.verified:
            self.spew(msgs=f"{self._trun_notv}{post}", **sargs)

        if self.executed:
            self.spew(msgs=f"{self._trun_ran}{post}", **sargs)

        self.result = self._run()
        self.executed = True
        self.spew(msgs=self.state)
        return self.result

    def init(self, redo: bool = False):
        """Initialize the Runner."""
        if not self._initialized or redo:
            self.log = self.apiobj.LOG.getChild(self.__class__.__name__)
            self._count_result = None
            self._result = None
            self._initialized = False
            self._executed = False
            self.state = "initialized!"
            self._initialized = True
            self.get_eset()

    def check_limits(self):
        """Check if $count_ids is past warning or error threshold."""
        if self.count_ids >= self.count_error:
            self.spew(msgs=self._tlimit_error, exc=True)
        if self.count_ids >= self.count_warn:
            self.spew(msgs=self._tlimit_warn, warn=True)
        self.state = self._tstate_checked_limits

    def check_count(self):
        """Get the count of assets matching $query, prompting as necessary."""
        self.get_count()
        self._check_count_prompt() if self.prompt else self._check_count()

    def _check_count(self):
        if self.is_match:
            self.verified = True
            self.state = self._tstate_count_matches
            self.spew(msgs=self.state, warn=True)
        else:
            self.state = self._tstate_count_mismatches
            self.spew(msgs=[self.state, self._trerun], exc=True)

    def _check_count_prompt(self):
        self.verified = self.confirm(action=self._tcount_action, default=self.is_match)
        if self.verified:
            self.state = f"{self._tchoice_y} {self._tcount_action}"
            self.spew(msgs=self.state)
        else:
            self.state = f"{self._tchoice_n} {self._tcount_action}"
            self.spew(msgs=self.state, exc=True)

    def confirm(
        self,
        action: str,
        top: bool = True,
        default: bool = False,
        msgs: t.Optional[t.List[str]] = None,
        **kwargs,
    ) -> bool:
        """Prompt user for confirmation."""
        pre = kwargs.get("pre", self._tconfirm_pre)
        msgs = self.infos(msgs=msgs, top=top)
        action = style_switch(text=action, switch=default)
        answer = confirm(
            msgs=msgs, text=f"{pre}{action}", default=default, check_stdin=self.check_stdin
        )
        return answer

    def get_eset(self):
        """Get the Enforcement Set object."""
        self.eset = self.apiobj.enforcements.get_set(value=self.eset, refetch=self.refetch)

    def get_count(self, refetch: bool = False):
        """Get $count_result from API using $query as a filter."""
        if refetch or not isinstance(self.count_result, int):
            self.state = self._tstate_get_count
            self.count_result = self.apiobj.count(query=self.query)
            self.state = self._tstate_got_count

    def infos(self, msgs: t.Optional[t.List[str]] = None, top: bool = True) -> t.List[str]:
        """Get info on runner."""
        ret = []
        infos = []
        if top:
            infos += [
                self._tstate,
                *self._teset_infos,
                *self._infos(title="Arguments", infos=self._info_args_desc()),
                *self._infos(title="Caclulations", infos=self._info_calcs_desc()),
            ]

            ret += infos
        msgs = listify(msgs)
        if msgs:
            ret += ["", *msgs] if ret else msgs
        return ret

    @property
    def query(self) -> str:
        """AQL to use to get count of assets matching $ids."""
        return f'("{AXID.name}" in [{self.ids_csv}])'

    @property
    def executed(self) -> bool:
        """The Enforcement Set has been executed already."""
        return self._executed

    @executed.setter
    def executed(self, value: bool):
        self._executed = value

    @property
    def count_warn(self) -> int:
        """Warn if trying to run $eset against this many Asset IDs."""
        return self._count_warn

    @property
    def count_error(self) -> int:
        """Error if trying to run $eset against this many Asset IDs."""
        return self._count_error

    @property
    def count_ids(self) -> int:
        """Count of Asset IDs supplied to $ids argument."""
        return len(self.ids)

    @property
    def count_result(self) -> t.Optional[int]:
        """The count of Asset IDs fetched from API using $query as a filter."""
        return self._count_result

    @count_result.setter
    def count_result(self, value: int):
        self._count_result = value

    @property
    def is_match(self) -> t.Optional[bool]:
        """$count_ids equals $count_result."""
        if isinstance(self.count_result, int):
            return self.count_ids == self.count_result
        return None

    @property
    def ids_csv(self) -> str:
        """The Asset IDs supplied in $ids formatted into a CSV string usable in AQL."""
        return ", ".join([f'"{x}"' for x in self.ids])

    @property
    def state(self) -> str:
        """The current status of runner."""
        return self._state

    @state.setter
    def state(self, value: str):
        if is_str(value):
            self._state = value
            if not isinstance(self._states, list):
                self._states = []
            self._states.append(value)
            self.spew(msgs=f"{self._tstate_change_pre} {value}", level="debug", top=False)

    @property
    def _trun_post(self) -> str:
        return f"against {self.count_ids} supplied Asset IDs"

    @property
    def _tstate_run_eval(self) -> str:
        return f"evaluating conditions for running Enforcement Set {self._teset}"

    @property
    def _tstate(self) -> str:
        return f"{self.__class__.__name__} state: {self.state}"

    @property
    def _tloadedids(self) -> str:
        return f"Loaded Asset IDs: {self.ids}"

    @property
    def _tquery(self) -> str:
        return f"$query={self.query}"

    @property
    def _tstr_items(self) -> t.List[str]:
        return [
            f"state={self.state!r}",
            f"eset={self._teset!r}",
            f"executed={self.executed}",
            f"count_ids={self.count_ids}",
            f"count_result={self.count_result}",
            f"verified={self.verified}",
            f"verify_count={self.verify_count}",
            f"prompt={self.prompt}",
            f"grabber={self.grabber}",
        ]

    @property
    def _teset(self) -> str:
        ret = f"{self.eset}"
        if isinstance(self.eset, EnforcementFullModel):
            ret = f"{self.eset.name}"
        return ret

    @property
    def _teset_infos(self) -> t.List[str]:
        """Build info for the Enforcement Set supplied to $eset."""
        obj = self.eset
        details = [f"Not yet fetched: {obj!r}"]
        if isinstance(obj, EnforcementFullModel):
            details = [
                f"Name: {obj.name!r} (UUID: {obj.uuid})",
                f"Description: {obj.description!r}",
                f"Main Action: name={obj.main_action_name!r} (type={obj.main_action_type!r})",
                f"Updated: user={obj.updated_user!r} (date={str(obj.updated_date)!r})",
            ]
        return ["Enforcement Set Details:", *[f"  {x}" for x in details]]

    @property
    def _tmatch(self) -> str:
        return "match" if self.is_match else "MISMATCH"

    @property
    def _trun(self) -> str:
        return f"run Enforcement Set {self._teset} against {self.count_ids} Asset IDs"

    @property
    def _tcount_action(self) -> str:
        return f"accept the count {self._tmatch} and {self._trun}"

    @property
    def _trerun(self) -> str:
        return f"re-run with $prompt=True or $verified=True in order to {self._tcount_action}"

    @property
    def _tstate_change_pre(self) -> str:
        return f"{self.__class__.__name__}.state changed to:"

    @property
    def _tsteps(self) -> t.List[str]:
        return [
            "Create a new Saved Query that targets this same set of Assets.",
            "Create a new Enforcement Set that uses the new Saved Query as a trigger.",
            "Execute the new Enforcement Set using the trigger manually (or via scheduling).",
        ]

    @property
    def _tsteps_num(self) -> t.List[str]:
        return [f"  {n + 1}.) {x}" for n, x in enumerate(self._tsteps)]

    @property
    def _tlimit2_post(self) -> str:
        return "a different approach to run an Enforcement Set against this many Asset IDs:"

    @property
    def _tlimit2_error(self) -> str:
        return f"{self._tcount_error_pre} {self._tlimit2_post}"

    @property
    def _tlimit2_warn(self) -> str:
        return f"{self._tcount_warn_pre} {self._tlimit2_post}"

    @property
    def _tlimit1_error(self) -> str:
        return self._tlimit1_tmpl.format(cond=self._tcount_error_cond, value=self.count_error)

    @property
    def _tlimit1_warn(self) -> str:
        return self._tlimit1_tmpl.format(cond=self._tcount_warn_cond, value=self.count_warn)

    @property
    def _tlimit1_tmpl(self) -> str:
        return f"{self.count_ids} Asset IDs were supplied but the {{cond}} limit is {{value}}"

    @property
    def _tlimit_error(self) -> t.List[str]:
        return [self._tlimit1_error, "", self._tlimit2_error, *self._tsteps_num]

    @property
    def _tlimit_warn(self) -> t.List[str]:
        return [self._tlimit1_warn, "", self._tlimit2_warn, *self._tsteps_num]

    @property
    def _tget_count_post(self) -> str:
        return f"using $query built from $count_ids={self.count_ids} Asset IDs"

    @property
    def _tstate_get_count(self) -> str:
        return f"getting $count_result {self._tget_count_post}"

    @property
    def _tstate_got_count(self) -> str:
        return f"fetched $count_result {self.count_result} {self._tget_count_post}"

    @property
    def _tstate_run(self) -> str:
        return f"{self._trun_pre} {self._trun_post}"

    @property
    def _tstate_ran(self) -> str:
        return f"{self._tran_pre} {self._trun_post}"

    def _run(self):
        """Actual workflow to run an Enforcement Set."""
        self.state = self._tstate_run
        ret = self.apiobj._run_enforcement(
            name=self.eset.name, ids=self.ids, fields=self.src_fields, query=self.src_query
        )
        self.state = self._tstate_ran
        return ret

    def _infos(self, title: str, infos: dict) -> t.List[str]:
        """Build info for a section."""
        return [
            "",
            f"{title.title()}:",
            *[f"  # {infos[k]}\n  {k} = {v}" for k, v in [(x, self._get(x)) for x in infos]],
        ]

    def _get(self, key: str) -> t.Any:
        return getattr(self, key, None)

    @classmethod
    def _info_args_desc(cls) -> dict:
        """Descriptions for arguments section."""
        ret = dict(
            verified="$ids have already been verified, run $eset against them",
            verify_count="verify that $count_result from $query equals $count_ids",
            prompt="prompt if $verified=False and $is_match=False",
        )
        return ret

    @property
    def _info_calcs(self) -> t.List[str]:
        return ["count_warn", "count_error", "count_ids", "count_result", "is_match"]

    def _info_calcs_desc(self) -> dict:
        """Descriptions for calculations section."""
        ret = {k: getattr(self.__class__, k).__doc__ for k in self._info_calcs}
        return ret

    @property
    def _tids(self) -> str:
        return f"$ids={self.ids!r}"

    def __post_init__(self):
        """Dataclass setup."""
        self.init()
        self._states = []
        self.src_fields = [x for x in csv_able(value=self.src_fields)]

        if self.prompt:
            self.do_echo = True

        ids = [x for x in csv_able(self.ids) if AXID.is_axid(x)]

        if not ids:
            raise RunnerError(self.infos(msgs=[self._tno_ids, self._tids, "", *AXID.rules]))

        self.ids = ids
        self.log.debug(self._tloadedids)
        self.log.debug(self._tquery)

    def __repr__(self) -> str:
        """Dunder."""
        return self.__str__()
