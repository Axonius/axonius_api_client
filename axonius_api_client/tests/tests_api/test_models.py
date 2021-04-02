# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.models."""
# import pytest
from axonius_api_client.api.models import ApiModel

# from axonius_api_client.tools import get_subcls
# from axonius_api_client.api import json_api


class TestApiModel:
    def test_basic(self, api_client):
        apiobj = ApiModel(client=api_client)
        assert str(apiobj)
        assert repr(apiobj)
        assert apiobj.CLIENT == api_client
        assert apiobj.HTTP == api_client.HTTP
        assert apiobj.LOG


# class TestDataSchemas:
#     def test_subclasses(self):
#         subs = get_subcls(DataSchema)
#         for sub in subs:
#             assert
