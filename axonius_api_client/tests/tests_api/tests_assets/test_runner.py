# -*- coding: utf-8 -*-
"""Test suite for assets."""
import re

import pytest

from axonius_api_client import Runner
from axonius_api_client.api.assets import runner as runner_module
from axonius_api_client.exceptions import ApiWarning, RunnerError, RunnerWarning

from ...utils import random_string, random_strs


class MetaEset:
    name = "badwolf execute"
    main_action_type = "create_notification"
    main_action_name = f"fizzlebot_{random_string(8)}"
    create_args = dict(
        name=name, main_action_name=main_action_name, main_action_type=main_action_type
    )


class RunEnforcements:
    @pytest.fixture(scope="class")
    def exec_eset(self, apiobj):
        self.cleanup(apiobj, MetaEset.name)
        with pytest.warns(ApiWarning):
            eset = apiobj.enforcements.create(**MetaEset.create_args)
        yield eset
        self.cleanup(apiobj, MetaEset.name)

    def cleanup(self, apiobj, name, exists=False):
        try:
            ret = apiobj.enforcements.delete(name)
        except Exception:
            if exists:
                print(f"Not able to cleanup eset {name}")
        else:
            print(f"Removed eset {name}: {ret}")


class TestRunEnforcement(RunEnforcements):
    @pytest.fixture(params=["api_devices"], scope="class")
    def apiobj(self, request):
        return request.getfixturevalue(request.param)

    def test_all_false(self, apiobj, exec_eset):
        with pytest.raises(RunnerError, match=re.escape(Runner._tall_n)):
            apiobj.run_enforcement(
                eset=exec_eset, ids=apiobj.IDS, verified=False, verify_count=False
            )

    def test_verify_count_matches(self, apiobj, exec_eset):
        with pytest.warns(RunnerWarning, match=re.escape(Runner._tstate_count_matches)):
            runner = apiobj.run_enforcement(eset=exec_eset, ids=apiobj.IDS)
        assert runner.is_match is True
        assert runner.state == runner._tstate_ran
        assert runner.executed is True

    def test_verify_count_mismatches(self, apiobj, exec_eset):
        ids = apiobj.IDS + random_strs(num=1, length=32)
        runner = apiobj.run_enforcement(eset=exec_eset, ids=ids, verify_and_run=False)
        with pytest.raises(RunnerError, match=re.escape(Runner._tstate_count_mismatches)):
            runner.verify_and_run()
        assert runner.is_match is False
        assert runner.state == runner._tstate_count_mismatches
        assert runner.executed is False

    def test_verified_true(self, apiobj, exec_eset):
        runner = apiobj.run_enforcement(eset=exec_eset, ids=apiobj.IDS, verified=True)
        assert runner.state.startswith(runner._tran_pre)
        with pytest.raises(RunnerError, match=re.escape(runner._trun_ran)):
            runner.run()
        with pytest.warns(RunnerWarning, match=re.escape(runner._trun_ran)):
            runner.run(force=True)
        assert str(runner)
        assert repr(runner)

    def test_run_not_verified(self, apiobj, exec_eset):
        runner = apiobj.run_enforcement(eset=exec_eset, ids=apiobj.IDS, verify_and_run=False)
        with pytest.raises(RunnerError, match=re.escape(runner._trun_notv)):
            runner.run()

    def test_count_warning(self, apiobj, exec_eset, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(Runner, "_count_warn", 2)
            runner = apiobj.run_enforcement(
                eset=exec_eset,
                ids=random_strs(num=Runner._count_warn),
                verify_and_run=False,
            )
            runner.count_result = Runner._count_warn
            with pytest.warns(RunnerWarning, match=re.escape(Runner._tcount_warn_pre)):
                runner.verify()

    def test_count_error(self, apiobj, exec_eset, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(Runner, "_count_error", 3)
            runner = apiobj.run_enforcement(
                eset=exec_eset,
                ids=random_strs(num=Runner._count_error),
                verify_and_run=False,
            )
            runner.count_result = Runner._count_error
            with pytest.raises(RunnerError, match=re.escape(Runner._tcount_error_pre)):
                runner.verify()

    def test_no_ids(self, apiobj, exec_eset):
        with pytest.raises(RunnerError, match=re.escape(Runner._tno_ids)):
            apiobj.run_enforcement(
                eset=exec_eset,
                ids="",
                verify_and_run=False,
            )

    def test_no_valid_ids(self, apiobj, exec_eset):
        with pytest.raises(RunnerError, match=re.escape(Runner._tno_ids)):
            apiobj.run_enforcement(
                eset=exec_eset,
                ids=random_strs(num=3, length=31),
                verify_and_run=False,
            )

    def test_prompt_matches_y(self, apiobj, exec_eset, monkeypatch):
        def confirm(*args, **kwargs):
            return True

        with monkeypatch.context() as m:
            m.setattr(target=runner_module, name="confirm", value=confirm)
            runner = apiobj.run_enforcement(
                eset=exec_eset,
                ids=apiobj.IDS,
                prompt=True,
                verify_and_run=False,
            )
            assert runner.prompt is True
            assert runner.do_echo is True
            runner.verify()
            assert runner.state.startswith(runner._tchoice_y)
            assert runner.verified is True
            runner.run()
            assert runner.executed is True

    def test_prompt_matches_n(self, apiobj, exec_eset, monkeypatch):
        def confirm(*args, **kwargs):
            return False

        with monkeypatch.context() as m:
            m.setattr(target=runner_module, name="confirm", value=confirm)
            runner = apiobj.run_enforcement(
                eset=exec_eset,
                ids=apiobj.IDS,
                prompt=True,
                verify_and_run=False,
            )
            assert runner.prompt is True
            assert runner.do_echo is True
            with pytest.raises(RunnerError, match=re.escape(runner._tchoice_n)):
                runner.verify()
            assert runner.state.startswith(runner._tchoice_n)
            assert runner.verified is False
            with pytest.raises(RunnerError, match=re.escape(runner._trun_notv)):
                runner.run()
            assert runner.executed is False
