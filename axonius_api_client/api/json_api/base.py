# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import logging
import typing as t
import warnings
from dataclasses import Field

import dataclasses_json
import marshmallow
import marshmallow_jsonapi
import marshmallow_jsonapi.fields as mm_fields

from ...constants.ctypes import SimpleLike
from ...constants.general import RERAISE
from ...exceptions import (
    ApiAttributeMissingError,
    ApiAttributeTypeError,
    ApiError,
    ExtraAttributeWarning,
    SchemaError,
)
from ...http import Http
from ...logs import get_obj_log
from ...setup_env import get_env_extra_warn
from ...tools import coerce_bool, combo_dicts, json_dump, json_load, listify, strip_right

LOGGER = logging.getLogger(__name__)
WARN_TRACKER: t.Dict[t.Type["BaseModel"], t.Set[str]] = {}


def get_warn_help(value: t.Type[Warning]) -> t.List[str]:
    """Pass."""
    name = value.__name__
    ret = [
        "",
        "To silence these warnings please upgrade to latest API client.",
        "If there is not a newer version available yet, you can disable these warnings using:",
        "- from command line, use OS environment variable AX_EXTRA_WARN='no'",
        "- or from python, use warnings module:",
        "import warnings, axonius_api_client",
        f'warnings.filterwarnings(action="ignore", category=axonius_api_client.exceptions.{name})',
        "",
    ]
    return ret


class BaseCommon:
    """Common methods for all schema and model classes."""

    @property
    def logger(self) -> logging.Logger:
        """Pass."""
        return get_obj_log(self)

    # noinspection PyUnusedLocal
    @classmethod
    def _post_load_attrs(
        cls,
        data: t.Union["BaseModel", t.List["BaseModel"]],
        http: t.Optional[Http] = None,
        **kwargs,
    ):
        """Add HTTP object as an attribute to any loaded model.

        Args:
            data (t.Union["BaseModel", t.List["BaseModel"]]): Loaded model(s)
            http (Optional[Http], optional): HTTP object to set on loaded model(s)
            **kwargs: n/a
        """
        for item in listify(data):
            # noinspection PyBroadException
            try:
                item.HTTP = http
            except Exception:  # pragma: no cover
                pass

    @classmethod
    def _load_schema(
        cls,
        schema: marshmallow.Schema,
        data: t.Union[dict, t.List[dict]],
        **kwargs,
    ) -> t.Union["BaseModel", t.List["BaseModel"]]:
        """Load data using a marshmallow schema.

        Args:
            schema (marshmallow.Schema): Schema to use to load `data`
            data (t.Union[dict, t.List[dict]]): Data to load
            **kwargs: passed to :meth:`_post_load_attrs`

        Returns:
            t.Union["BaseModel", t.List["BaseModel"]]: Loaded model(s)

        Raises:
            JsonApiError: when "type" of JSON API data does not match Meta._type of schema
            ValidationError: when marshmallow schema validation fails
        """
        kwargs["reraise"] = kwargs.get("reraise", RERAISE)
        try:
            loaded = schema.load(data, unknown=marshmallow.INCLUDE)
        except Exception as exc:
            if kwargs["reraise"]:
                raise
            raise SchemaError(schema=schema, exc=exc, obj=cls, data=data)

        cls._post_load_attrs(data=loaded, **kwargs)
        return loaded

    @staticmethod
    def _get_aname(value: str) -> str:
        """Pass."""
        return strip_right(obj=str(value or ""), fix="_adapter")

    @staticmethod
    def _prepend_sort(value: str, descending: bool = False):
        """Pass."""
        if isinstance(value, str):
            if value.startswith("-"):
                value = value[1:]
            if descending:
                value = f"-{value}"
        return value


class BaseSchema(BaseCommon, marshmallow.Schema):
    """Schema base class for validating non JSON API data."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the BaseModel or type that data should be loaded into.

        Returns:
            t.Union["BaseModel", type]: BaseModel to load data into, or callable (i.e. dict)

        Raises:
            NotImplementedError: Sub classes MUST define this.
        """
        raise NotImplementedError()

    @classmethod
    def load_response(
        cls, data: t.Union[dict, list, tuple], **kwargs
    ) -> t.Union["BaseModel", t.List["BaseModel"]]:
        """Load data using this schema.

        Args:
            data (t.Union[dict, list, tuple]): Response data to load using this schema
            **kwargs: passed to :meth:`BaseCommon._load_schema`

        Returns:
            t.Union["BaseModel", t.List["BaseModel"]]: Loaded model(s)

        Raises:
            SchemaError: if data is not a dict or list
        """
        many = isinstance(data, (list, tuple))
        schema = cls(many=many, unknown=marshmallow.INCLUDE)

        if not isinstance(data, (dict, list, tuple)):
            exc = ApiError(
                f"Data to load must be a dictionary or list, not a {type(data).__name__}"
            )
            raise SchemaError(schema=schema, exc=exc, data=data, obj=cls)

        return cls._load_schema(**combo_dicts(kwargs, schema=schema, data=data))

    # noinspection PyUnusedLocal
    @marshmallow.post_load
    def post_load_process(self, data: dict, **kwargs) -> t.Union[dict, "BaseModel"]:
        """Marshmallow post_load hook to load validated data into a model class.

        Args:
            data (dict): validated data to load
            **kwargs: n/a

        Returns:
            t.Union[dict, "BaseModel"]: Loaded data model
        """
        model_cls = self.get_model_cls()
        data = data or {}

        if not dataclasses.is_dataclass(model_cls):
            return model_cls(**data) if callable(model_cls) else data
        return model_cls.from_dict(data)

    @classmethod
    def get_model_fields(cls) -> t.List[Field]:
        """Get the fields of the model class that this schema loads into."""
        # noinspection PyProtectedMember
        return cls.get_model_cls()._get_fields()


class BaseSchemaJson(BaseSchema, marshmallow_jsonapi.Schema):
    """Schema base class for validating JSON API data."""

    id = mm_fields.Str()
    document_meta = mm_fields.DocumentMeta()

    class Meta:
        """Pass."""

        type_ = "base_schema"

    @classmethod
    def load_response(cls, data: dict, **kwargs) -> t.Union["BaseModel", t.List["BaseModel"]]:
        """Load data using this JSON API schema.

        Args:
            data (dict): Response data to load using this schema
            **kwargs: passed to :meth:`BaseCommon._load_schema`

        Returns:
            t.Union["BaseModel", t.List["BaseModel"]]: Loaded model(s)

        Raises:
            SchemaError: if data is not a dict
        """
        if not isinstance(data, dict):
            if isinstance(data, list):
                # Fix for endpoints that do not return JSON API structure
                data = {"data": [{"attributes": x, "type": cls.Meta.type_} for x in data]}
            else:
                exc = ApiError(f"Data to load must be a dictionary, not a {type(data).__name__}")
                raise SchemaError(schema=cls, exc=exc, data=data, obj=cls)
        inner_data: t.Any = data.get("data")
        many: bool = isinstance(inner_data, (list, tuple))
        schema = cls(many=many, unknown=marshmallow.INCLUDE)
        return cls._load_schema(**combo_dicts(kwargs, schema=schema, data=data))

    @classmethod
    def validate_attr_excludes(cls) -> t.List[str]:
        """Pass."""
        return ["document_meta"]

    @classmethod
    def validate_attrs(cls) -> dict:
        """Pass."""
        excludes = cls.validate_attr_excludes()
        return {k: v for k, v in cls._declared_fields.items() if k not in excludes}

    @classmethod
    def validate_attr(
        cls,
        value: str,
        exc_cls: t.Type[Exception] = marshmallow.ValidationError,
    ) -> str:
        """Pass."""
        check = value
        if check.startswith("-"):
            check = value[1:]

        attrs = cls.validate_attrs()
        if check in attrs:
            return value

        valids = "\n  " + "\n  ".join(list(attrs))
        raise exc_cls(f"Invalid attribute {value!r}, valids: {valids}")


# noinspection PyDataclass
class BaseModel(dataclasses_json.DataClassJsonMixin, BaseCommon):
    """Model base class for holding data."""

    HTTP: t.ClassVar[Http] = None
    """HTTP client to use for requests."""

    @classmethod
    def get_request_if_not_request(
        cls,
        http: Http,
        request_obj: t.Optional["BaseModel"] = None,
        *args,
        **kwargs,
    ) -> "BaseModel":
        """If request is not of this type, build one using args and kwargs."""
        # noinspection PyArgumentList
        data = request_obj if isinstance(request_obj, cls) else cls(*args, **kwargs)
        cls._post_load_attrs(data, http=http)
        return data

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the BaseSchema that should be used to validate the data for this model.

        Returns:
            t.Optional[Type[BaseSchema]]: BaseSchema to use to verify data

        Raises:
            NotImplementedError: Sub classes MUST define this.
        """
        raise NotImplementedError()

    @classmethod
    def _get_attr_value(cls, value: t.Union[str, dict, "BaseModel"], attr: str) -> str:
        """Pass."""
        if isinstance(value, str):
            if not value.strip():
                raise ApiError(
                    f"Value provided for attribute {attr!r} as str can not be empty: {value!r}"
                )
            return value

        if isinstance(value, dict):
            if attr not in value:
                raise ApiError(f"Dict provided does not have attribute {attr!r}: {value!r}")

            ret = value[attr]
            if not (isinstance(ret, str) and ret.strip()):
                raise ApiError(
                    f"Dict provided has an empty or non string attribute {attr!r}: {ret!r}"
                )
            return ret

        if isinstance(value, cls):
            if not hasattr(value, attr):
                raise ApiError(f"{cls} provided does not have attribute {attr!r}: {value!r}")

            ret = getattr(value, attr)
            if not (isinstance(ret, str) and ret.strip()):
                raise ApiError(
                    f"{cls} provided has an empty or non string attribute {attr!r}: {ret!r}"
                )

            return ret
        raise ApiError(
            f"Unable to get attribute {attr}!"
            f" Invalid value type {type(value)} {value!r}, must be str, dict, or {cls}"
        )

    @classmethod
    def load_response(
        cls, data: t.Union[dict, list, tuple], schema_cls: t.Optional[BaseSchema] = None, **kwargs
    ) -> t.Union["BaseModel", t.List["BaseModel"]]:
        """Load data using this JSON API schema.

        Args:
            data (t.Union[dict, list, tuple]): Response data to load using this schema
            schema_cls (Optional[BaseSchema], optional): Schema class to use to validate data
                will fall back to :meth:`get_schema_cls` or dataclasses_json automatic schema
            **kwargs: passed to :meth:`BaseCommon._load_schema`

        Returns:
            t.Union["BaseModel", t.List["BaseModel"]]: Loaded model(s)

        Raises:
            SchemaError: if data is not a dict or list
        """
        schema_cls = schema_cls or cls.get_schema_cls() or cls.schema
        if callable(getattr(schema_cls, "load_response", None)):
            return schema_cls.load_response(data=data, **kwargs)

        many = isinstance(data, (list, tuple))
        schema = schema_cls(many=many, unknown=marshmallow.INCLUDE)
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

    def dump_request(self, schema_cls: t.Optional[BaseSchema] = None, **kwargs) -> dict:
        """Convert this model into a dictionary for sending as a request.

        This does a bunch of fancy foot work to re-validate the data using marshmallow schema
        if possible.

        Args:
            schema_cls (Optional[BaseSchema], optional): Schema class to use to validate data
                will fall back to :meth:`get_schema_cls` or dataclasses_json automatic schema
            **kwargs: passed to :meth:`BaseCommon._load_schema` as part of reloading the data
                to validate it

        Returns:
            dict: serialized dict of this model
        """
        schema_cls = schema_cls or self.get_schema_cls() or self.schema
        schema = schema_cls()
        dumped = self.to_dict()

        if isinstance(schema, BaseSchemaJson):
            if "data" not in dumped:
                dumped = {"data": {"attributes": dumped, "type": schema.Meta.type_}}
            if "type" not in dumped["data"]:
                dumped = {"data": {"attributes": dumped, "type": schema.Meta.type_}}

        loaded = self._load_schema(**combo_dicts(kwargs, schema=schema, data=dumped))
        re_dumped = schema.dump(loaded)
        re_dumped.pop("document_meta", None)
        return re_dumped

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
            if v is None:
                continue

            if isinstance(v, dict):
                for a, b in v.items():
                    if isinstance(b, SimpleLike):
                        ret[f"{k}[{a}]"] = b
            elif isinstance(v, SimpleLike):
                ret[k] = v
            elif isinstance(v, (list, tuple)) and v and all([isinstance(x, SimpleLike) for x in v]):
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

    def __repr__(self):
        """Pass."""
        return self.__str__()

    @classmethod
    def from_dict(cls, data: dict, **kwargs):
        """Pass."""
        fields_known: t.Dict[str, Field] = cls._get_fields_dict()
        extra_attributes = {k: data.pop(k) for k in list(data) if k not in fields_known}
        obj = super().from_dict(data, **kwargs)
        if extra_attributes:
            if hasattr(obj, "_extra_attributes"):
                # noinspection PyProtectedMember
                obj._extra_attributes.update(extra_attributes)
            else:
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
    def _str_properties() -> t.List[str]:  # pragma: no cover
        """Pass."""
        return []

    def _to_str_properties(self) -> t.List[str]:  # pragma: no cover
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
    def _get_field_names(cls) -> t.List[str]:
        """Get a list of field names defined for this dataclass."""
        return [x.name for x in cls._get_fields()]

    @classmethod
    def _get_fields(cls) -> t.Tuple[Field, ...]:
        """Get a list of fields defined for this dataclass."""
        return dataclasses.fields(cls)

    @classmethod
    def _get_fields_dict(cls) -> t.Dict[str, Field]:
        """Get a list of fields defined for this dataclass."""
        return {x.name: x for x in dataclasses.fields(cls)}

    @classmethod
    def remove_unknown_arguments(
        cls,
        remove_unknown_arguments: bool = True,
        warn_unknown_arguments: bool = True,
        kwargs: t.Optional[dict] = None,
    ) -> t.Tuple[dict, dict]:
        """Remove unknown arguments from the kwargs.

        Args:
            remove_unknown_arguments (bool, optional): Whether to remove unknown arguments
                from the kwargs. Defaults to True.
            warn_unknown_arguments (bool, optional): Whether to warn about unknown arguments.
                Defaults to True.
            kwargs (t.Optional[dict], optional): The kwargs to remove unknown arguments from.
                Defaults to None.

        Returns:
            t.Tuple[dict, dict]: The kwargs with unknown arguments removed, and the unknown
                arguments.
        """
        if not isinstance(kwargs, dict):
            kwargs = {}

        known_arguments: t.Dict[str, dataclasses.Field] = cls._get_fields_dict()
        unknown_arguments: t.Dict[str, t.Any] = {
            k: v for k, v in kwargs.items() if k not in known_arguments
        }
        if unknown_arguments:
            msg = f"Unknown arguments passed to {cls}: {unknown_arguments}"
            LOGGER.warning(msg)
            if warn_unknown_arguments and get_env_extra_warn():
                warnings.warn(message=msg, category=ExtraAttributeWarning)
            if remove_unknown_arguments:
                for k in unknown_arguments:
                    kwargs.pop(k)
        return kwargs, unknown_arguments

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

        def is_missing(check) -> bool:
            """Pass."""
            return check == dataclasses.MISSING

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

            default_text = ""
            if not is_missing(field.default_factory):
                default = field.default_factory
                required = False
                default_text = f", default={default}"
            if not is_missing(field.default):
                default = field.default
                required = False
                default_text = f", default={default}"

            finfo = f"Attribute name={fname!r}, type={ftype}, required={required}{default_text}"

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

                if ftype_origin in [list, t.List] or list in ftype_args:
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

        # noinspection PyArgumentList
        ret = cls(**cls_args)
        extra_attributes = {k: v for k, v in obj.items() if k not in [x.name for x in fields]}
        ret._extra_attributes = extra_attributes
        return ret

    @property
    def extra_attributes(self) -> dict:
        """Extra attributes supplied during deserialization."""
        return getattr(self, "_extra_attributes", {})

    @extra_attributes.setter
    def extra_attributes(self, value: dict):
        if isinstance(value, dict) and value:
            schema = self.get_schema_cls()
            if self.__class__ not in WARN_TRACKER:
                WARN_TRACKER[self.__class__] = set()
            unknown = list(value)
            unknown_str = ", ".join(unknown)
            if unknown_str not in WARN_TRACKER[self.__class__]:
                WARN_TRACKER[self.__class__].add(unknown_str)
                stype = getattr(getattr(schema, "Meta", None), "type_", None)
                this_cls = self.__class__
                warn_help = get_warn_help(ExtraAttributeWarning)
                msgs = [
                    f"Extra attributes found in dataclass model {this_cls}",
                    f"Associated schema {schema} (JSON API type: {stype!r})",
                    *warn_help,
                    "Extra attributes found:",
                    f"{json_dump(value)}",
                ]
                msg = "\n".join(msgs)
                LOGGER.warning(msg)
                if get_env_extra_warn():
                    warnings.warn(message=msg, category=ExtraAttributeWarning)

        # noinspection PyAttributeOutsideInit
        self._extra_attributes = value
