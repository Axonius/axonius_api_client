# -*- coding: utf-8 -*-
"""Rewritten toolbox."""
from .tool import Tool
from . import error, typer, utility

Error: error.Error = error.Error()
Typer: typer.Typer = typer.Typer()

__all__ = ("error", "typer", "utility", "Error", "Typer", "Tool")
