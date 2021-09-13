# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import warnings
from typing import List, Optional, Type, Union

import dataclasses_json
import marshmallow
import marshmallow_jsonapi

from ...exceptions import (JsonApiError, JsonApiIncorrectType,
                           UnsupportedVersion, ValidationError)
from ...http import Http
from ...tools import listify


class BaseCommon:
    """Pass."""

    @classmethod
    def _check_version(cls, data: dict, api_endpoint=None):
        """Pass."""
        if not isinstance(data, dict) or (isinstance(data, dict) and "data" not in data):
            raise UnsupportedVersion(schema=cls, data=data, api_endpoint=api_endpoint)

    @classmethod
    def _post_load_attrs(cls, loaded, http: Optional[Http] = None, **kwargs):
        """Pass."""
        for item in listify(loaded):
            if isinstance(item, BaseModel):
                item.HTTP = http

    @classmethod
    def _load_schema(cls, schema, data: dict, http: Http, api_endpoint, **kwargs):
        """Pass."""
        try:
            kwargs["loaded"] = loaded = schema.load(data, unknown=marshmallow.INCLUDE)
        except marshmallow.ValidationError as exc:
            raise ValidationError(
                schema=schema, exc=exc, api_endpoint=api_endpoint, obj=cls, data=data
            )
        except marshmallow_jsonapi.exceptions.IncorrectTypeError as exc:
            raise JsonApiError(
                schema=schema, exc=exc, api_endpoint=api_endpoint, obj=cls, data=data
            )

        cls._post_load_attrs(http=http, **kwargs)
        return loaded


class BaseSchema(BaseCommon, marshmallow.Schema):
    """Pass."""

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return dict

    @classmethod
    def load_response(cls, data: Union[dict, list], http: Http, api_endpoint, **kwargs):
        """Pass."""
        many = isinstance(data, (list, tuple))
        schema = cls(many=many)
        return cls._load_schema(schema=schema, data=data, http=http, api_endpoint=api_endpoint)

    @marshmallow.post_load
    def post_load_process(self, data, **kwargs) -> Union[dict, "BaseModel"]:
        """Pass."""
        model_cls = self.get_model_cls()
        data = data or {}
        if hasattr(model_cls, "from_dict"):
            fields_known = [x.name for x in dataclasses.fields(model_cls)]
            # fields_unknown = [x for x in data if x not in fields_known]
            extra = {k: data.pop(k) for k in list(data) if k not in fields_known}
            obj = model_cls.from_dict(data)
            # obj.extra_attributes = {k: v for k, v in data.items() if k in fields_unknown}
            obj.extra_attributes = extra
        else:
            obj = model_cls(**data)
        return obj


class BaseSchemaJson(BaseSchema, marshmallow_jsonapi.Schema):
    """Pass."""

    id = marshmallow_jsonapi.fields.Str()
    document_meta = marshmallow_jsonapi.fields.DocumentMeta()

    class Meta:
        """Pass."""

        type_ = "base_schema"

    @classmethod
    def load_response(cls, data: dict, http: Http, api_endpoint, **kwargs):
        """Pass."""

        def fix_type(item):
            if isinstance(item, dict) and item.get("type") and item["type"] != cls.Meta.type_:
                msg = JsonApiIncorrectType.get_msg(
                    data=data, api_endpoint=api_endpoint, item=item, schema=schema
                )
                warnings.warn(message=msg, category=JsonApiIncorrectType)
                item["type"] = cls.Meta.type_
            return item

        cls._check_version(data=data, api_endpoint=api_endpoint)
        many = isinstance(data["data"], (list, tuple))
        schema = cls(many=many)

        if isinstance(data["data"], (list, tuple)):
            data["data"] = [fix_type(item=x) for x in data["data"]]
        elif isinstance(data["data"], dict):
            data["data"] = fix_type(item=data["data"])

        return cls._load_schema(schema=schema, data=data, http=http, api_endpoint=api_endpoint)


@dataclasses.dataclass
class BaseModel(dataclasses_json.DataClassJsonMixin, BaseCommon):
    """Pass."""

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None

    @classmethod
    def load_response(
        cls,
        data: Union[dict, list],
        http: Http,
        api_endpoint,
        schema_cls: Optional[Type[BaseSchema]] = None,
        **kwargs,
    ):
        """Pass."""
        schema_cls = schema_cls or cls.get_schema_cls() or cls.schema
        many = isinstance(data, (list, tuple))
        schema = schema_cls(many=many)
        return cls._load_schema(schema=schema, data=data, http=http, api_endpoint=api_endpoint)

    @classmethod
    def load_request(cls, api_endpoint=None, http: Optional[Http] = None, **kwargs):
        """Pass."""
        schema = cls.schema()
        return cls._load_schema(schema=schema, data=kwargs, http=http, api_endpoint=api_endpoint)

    def dump_request(
        self, schema_cls: Optional[Type[BaseSchema]] = None, api_endpoint=None, **kwargs
    ) -> Optional[dict]:
        """Pass."""
        schema_cls = schema_cls or self.get_schema_cls() or self.schema
        schema = schema_cls()
        dumped = self.to_dict()

        if isinstance(schema, BaseSchemaJson) and "data" not in dumped:
            dumped = {"data": {"attributes": dumped, "type": schema.Meta.type_}}

        loaded = self._load_schema(schema=schema, data=dumped, http=None, api_endpoint=api_endpoint)
        redumped = schema.dump(loaded)
        return redumped

    def dump_request_params(
        self, schema_cls: Optional[Type[BaseSchema]] = None, api_endpoint=None, **kwargs
    ) -> Optional[dict]:
        """Pass."""
        dumped = self.to_dict()

        for k in list(dumped):
            if isinstance(dumped[k], dict):
                value = dumped.pop(k)
                for a, b in value.items():
                    dumped[f"{k}[{a}]"] = b
        return dumped

    def dump_request_path(
        self, path: str, schema_cls: Optional[Type[BaseSchema]] = None, api_endpoint=None, **kwargs
    ) -> str:
        """Pass."""
        format_args = {}
        format_args.update(self.to_dict())
        format_args.update(kwargs)
        path = path.format(**format_args)
        return path

    def replace_attrs(self, **kwargs) -> "BaseModel":
        """Pass."""
        # TBD: does this do validation?
        return dataclasses.replace(self, **kwargs)

    def __str__(self):
        """Pass."""
        props = self._to_str_properties()
        return self._str_join().join(props) if props else super().__str__()

    @staticmethod
    def _human_key(key):
        """Pass."""
        return key.replace("_", " ").title()

    @staticmethod
    def _str_join() -> str:
        """Pass."""
        return "\n"

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return []

    def _to_str_properties(self) -> List[str]:
        """Pass."""
        ret = []
        for prop in self._str_properties():
            key = self._human_key(prop)
            value = getattr(self, prop, None)
            if (
                isinstance(value, (list, tuple))
                and value
                and not all([isinstance(x, (str, int, bool, float, type(None))) for x in value])
            ):
                ret += [f"{key} #{idx}: {item}" for idx, item in enumerate(value)]
                continue
            ret.append(f"{key}: {value}")
        return ret

    @classmethod
    def _get_fields(cls) -> List[dataclasses.Field]:
        """Get a list of fields defined for current this dataclass object."""
        return dataclasses.fields(cls)
