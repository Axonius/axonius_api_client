# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import typing as t

import marshmallow
import marshmallow_jsonapi

from .base import BaseSchemaJson


class SystemMetaSchema(BaseSchemaJson):
    """Pass."""

    api_client_version = marshmallow_jsonapi.fields.Str()

    def __init__(self, *args, **kwargs):
        """Pass."""
        self._declared_fields["Build Date"] = marshmallow_jsonapi.fields.Str(
            load_default="", dump_default=""
        )
        self._declared_fields["Customer Id"] = marshmallow_jsonapi.fields.Str(
            load_default="", dump_default=""
        )
        self._declared_fields["Installed Version"] = marshmallow_jsonapi.fields.Str(
            load_default="", dump_default=""
        )
        self._declared_fields["Contract Expiry Date"] = marshmallow_jsonapi.fields.Str(
            load_default="", dump_default=""
        )
        super().__init__(*args, **kwargs)

    class Meta:
        """Pass."""

        type_ = "about_schema"

    @marshmallow.post_load
    def post_load_version(self, data, **kwargs) -> dict:
        """Pass."""
        data["Version"] = data.get("Installed Version")
        return data

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return dict
