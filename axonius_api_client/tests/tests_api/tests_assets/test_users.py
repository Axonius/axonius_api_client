# -*- coding: utf-8 -*-
"""Test suite for assets."""
import pytest

from .base_assets import (
    AssetsPrivate,
    AssetsPublic,
    ModelMixinsBase,
    check_assets,
    get_field_values,
    load_test_data,
)


class TestUsers(AssetsPrivate, AssetsPublic, ModelMixinsBase):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        """Pass."""
        return load_test_data(apiobj=api_users)

    def test_get_by_username(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_USERNAME

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]

        rows = apiobj.get_by_username(
            value=value, field=field, fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)
        assert len(rows) == 1

        rows_values = get_field_values(rows=rows, field=field)
        assert value in rows_values

    def test_get_by_username_equals_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_USERNAME

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]

        rows = apiobj.get_by_username(
            value=value,
            field=field,
            fields_map=apiobj.TEST_DATA["fields_map"],
            not_flag=True,
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        assert value not in rows_values

    def test_get_by_usernames(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_USERNAME

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        values = values[0:2]

        rows = apiobj.get_by_usernames(
            values=values, field=field, fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        for value in values:
            assert value in rows_values

    def test_get_by_usernames_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_USERNAME

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        values = values[0:2]

        rows = apiobj.get_by_usernames(
            values=values,
            field=field,
            fields_map=apiobj.TEST_DATA["fields_map"],
            not_flag=True,
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        for value in values:
            assert value not in rows_values

    def test_get_by_username_regex(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_USERNAME

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]
        regex_value = value[0:5]

        rows = apiobj.get_by_username_regex(
            value=regex_value, fields_map=apiobj.TEST_DATA["fields_map"], field=field,
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        assert value in rows_values

    def test_get_by_username_regex_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_USERNAME

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]
        regex_value = value[0:5]

        rows = apiobj.get_by_username_regex(
            value=regex_value,
            field=field,
            not_flag=True,
            fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        assert value not in rows_values

    def test_get_by_mail(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_MAIL

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]

        rows = apiobj.get_by_mail(
            value=value, field=field, fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)
        assert len(rows) >= 1

        rows_values = get_field_values(rows=rows, field=field)
        assert value in rows_values

    def test_get_by_mail_equals_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_MAIL

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]

        rows = apiobj.get_by_mail(
            value=value,
            field=field,
            fields_map=apiobj.TEST_DATA["fields_map"],
            not_flag=True,
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        assert value not in rows_values

    def test_get_by_mails(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_MAIL

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        values = values[0:2]

        rows = apiobj.get_by_mails(
            values=values, field=field, fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        for value in values:
            assert value in rows_values

    def test_get_by_mails_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_MAIL

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        values = values[0:2]

        rows = apiobj.get_by_mails(
            values=values,
            field=field,
            fields_map=apiobj.TEST_DATA["fields_map"],
            not_flag=True,
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        for value in values:
            assert value not in rows_values

    def test_get_by_mail_regex(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_MAIL

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]
        regex_value = value[0:5]

        rows = apiobj.get_by_mail_regex(
            value=regex_value, field=field, fields_map=apiobj.TEST_DATA["fields_map"],
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        assert value in rows_values

    def test_get_by_mail_regex_not(self, apiobj):
        """Pass."""
        field = apiobj.FIELD_MAIL

        values = get_field_values(rows=apiobj.TEST_DATA["assets"], field=field)
        value = values[0]
        regex_value = value[0:5]

        rows = apiobj.get_by_mail_regex(
            value=regex_value,
            field=field,
            fields_map=apiobj.TEST_DATA["fields_map"],
            not_flag=True,
        )
        check_assets(rows)

        rows_values = get_field_values(rows=rows, field=field)
        assert value not in rows_values
