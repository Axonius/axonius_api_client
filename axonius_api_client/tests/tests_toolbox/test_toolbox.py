# -*- coding: utf-8 -*-
"""Test suite."""
import typing as t

import pytest
from axonius_api_client.toolbox import Tool


class TestToolbox:
    class ExampleTool(Tool):
        @classmethod
        def use(cls, *args, **kwargs) -> t.Any:
            return "Processed"

    def test_process(self):
        with pytest.raises(NotImplementedError):
            Tool.use()

        assert self.ExampleTool.use() == "Processed"

    def test_call(self):
        example_toolbox = self.ExampleTool()
        assert str(example_toolbox).endswith("ExampleToolbox()")
        assert example_toolbox() == "Processed"


class TestToolboxArgs:
    class ExampleTool(Tool):
        include_details: bool = True

        @classmethod
        def use(cls, *args, **kwargs) -> t.Any:
            parsed_kwargs = cls._parse_kwargs(**kwargs)
            return f"Processed kwargs: {parsed_kwargs}"

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            ({}, "Processed kwargs: {'include_details': True}"),
            ({"nonexistent_arg": 42}, "Processed kwargs: {'include_details': True}"),
            ({"include_details": False}, "Processed kwargs: {'include_details': False}"),
            ({"include_details": 8}, "Processed kwargs: {'include_details': True}"),
        ],
    )
    def test_process(self, kwargs, expected):
        result = self.ExampleTool.use(**kwargs)
        assert result == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            ({}, {"include_details": True}),
            ({"include_details": False}, {"include_details": False}),
            ({"include_details": 42}, {"include_details": True}),
            ({"nonexistent_arg": 42}, {"include_details": True}),
            ({"include_details": False, "nonexistent_arg": 42}, {"include_details": False}),
        ],
    )
    def test_parse_kwargs(self, kwargs, expected):
        result = self.ExampleTool._parse_kwargs(**kwargs)
        assert result == expected

    def test_call(self):
        example_toolbox = self.ExampleTool()
        assert str(example_toolbox).endswith("ExampleToolbox(include_details=True)")
        assert example_toolbox() == "Processed kwargs: {'include_details': True}"

    def test_init_defaults(self):
        example_toolbox = self.ExampleTool(include_details=False)
        assert str(example_toolbox).endswith("ExampleToolbox(include_details=False)")

    def test_call_args(self):
        example_toolbox = self.ExampleTool()
        assert not str(example_toolbox)
        assert example_toolbox() == "Processed"
