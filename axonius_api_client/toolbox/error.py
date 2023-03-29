# -*- coding: utf-8 -*-
"""Tool for handling errors.

"Success is stumbling from failure to failure with no loss of enthusiasm."
 - Winston Churchill
"""
import logging
import sys
import typing as t

from .tool import Tool, Fields, Field

LOG: logging.Logger = logging.getLogger(__name__)


class Error(Tool):
    """Tool for handling errors."""

    supplied: t.Any = None
    """Value to return instead of raising error if return_supplied is True."""
    fallback: t.Any = None
    """Value to return instead of raising error if return_fallback is True."""
    return_supplied: bool = False
    """If True, on errors return value in supplied instead of raising an exception.
    Overrides return_fallback."""
    return_fallback: bool = False
    """If True, on errors return value in fallback instead of raising an exception."""
    raise_original: bool = False
    """If True, raise the original exception. Overrides everything."""
    log_fallback: bool = True
    """If True and return_fallback is True, log exception at log_level."""
    log_stack: bool = True
    """If True and return_fallback is True and log_fallback is True, include stack."""
    log_level: str = "debug"
    """Level to use on log when log_fallback=True."""
    logger: logging.Logger = LOG
    """Logger to use when log_fallback=True."""

    @classmethod
    def _use(cls, error: Exception, **kwargs) -> t.Any:
        """Determine if error should be raised or value returned.

        Args:
            error (Exception):
                Exception to raise if return_fallback is False.
            **kwargs:
                supplied (t.Any):
                    Value to return instead of raising error if return_supplied is True.
                fallback (t.Any):
                    Value to return instead of raising error if return_fallback is True.
                return_supplied (bool):
                    If True, on errors return value in supplied instead of raising an exception.
                    Overrides return_fallback.
                return_fallback (bool):
                    If True, on errors return value in fallback instead of raising an exception.
                raise_original (bool):
                    If True, raise the original exception. Overrides everything.
                log_fallback (bool):
                    If True and return_fallback is True, log exception at log_level.
                log_stack (bool):
                    If True and return_fallback is True and log_fallback is True, include stack.
                log_level (str):
                    Level to use on log when log_fallback=True.
                logger (logging.Logger):
                    Logger to use when log_fallback=True.
        """
        from . import Typer

        fields: Fields = cls.get_fields(**kwargs)
        flags: t.List[Field] = [fields.return_fallback, fields.return_supplied]
        raise_original: bool = fields.raise_original.value
        return_fallback: bool = fields.return_fallback.value
        return_supplied: bool = fields.return_supplied.value
        log_fallback: bool = fields.log_fallback.value
        log_stack: bool = fields.log_stack.value
        log_level: str = fields.log_level.value
        logger: logging.Logger = fields.logger.value
        supplied: t.Any = fields.supplied.value
        fallback: t.Any = fields.fallback.value

        if raise_original and any(sys.exc_info()):
            raise

        if return_fallback or return_supplied:
            if log_fallback:
                flag_str: str = ",".join([f"{x.name}={x.value}" for x in flags])
                log_method: callable = cls.UTILITY.safe_getattr(
                    attr=log_level.strip().lower(),
                    value=logger,
                    fallback=cls.logger,
                    final=LOG.error,
                )
                log_method(
                    f"Ignoring {Typer(error)} error due to {flag_str}: {error}",
                    exc_info=log_stack,
                )

            if return_supplied:
                return supplied

            return fallback

        raise error
