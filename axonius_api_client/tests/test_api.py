# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.auth."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

import axonius_api_client


class TestApiClient(object):
    """Test axonius_api_client.api.ApiClient."""

    def test_str_repr(self, auth_objs):
        """Test str/repr has URL."""
        for auth_obj in auth_objs:
            api_client = axonius_api_client.api.ApiClient(auth=auth_obj)
            assert "auth" in format(api_client)
            assert "auth" in repr(api_client)


class TestFindAdapter(object):
    """Test axonius_api_client.api.find_adapter."""

    def test_postfix_none(self):
        """Test that _adapter gets added when not known_names."""
        r = axonius_api_client.api.find_adapter(name="known", known_names=None)
        assert r == "known_adapter"

    def test_normal_none(self):
        """Test name with _adapter is returned as is when not known_names."""
        r = axonius_api_client.api.find_adapter(name="known_adapter", known_names=None)
        assert r == "known_adapter"

    def test_postfix(self):
        """Test that _adapter gets added and found in known_names."""
        r = axonius_api_client.api.find_adapter(
            name="known", known_names=["known_adapter"]
        )
        assert r == "known_adapter"

    def test_normal(self):
        """Test that name with _adapter returned as is when found in known_names."""
        r = axonius_api_client.api.find_adapter(
            name="known_adapter", known_names=["known_adapter"]
        )
        assert r == "known_adapter"

    def test_missing(self):
        """Test exc thrown when name not in known_names."""
        with pytest.raises(axonius_api_client.exceptions.UnknownAdapterName):
            axonius_api_client.api.find_adapter(
                name="unknown", known_names=["known_adapter"]
            )


class TestFindField(object):
    """Test axonius_api_client.api.find_field."""

    def test_generic_prefix_none(self):
        """Test that specific_data gets prefixed when not fields & not adapter."""
        r = axonius_api_client.api.find_field(name="field1", fields=None, adapter=None)
        assert r == "specific_data.data.field1"
        r = axonius_api_client.api.find_field(
            name="field1", fields=None, adapter="generic"
        )
        assert r == "specific_data.data.field1"
        r = axonius_api_client.api.find_field(
            name="field1", fields=None, adapter="specific"
        )
        assert r == "specific_data.data.field1"

    def test_generic_normal_none(self):
        """Test that specific_data when not fields & not adapter."""
        r = axonius_api_client.api.find_field(
            name="specific_data.data.field1", fields=None, adapter=None
        )
        assert r == "specific_data.data.field1"
        r = axonius_api_client.api.find_field(
            name="specific_data.data.field1", fields=None, adapter="generic"
        )
        assert r == "specific_data.data.field1"
        r = axonius_api_client.api.find_field(
            name="specific_data.data.field1", fields=None, adapter="specific"
        )
        assert r == "specific_data.data.field1"

    def test_adapter_prefix_none(self):
        """Test that specific_data gets prefixed when not fields & not adapter."""
        r = axonius_api_client.api.find_field(
            name="field1", fields=None, adapter="known"
        )
        assert r == "adapters_data.known_adapter.field1"
        r = axonius_api_client.api.find_field(
            name="field1", fields=None, adapter="known_adapter"
        )
        assert r == "adapters_data.known_adapter.field1"

    # HERE
