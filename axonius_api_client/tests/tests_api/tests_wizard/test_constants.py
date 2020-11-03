# -*- coding: utf-8 -*-
"""Test suite."""
from axonius_api_client.constants.wizards import Entry, Expr
from axonius_api_client.parsers.fields import schema_custom


class TestExpr:
    def test_get_query(self):
        exprs = [
            Expr.build(
                entry={Entry.FLAGS: ["(", "!"], Entry.WEIGHT: -1},
                query="badwolf equals abc",
                field=schema_custom(name="badwolf"),
                idx=0,
                value="abc",
                op_comp="equals",
            ),
            Expr.build(
                entry={Entry.FLAGS: ["|", "!", ")"], Entry.WEIGHT: 1},
                query="badwolf equals def",
                field=schema_custom(name="badwolf"),
                idx=1,
                value="def",
                op_comp="equals",
            ),
            Expr.build(
                entry={Entry.FLAGS: [], Entry.WEIGHT: 0},
                query="another exists",
                field=schema_custom(name="another"),
                idx=2,
                value=None,
                op_comp="exists",
                is_complex=True,
            ),
        ]
        query = Expr.get_query(exprs=exprs)
        exp = "(not badwolf equals abc or not badwolf equals def) and another exists"
        assert query == exp

    def test_get_subs_query(self):
        sub_exprs = [
            Expr.build_child(
                query="badwolf equals abc",
                field="badwolf",
                idx=0,
                value="abc",
                op_comp="equals",
            ),
            Expr.build_child(
                query="badwolf exists",
                field="badwolf",
                idx=1,
                value=None,
                op_comp="exists",
            ),
        ]
        query = Expr.get_subs_query(sub_exprs=sub_exprs)
        exp = "badwolf equals abc and badwolf exists"
        assert query == exp
