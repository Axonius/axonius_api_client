# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

import axonius_api_client


FAKE_FIELDS = {
    "generic": [
        {"name": "specific_data.data.hostname", "title": "Host Name", "type": "string"}
    ],
    "specific": {
        "known_adapter": [
            {
                "name": "adapters_data.known_adapter.hostname",
                "title": "Host Name",
                "type": "string",
            }
        ]
    },
}


def test_max_page_size_invalid():
    """Test exc thrown when page_size > constants.MAX_PAGE_SIZE."""
    page_size = axonius_api_client.constants.MAX_PAGE_SIZE + 100
    with pytest.raises(axonius_api_client.api.exceptions.ApiError):
        axonius_api_client.api.utils.check_max_page_size(page_size=page_size)


@pytest.mark.parametrize("adapter", ["known", "known_adapter"])
class TestFindAdapter(object):
    """Test axonius_api_client.api.utils.find_adapter."""

    @pytest.mark.parametrize("known_names", [None, ["known_adapter"]])
    def test_valid(self, adapter, known_names):
        """Test that _adapter gets added properly."""
        response = axonius_api_client.api.utils.find_adapter(
            name=adapter, known_names=known_names
        )
        assert response == "known_adapter"

    def test_invalid(self, adapter):
        """Test exc thrown when name not in known_names."""
        with pytest.raises(axonius_api_client.api.exceptions.UnknownAdapterName):
            axonius_api_client.api.utils.find_adapter(
                name=adapter, known_names=["other_known_adapter"]
            )


class TestFindFieldGeneric(object):
    """Test axonius_api_client.api.utils.find_field with generic fields."""

    @pytest.mark.parametrize("fields", [None, FAKE_FIELDS])
    @pytest.mark.parametrize("field", ["hostname", "specific_data.data.hostname"])
    def test_valid(self, field, fields):
        """Test field name found and/or prefixed properly."""
        response = axonius_api_client.api.utils.find_field(
            name=field, adapter="generic", fields=fields
        )
        assert response == "specific_data.data.hostname"

    def test_invalid(self):
        """Test exc thrown when field not in FAKE_FIELDS."""
        with pytest.raises(axonius_api_client.api.exceptions.UnknownFieldName):
            axonius_api_client.api.utils.find_field(
                name="unknown_field", adapter="generic", fields=FAKE_FIELDS
            )


@pytest.mark.parametrize("adapter", ["known", "known_adapter"])
class TestFindFieldAdapter(object):
    """Test axonius_api_client.api.utils.find_field with adapter fields."""

    @pytest.mark.parametrize("fields", [None, FAKE_FIELDS])
    @pytest.mark.parametrize(
        "field", ["hostname", "adapters_data.known_adapter.hostname"]
    )
    def test_valid(self, adapter, field, fields):
        """Test field name found and/or prefixed properly."""
        response = axonius_api_client.api.utils.find_field(
            name=field, fields=fields, adapter=adapter
        )
        assert response == "adapters_data.known_adapter.hostname"

    def test_invalid(self, adapter):
        """Test exc thrown when field not in FAKE_FIELDS."""
        with pytest.raises(axonius_api_client.api.exceptions.UnknownFieldName):
            axonius_api_client.api.utils.find_field(
                name="unknown_field", fields=FAKE_FIELDS, adapter=adapter
            )


class TestValidateFields(object):
    """Test axonius_api_client.api.utils.validate_fields."""

    @pytest.mark.parametrize(
        "fields",
        [
            {
                "fields": {"generic": ["hostname", "specific_data.data.hostname"]},
                "expected": ["specific_data.data.hostname"],
            },
            {
                "fields": {"generic": ["hostname"]},
                "expected": ["specific_data.data.hostname"],
            },
            {
                "fields": {"generic": ["hostname"], "known_adapter": ["hostname"]},
                "expected": [
                    "specific_data.data.hostname",
                    "adapters_data.known_adapter.hostname",
                ],
            },
        ],
    )
    def test__validate_fields_valid(self, fields):
        """Test valid dup fields dont show up and prefix gets added properly."""
        response = axonius_api_client.api.utils.validate_fields(
            known_fields=FAKE_FIELDS, ignore_non_list=True, **fields["fields"]
        )
        assert response == fields["expected"]

    def test__validate_fields_invalid_field(self):
        """Test exc thrown when invalid generic field supplied."""
        with pytest.raises(axonius_api_client.api.exceptions.UnknownFieldName):
            axonius_api_client.api.utils.validate_fields(
                known_fields=FAKE_FIELDS, generic=["this_wont_exist_yo"]
            )

    def test__validate_fields_invalid_adapter(self):
        """Test exc thrown when invalid adapter name supplied."""
        with pytest.raises(axonius_api_client.api.exceptions.UnknownAdapterName):
            axonius_api_client.api.utils.validate_fields(
                known_fields=FAKE_FIELDS,
                generic=["hostname"],
                this_wont_exist_yo=["hostname"],
            )
