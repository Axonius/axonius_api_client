# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import logging
from typing import List, Optional, Type, Union

import dataclasses_json
import marshmallow
import marshmallow_jsonapi

from ...constants.general import SIMPLE
from ...exceptions import ApiAttributeMissingError, ApiAttributeTypeError, ApiError, SchemaError
from ...http import Http
from ...tools import coerce_bool, combo_dicts, json_dump, json_load, listify

LOGGER = logging.getLogger(__name__)


class BaseCommon:
    """Common methods for all schema and model classes."""

    @classmethod
    def _post_load_attrs(
        cls, data: Union["BaseModel", List["BaseModel"]], http: Optional[Http] = None, **kwargs
    ):
        """Add HTTP object as an attribute to any loaded model.

        Args:
            data (Union["BaseModel", List["BaseModel"]]): Loaded model(s)
            http (Optional[Http], optional): HTTP object to set on loaded model(s)
            **kwargs: n/a
        """
        for item in listify(data):
            try:
                item.HTTP = http
            except Exception:  # pragma: no cover
                pass

    @classmethod
    def _load_schema(
        cls, schema: marshmallow.Schema, data: Union[dict, List[dict]], **kwargs
    ) -> Union["BaseModel", List["BaseModel"]]:
        """Load data using a marshmallow schema.

        Args:
            schema (marshmallow.Schema): Schema to use to load data
            data (Union[dict, List[dict]]): Data to load
            **kwargs: passed to :meth:`_post_load_attrs`

        Returns:
            Union["BaseModel", List["BaseModel"]]: Loaded model(s)

        Raises:
            JsonApiError: when "type" of JSON API data does not match Meta._type of schema
            ValidationError: when marshmallow schema validation fails
        """
        try:
            loaded = schema.load(data, unknown=marshmallow.INCLUDE)
        except Exception as exc:
            raise SchemaError(schema=schema, exc=exc, obj=cls, data=data)

        cls._post_load_attrs(data=loaded, **kwargs)
        return loaded


class BaseSchema(BaseCommon, marshmallow.Schema):
    """Schema base class for validating non JSON API data."""

    @staticmethod
    def get_model_cls() -> Union["BaseModel", type]:
        """Get the BaseModel or type that data should be loaded into.

        Returns:
            Union["BaseModel", type]: BaseModel to load data into, or callable (i.e. dict)

        Raises:
            NotImplementedError: Sub classes MUST define this.
        """
        raise NotImplementedError()

    @classmethod
    def load_response(
        cls, data: Union[dict, list, tuple], **kwargs
    ) -> Union["BaseModel", List["BaseModel"]]:
        """Load data using this schema.

        Args:
            data (Union[dict, list, tuple]): Response data to load using this schema
            **kwargs: passed to :meth:`BaseCommon._load_schema`

        Returns:
            Union["BaseModel", List["BaseModel"]]: Loaded model(s)

        Raises:
            SchemaError: if data is not a dict or list
        """
        many = isinstance(data, (list, tuple))
        schema = cls(many=many)

        if not isinstance(data, (dict, list, tuple)):
            exc = ApiError(
                f"Data to load must be a dictionary or list, not a {type(data).__name__}"
            )
            raise SchemaError(schema=schema, exc=exc, data=data, obj=cls)

        return cls._load_schema(**combo_dicts(kwargs, schema=schema, data=data))

    @marshmallow.post_load
    def post_load_process(self, data: dict, **kwargs) -> Union[dict, "BaseModel"]:
        """Marshmallow post_load hook to load validated data into a model class.

        Args:
            data (dict): validated data to load
            **kwargs: n/a

        Returns:
            Union[dict, "BaseModel"]: Loaded data model
        """
        model_cls = self.get_model_cls()
        data = data or {}

        if not dataclasses.is_dataclass(model_cls):
            return model_cls(**data) if callable(model_cls) else data

        # fields_known = [x.name for x in dataclasses.fields(model_cls)]
        # extra_attributes = {k: data.pop(k) for k in list(data) if k not in fields_known}
        obj = model_cls.from_dict(data)
        # obj.extra_attributes = extra_attributes
        return obj


class BaseSchemaJson(BaseSchema, marshmallow_jsonapi.Schema):
    """Schema base class for validating JSON API data."""

    id = marshmallow_jsonapi.fields.Str()
    document_meta = marshmallow_jsonapi.fields.DocumentMeta()

    class Meta:
        """Pass."""

        type_ = "base_schema"

    @classmethod
    def load_response(cls, data: dict, **kwargs) -> Union["BaseModel", List["BaseModel"]]:
        """Load data using this JSON API schema.

        Args:
            data (dict): Response data to load using this schema
            **kwargs: passed to :meth:`BaseCommon._load_schema`

        Returns:
            Union["BaseModel", List["BaseModel"]]: Loaded model(s)

        Raises:
            SchemaError: if data is not a dict
        """
        many = isinstance(data, dict) and isinstance(data.get("data"), (list, tuple))
        schema = cls(many=many)
        if not isinstance(data, dict):
            exc = ApiError(f"Data to load must be a dictionary, not a {type(data).__name__}")
            raise SchemaError(schema=schema, exc=exc, data=data, obj=cls)
        return cls._load_schema(**combo_dicts(kwargs, schema=schema, data=data))


@dataclasses.dataclass
class BaseModel(dataclasses_json.DataClassJsonMixin, BaseCommon):
    """Model base class for holding data."""

    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Get the BaseSchema that should be used to validate the data for this model.

        Returns:
            Optional[Type[BaseSchema]]: BaseSchema to use to verify data

        Raises:
            NotImplementedError: Sub classes MUST define this.
        """
        raise NotImplementedError()

    @classmethod
    def load_response(
        cls, data: Union[dict, list, tuple], schema_cls: Optional[BaseSchema] = None, **kwargs
    ) -> Union["BaseModel", List["BaseModel"]]:
        """Load data using this JSON API schema.

        Args:
            data (Union[dict, list, tuple]): Response data to load using this schema
            schema_cls (Optional[BaseSchema], optional): Schema class to use to validate data
                will fallback to :meth:`get_schema_cls` or dataclasses_json automatic schema
            **kwargs: passed to :meth:`BaseCommon._load_schema`

        Returns:
            Union["BaseModel", List["BaseModel"]]: Loaded model(s)

        Raises:
            SchemaError: if data is not a dict or list
        """
        schema_cls = schema_cls or cls.get_schema_cls() or cls.schema
        if callable(getattr(schema_cls, "load_response", None)):
            return schema_cls.load_response(data=data, **kwargs)

        many = isinstance(data, (list, tuple))
        schema = schema_cls(many=many)
        if not isinstance(data, (dict, list, tuple)):
            exc = ApiError(
                f"Data to load must be a dictionary or list, not a {type(data).__name__}"
            )
            raise SchemaError(schema=schema, exc=exc, data=data, obj=cls)
        return cls._load_schema(**combo_dicts(kwargs, schema=schema, data=data))

    @classmethod
    def load_request(cls, **kwargs) -> "BaseModel":
        """Create an instance of this model using the dataclasses_json generated schema.

        Args:
            **kwargs: passed to :meth:`BaseCommon._load_schema`, keys must be valid
                fields defined in this dataclass

        Returns:
            BaseModel: loaded model
        """
        schema = cls.schema()
        return cls._load_schema(schema=schema, data=kwargs)

    def dump_request(self, schema_cls: Optional[BaseSchema] = None, **kwargs) -> dict:
        """Convert this model into a dictionary for sending as a request.

        This does a bunch of fancy foot work to re-validate the data using marshmallow schema
        if possible.

        Args:
            schema_cls (Optional[BaseSchema], optional): Schema class to use to validate data
                will fallback to :meth:`get_schema_cls` or dataclasses_json automatic schema
            **kwargs: passed to :meth:`BaseCommon._load_schema` as part of reloading the data
                to validate it

        Returns:
            dict: serialized dict of this model
        """
        schema_cls = schema_cls or self.get_schema_cls() or self.schema
        schema = schema_cls()
        dumped = self.to_dict()

        if isinstance(schema, BaseSchemaJson) and "data" not in dumped:
            dumped = {"data": {"attributes": dumped, "type": schema.Meta.type_}}

        loaded = self._load_schema(**combo_dicts(kwargs, schema=schema, data=dumped))
        redumped = schema.dump(loaded)
        return redumped

    def dump_request_params(self, **kwargs) -> dict:
        """Convert this object into a set of GET URL parameters.

        Args:
            **kwargs: n/a

        Returns:
            dict: serialized URL parameters to send for a GET request
        """
        dumped = json_load(obj=json_dump(obj=self.to_dict()))
        ret = {}
        for k, v in dumped.items():
            if isinstance(v, dict):
                for a, b in v.items():
                    if isinstance(b, SIMPLE):
                        ret[f"{k}[{a}]"] = b
            elif isinstance(v, SIMPLE):
                ret[k] = v
        return ret

    def dump_request_path(self, path: str, **kwargs) -> str:
        """Format a path string with values from this object.

        Args:
            path (str): Path string to format
            **kwargs: merged in with the dict form of this object

        Returns:
            str: Formatted path string
        """
        return path.format(**combo_dicts(self.to_dict(), kwargs))

    def __str__(self):
        """Pass."""
        props = self._to_str_properties()
        return self._str_join().join(props) if props else super().__str__()

    @classmethod
    def from_dict(cls, data: dict):
        """Pass."""
        fields_known = [x.name for x in dataclasses.fields(cls)]
        extra_attributes = {k: data.pop(k) for k in list(data) if k not in fields_known}
        obj = super().from_dict(data)
        obj.extra_attributes = extra_attributes
        return obj

    @staticmethod
    def _human_key(key):  # pragma: no cover
        """Pass."""
        return key.replace("_", " ").title()

    @staticmethod
    def _str_join() -> str:  # pragma: no cover
        """Pass."""
        return "\n"

    @staticmethod
    def _str_properties() -> List[str]:  # pragma: no cover
        """Pass."""
        return []

    def _to_str_properties(self) -> List[str]:  # pragma: no cover
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
                ret += [f"{key} #{idx + 1}: {item}" for idx, item in enumerate(value)]
                continue
            ret.append(f"{key}: {value}")
        return ret

    @classmethod
    def _get_field_names(cls) -> List[str]:
        """Get a list of field names defined for this dataclass."""
        return [x.name for x in cls._get_fields()]

    @classmethod
    def _get_fields(cls) -> List[dataclasses.Field]:
        """Get a list of fields defined for this dataclass."""
        return dataclasses.fields(cls)

    def __getitem__(self, key):
        """Pass."""
        return self.__dict__[key]

    def __setitem__(self, key, value):
        """Pass."""
        self.__dict__[key] = value

    @classmethod
    def new_from_kwargs(cls, **kwargs) -> "BaseModel":  # pragma: no cover
        """Beta concept for our own deserializer."""
        return cls.new_from_dict(obj=kwargs)

    @classmethod
    def new_from_dict(cls, obj: dict) -> "BaseModel":  # pragma: no cover
        """Beta concept for our own deserializer."""

        def is_missing(obj) -> bool:
            """Pass."""
            return obj == dataclasses.MISSING

        if not isinstance(obj, dict):
            raise ApiError(f"Object to load must be type {dict}, not {type(obj)}")

        cls_args = {}
        pre = f"Attribute error for dataclass {cls}"
        fields = cls._get_fields()
        for field in fields:
            ftype = field.type
            ftype_args = getattr(ftype, "__args__", ())
            ftype_origin = getattr(ftype, "__origin__", None)
            fname = field.name

            required = True

            if not is_missing(field.default_factory):
                default = field.default_factory
                required = False
            if not is_missing(field.default):
                default = field.default
                required = False

            finfo = f"Attribute name={fname!r}, type={ftype}, required={required}"
            if not required:
                finfo += f", default={default!r}"

            if fname not in obj:
                if required:
                    raise ApiAttributeMissingError(
                        f"{pre}\n{finfo}\nMissing required attribute {fname!r}"
                    )

                if not is_missing(field.default_factory):
                    cls_args[fname] = field.default_factory()
                else:
                    cls_args[fname] = field.default
                continue

            if fname in obj:
                value = obj[fname]
                vinfo = f"Supplied type={type(value)}, value={value!r}"
                err = f"{pre}\n{finfo}\n{vinfo}\n"

                if value is None and type(None) in ftype_args:
                    cls_args[fname] = value
                    continue

                if ftype == dict or dict in ftype_args:
                    if not isinstance(value, dict):
                        raise ApiAttributeTypeError(f"{err}Supplied incorrect type for {fname!r}")
                    cls_args[fname] = value
                    continue

                if ftype_origin in [list, List] or list in ftype_args:
                    if value is None:
                        value = []
                    if not isinstance(value, (list, tuple)):
                        raise ApiAttributeTypeError(f"{err}Supplied incorrect type for {fname!r}")

                    if ftype_args:
                        for idx, i in enumerate(value):
                            if not isinstance(i, ftype_args):
                                raise ApiAttributeTypeError(
                                    f"{err}List item at index {idx!r} should be type {ftype_args},"
                                    f" not type {type(i)} for {fname!r}"
                                )

                    cls_args[fname] = value
                    continue

                if ftype == str or str in ftype_args:
                    min_length = field.metadata.get("min_length", 0)
                    if not isinstance(value, str):
                        raise ApiAttributeTypeError(f"{err}Supplied incorrect type for {fname!r}")
                    if min_length and not len(value) >= min_length:
                        raise ApiAttributeTypeError(
                            f"{err}Less than minimum length of {min_length} for {fname!r}"
                        )
                    cls_args[fname] = value
                    continue

                if ftype == bool or bool in ftype_args:
                    cls_args[fname] = coerce_bool(obj=value, errmsg=err)
                    continue

                # int, float, dataclass, etc

        ret = cls(**cls_args)
        extra_attributes = {k: v for k, v in obj.items() if k not in [x.name for x in fields]}
        ret._extra_attributes = extra_attributes
        return ret

    @property
    def extra_attributes(self) -> dict:
        """Extra atttributes supplied during deserialization."""
        return getattr(self, "_extra_attributes", {})

    @extra_attributes.setter
    def extra_attributes(self, value: dict):
        if value:
            LOGGER.warning(f"Extra attributes found in {self}:\n{json_dump(value)}")
        self._extra_attributes = value
