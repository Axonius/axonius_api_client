# -*- coding: utf-8 -*-
"""Base class for tool objects.

"Give me six hours to chop down a tree and I will spend the first four sharpening the axe."
 - Abraham Lincoln
"""
import abc
import functools
import typing as t
from . import utility
import types


class Field:
    """Field container for tool objects."""

    name: str
    """Name of the field."""
    field_type: t.Any
    """Type of the field."""
    fields: "Fields"
    """Fields container for this field."""

    description: t.ClassVar[str] = ""
    """Description from the docstring of the field."""

    default: t.ClassVar[t.Any] = None
    """Default value for this field."""
    default_source: t.ClassVar[str] = "tool class"
    """Source of the default value for this field."""

    def __init__(self, name: str, field_type: t.Type[t.Any], fields: "Fields") -> None:
        """Initialize a field container for tool objects.

        Args:
            name (str):
                Name of the field.
            field_type (t.Type[t.Any]):
                Type of the field.
            fields (Fields):
                Fields container for this field.

        """
        self.name: str = name
        self.field_type: t.Type[t.Any] = field_type
        self.fields: Fields = fields
        self.default: t.ClassVar[t.Any] = getattr(self.fields.TOOL, self.name)
        self.description: t.ClassVar[str] = getattr(self.fields.TOOL, self.name).__doc__

    def is_type(self, value: t.Any) -> bool:
        """Determine if value is an instance of the type for this field.

        Args:
            value (t.Any):
                Value to check.

        Returns:
            bool:
                True if value is an instance of the type for this field.
        """
        return utility.safe_is_type(value=value, expected_types=self.field_type)

    def parse(
        self, obj: t.Optional["Tool"] = None, kwargs: t.Optional[t.Dict[str, t.Any]] = None
    ) -> t.Tuple[t.Any, str]:
        """Parse kwargs for this field.

        Notes:
            To get the value:
            - If the field is in kwargs, and value is the correct type, use it.
            - If the field is in kwargs, and value is not the correct type, :meth:`get_default`
            - If the field is not in kwargs, :meth:`get_default`.

        Args:
            obj (Tool):
                Instance of the tool to get the default value from.
            kwargs:
                Keyword arguments to parse for this field.

        Returns:
            t.Tuple[t.Any, str]:
                Tuple of the value and the source of the value.
        """
        kwargs: t.Dict[str, t.Any] = kwargs if isinstance(kwargs, dict) else {}

        if self.name in kwargs:
            value: t.Any = kwargs[self.name]
            if self.is_type(value=value):
                source: str = "kwargs"
            else:
                # TODO add logging here at debug level
                # requires adding logger object to field. or fields. or to all tool objects.
                # all tool objects need it anyway.
                reason: str = f"kwargs had incorrect type {type(value)}"
                value, source = self.get_default(obj=obj)
                source: str = f"{source} ({reason})"
        else:
            reason: str = f"kwargs did not have"
            value, source = self.get_default(obj=obj)
            source: str = f"{source} ({reason})"
        return value, source

    def get_default(self, obj: t.Optional["Tool"] = None) -> t.Tuple[t.Any, str]:
        """Get the default value for this field.

        Notes:
            To calculate the default value:
            - If obj is a Tool instance, get the default value from the instance.
            - If obj is not a Tool instance, get the default value from the class.

        Args:
            obj (Tool):
                Instance of the tool to get the default value from.

        Returns:
            t.Tuple[t.Any, str]:
                Tuple of the default value and the source of the default value.
        """
        if isinstance(obj, self.fields.TOOL) and hasattr(obj, self.name):
            value: t.Any = getattr(obj, self.name)
            source: str = "tool instance"
        else:
            value: t.Any = self.default
            source: str = self.default_source
        return value, source

    def __str__(self) -> str:
        """Get a string representation of this field."""
        items: t.List[str] = [
            f"name={self.name!r}",
            f"type={self.field_type}",
            f"default={self.default!r}",
            f"description={self.description!r}",
        ]
        items_str: str = ", ".join(items)
        return f"{self.__class__.__name__}({items_str})"

    def __repr__(self) -> str:
        """Get a string describing this object."""
        return self.__str__()


class FieldsArgs:
    """Container to hold parsed field values and sources for tool objects. @DynamicAttrs"""

    FIELDS: "Fields"
    """Fields container for this arguments container."""
    KWARGS: t.Dict[str, t.Any] = None
    """Dictionary of keyword arguments used to parse the field values."""
    SET_ATTRIBUTES: bool = False
    """If True, set the parsed values as attributes on the instance."""
    ONLY_FIELDS: t.List[str] = None
    """List of attributes to set if :attr:`SET_ATTRIBUTES` is True."""
    SKIP_FIELDS: t.List[str] = None
    """List of attributes to skip if :attr:`SET_ATTRIBUTES` is True."""
    OBJ: t.Optional[t.Union["Tool", t.Type["Tool"]]] = None
    """Instance of the tool to get the default values from."""
    PARSED: t.ClassVar[t.Dict[str, t.Any]] = None
    """Dictionary of field names and their values."""
    SOURCES: t.ClassVar[t.Dict[str, str]] = None
    """Dictionary of field names and their sources."""

    def __init__(
        self,
        fields: "Fields",
        kwargs: t.Optional[t.Dict[str, t.Any]] = None,
        obj: t.Optional[t.Union["Tool", t.Type["Tool"]]] = None,
        only_fields: t.Optional[t.List[str]] = None,
        skip_fields: t.Optional[t.List[str]] = None,
        set_attributes: bool = False,
    ) -> None:
        """Parse kwargs for a tool method.

        Notes:
            Loops through the fields the tool in question and:
            - Get value and source for the field from :meth:`Field.parse`.

        Args:
            fields (Fields):
                Fields container for the Tool class.
            kwargs (t.Dict[str, t.Any]):
                Keyword arguments to parse.
            obj (Tool):
                If is a Tool instance, get the default value for fields from this instance instead
                of from the tool class.
            only_fields (t.List[str]):
                If given, only parse the fields listed in only_fields.
            skip_fields (t.List[str]):
                If given, skip parsing the fields listed in skip_fields.
            set_attributes (bool):
                If True and instance is a Tool instance, the parsed values for each field
                are set as attributes on the instance.
        """
        self.KWARGS: t.Dict[str, t.Any] = kwargs if isinstance(kwargs, dict) else {}
        self.FIELDS: Fields = fields
        self.OBJ: t.Optional[t.Union["Tool", t.Type["Tool"]]] = obj
        self.SET_ATTRIBUTES: bool = set_attributes
        self.ONLY_FIELDS: t.List[str] = utility.listify(value=only_fields)
        self.SKIP_FIELDS: t.List[str] = utility.listify(value=skip_fields)
        self.SOURCES, self.PARSED = self.parse()

    def parse(self) -> t.Tuple[t.Dict[str, t.Any], t.Dict[str, str]]:
        """Parse the field values and sources.

        Returns:
            t.Tuple[t.Dict[str, t.Any], t.Dict[str, str]]:
                Tuple of the parsed field values and their sources.
        """
        sources: t.ClassVar[t.Dict[str, str]] = {}
        parsed: t.ClassVar[t.Dict[str, t.Any]] = {}

        for field in self.FIELDS.FIELDS:
            if (self.ONLY_FIELDS and field.name not in self.ONLY_FIELDS) or (
                self.SKIP_FIELDS and field.name in self.SKIP_FIELDS
            ):
                continue
            value, source = field.parse(obj=self.INSTANCE, kwargs=self.KWARGS)
            sources[field.name] = source
            parsed[field.name] = value
            setattr(self, field.name, value)
            if self.SET_ATTRIBUTES is True and isinstance(self.OBJ, self.FIELDS.TOOL):
                setattr(self.OBJ, field.name, value)
        return parsed, sources


class Fields:
    """Container to hold fields for tool objects. @DynamicAttrs"""

    TOOL: t.Union[type, t.Type["Tool"]]
    """Tool class that this container is for."""
    FIELDS: t.ClassVar[t.List[Field]] = None
    """List of fields for the tool class that this container is for."""
    HINTS: t.ClassVar[t.Dict[str, t.Any]] = None
    """Dictionary of hints for the tool class that this container is for."""
    FIELDS_BY_NAME: t.ClassVar[t.Dict[str, Field]] = None
    """Dictionary of fields for the tool class that this container is for."""
    KEY_ARGS: t.ClassVar[str] = "fields_args"
    """Key to store the value sources in return from :meth:`parse`."""

    def __init__(self, tool: t.Union[t.Type["Tool"], "Tool"]) -> None:
        """Initialize a container to hold fields for tool objects.

        Args:
            tool (t.Type[Tool]):
                Tool class that this container is for.
        """
        if isinstance(tool, Tool):
            tool = tool.__class__

        if not utility.safe_is_subclass(tool, Tool):
            raise TypeError(f"tool {tool!r} must be a subclass of {Tool}, not {type(tool)}")

        self.TOOL: t.Type["Tool"] = tool
        self.HINTS: t.ClassVar[t.Dict[str, t.Type[t.Any]]] = tool.UTILITY.get_type_hints(
            value=self.TOOL
        )
        self.FIELDS: t.ClassVar[t.List[Field]] = [
            self._get_field(name=name, field_type=field_type)
            for name, field_type in self.HINTS.items()
        ]
        self.FIELDS_BY_NAME: t.ClassVar[t.Dict[str, Field]] = {
            field.name: field for field in self.FIELDS
        }

    @classmethod
    def get_fields(cls, obj_or_cls: t.Union["Tool", t.Type["Tool"], callable]) -> "Fields":
        """Get the fields from the given object or class.

        Cases:
            - obj_or_cls is a class of type Tool. It should already have a FIELDS attribute
              from the fields_generate decorator. If not, create a new Fields object and
                assign it to the class.
            - obj_or_cls is a method of an instance of a class of type Tool.
              There does not seem to be a way to get to the instance itself from the method,
                so we have to get the class from the method and get the FIELDS attribute from
                the class.
            - obj_or_cls is an instance of a class of type Tool. Get the FIELDS attribute from
                the class.

        Args:
            obj_or_cls (t.Any):
                Object or class to get the fields from.
        """
        inner_cls: t.Optional[t.Type[Tool]] = getattr(obj_or_cls, "__class__", None)

        if isinstance(getattr(obj_or_cls, "FIELDS", None), cls):
            return obj_or_cls.FIELDS

        if isinstance(getattr(inner_cls, "FIELDS", None), cls):
            return inner_cls.FIELDS

        if isinstance(obj_or_cls, Tool):
            tool: t.Type[Tool] = obj_or_cls.__class__
        elif utility.safe_is_subclass(obj_or_cls, Tool):
            tool: t.Type[Tool] = obj_or_cls
        elif utility.safe_is_subclass(inner_cls, Tool):
            tool: t.Type[Tool] = inner_cls
        else:
            raise TypeError(
                f"obj_or_cls {obj_or_cls!r} must be a subclass of {Tool}, not {type(obj_or_cls)}"
            )
        return cls(tool=tool)

    def parse(
        self,
        kwargs: t.Optional[t.Dict[str, t.Any]] = None,
        obj: t.Optional[t.Union["Tool", t.Type["Tool"], callable]] = None,
        only_fields: t.Optional[t.List[str]] = None,
        skip_fields: t.Optional[t.List[str]] = None,
        set_attributes: bool = False,
        reparse: bool = True,
    ) -> FieldsArgs:
        """Get the arguments for the given method.

        Args:
            kwargs (t.Dict[str, t.Any]):
                Keyword arguments to parse.
            obj (Tool):
                If is a Tool instance, get the default value for fields from this instance instead
                of from the tool class.
            only_fields (t.List[str]):
                If given, only parse the fields that listed in only_fields.
            skip_fields (t.List[str]):
                If given, skip parsing the fields that listed in skip_fields.
            set_attributes (bool):
                If True and instance is a Tool instance, the parsed values for each field
                are set as attributes on the instance.
            reparse (bool):
                If True, and the key :attr:`KEY_ARGS` is in kwargs, parse again.

        Returns:
           FieldsArgs:
                Parsed kwargs.
        """
        kwargs: t.Dict[str, t.Any] = kwargs if isinstance(kwargs, dict) else {}
        parsed: t.Optional[FieldsArgs] = kwargs.get(self.KEY_ARGS, None)
        if parsed is not None:
            if not isinstance(parsed, FieldsArgs):
                raise TypeError(
                    f"Value for key {self.KEY_ARGS!r} in kwargs is not a {FieldsArgs} but a"
                    f" {type(parsed)}"
                )

        if not parsed or reparse:
            parsed: FieldsArgs = FieldsArgs(
                fields=self,
                kwargs=kwargs,
                obj=obj,
                set_attributes=set_attributes,
                only_fields=only_fields,
                skip_fields=skip_fields,
            )

        if parsed.FIELDS.TOOL != self.TOOL:
            raise ValueError(
                f"Tools mismatch! Fields are for {self.TOOL} is not for the same "
                f"tool fields container, but {parsed.FIELDS}"
            )

        kwargs[self.KEY_ARGS] = parsed
        return parsed

    def __iter__(self):
        """Iterate over the fields."""
        return iter(self.FIELDS)

    def _get_field(self, name: str, field_type: t.Any) -> Field:
        """Build a Field object from a name and type."""
        field: Field = Field(name=name, field_type=field_type, fields=self)
        setattr(self, name, field)
        return field

    def __str__(self) -> str:
        """Get a string representation of the fields."""
        items: t.List[str] = [
            f"tool={self.TOOL.UTILITY.safe_cls_str(self.TOOL)!r}",
            f"field_count={len(self.FIELDS)}",
        ]
        items_str: str = ", ".join(items)
        header: str = f"{self.__class__.__name__}({items_str})"
        fields: t.List[str] = [str(field) for field in self.FIELDS]
        return "\n".join([header, *fields])

    def __repr__(self) -> str:
        """Get a string describing this object."""
        return self.__str__()


def fields_generate(
    cls: t.Optional[t.Type["Tool"]] = None,
    /,
) -> t.Union[t.Callable[[t.Type["Tool"]], t.Type["Tool"]], t.Type["Tool"]]:
    """Decorator to generate fields and add them to the class.

    Args:

        cls (t.Type[Tool]):
            Tool class to generate fields for.

    Returns:
        t.Union[t.Callable[[t.Type[Tool]], t.Type[Tool]], t.Type[Tool]]:
            If cls is None, return the decorator, otherwise return the class.
    """

    def wrapper(wrap_cls: t.Type["Tool"]) -> t.Type["Tool"]:
        wrap_cls.FIELDS = Fields(tool=wrap_cls)
        return wrap_cls

    # if cls is None, this is being used as a decorator
    if cls is None:
        # return the decorator
        return wrapper

    return wrapper(cls)


def fields_parse(
    method: t.Optional[callable] = None,
    set_attributes: bool = False,
    only_fields: t.Optional[t.List[str]] = None,
    skip_fields: t.Optional[t.List[str]] = None,
    reparse: bool = False,
) -> callable:
    """Decorator to generate arguments for the given method.

    Args:
        method (callable):
            Method to generate arguments for and add to kwargs as :attr:`Fields.KEY_ARGS`.
        set_attributes (bool):
            If True, the parsed values for each field are set as attributes on the instance.
        only_fields (t.List[str]):
            If given, only parse the fields that listed in only_fields.
        skip_fields (t.List[str]):
            If given, skip parsing the fields that listed in skip_fields.
        reparse (bool):
            If True, and the key :attr:`Fields.KEY_ARGS` is in kwargs, parse again.

    """

    @functools.wraps(method)
    def wrapper(obj_or_cls, *args, **kwargs) -> callable:
        """Wrapper for the decorator."""
        fields: Fields = Fields.get_fields(obj_or_cls)
        fields_args: FieldsArgs = fields.parse(
            kwargs=kwargs,
            obj=obj_or_cls,
            set_attributes=set_attributes,
            reparse=reparse,
            only_fields=only_fields,
            skip_fields=skip_fields,
        )
        kwargs[fields.KEY_ARGS] = fields_args
        return method(obj_or_cls, *args, **kwargs)

    if method is None:
        # return the decorator
        return wrapper

    return wrapper


class Tool(metaclass=abc.ABCMeta):
    """Base class for tool objects."""

    FIELDS: t.ClassVar[Fields]
    """The fields from when this object was initialized."""

    UTILITY: t.ClassVar[types.ModuleType] = utility
    """The utility module."""

    @fields_parse()
    def use(self, *args, **kwargs) -> t.Any:
        """Entry point for tool objects.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Any: Result of the tool.
        """
        return self._use(*args, **kwargs)

    @classmethod
    @abc.abstractmethod
    def _use(cls, *args, fields_args: FieldsArgs, **kwargs) -> t.Any:
        """Entry point for tool objects.

        Args:
            *args: Positional arguments.
            fields_args (FieldsArgs): Parsed keyword arguments.
            **kwargs: Keyword arguments.

        Returns:
            Any: Result of the tool.
        """
        raise NotImplementedError

    @classmethod
    @fields_parse(reparse=True)
    def new(cls, **kwargs) -> "Tool":
        """Create a new instance of this tool.

        Args:
            **kwargs: Can override any of the class attribute default values.

        Returns:
            Tool: New instance of this tool.
        """
        return cls(**kwargs)

    @fields_parse(set_attributes=True)
    def __init__(self, *args, **kwargs) -> None:
        """Initialize a new instance of a tool object.

        Args:
            **kwargs: Can override any of the class attribute default values.
        """

    @fields_parse()
    def __call__(self, *args, **kwargs) -> t.Any:
        """Call the process method for this tool object.

        Args:
            **kwargs: Passed to :method:`use`.

        Returns:
            Any: Result of :method:`use:.
        """
        return self.use(*args, **kwargs)

    def __str__(self) -> str:
        """Get a string describing the fields for this tool."""
        return f"{self.FIELDS}"

    def __repr__(self) -> str:
        """Get a string describing the fields for this tool."""
        return self.__str__()
