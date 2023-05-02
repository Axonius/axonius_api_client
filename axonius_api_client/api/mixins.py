# -*- coding: utf-8 -*-
"""API model base classes and mixins."""
import logging
import typing as t

from ..auth import AuthModel
from ..constants.logs import LOG_LEVEL_API
from ..http import Http
from ..logs import get_obj_log


class Model:
    """API model base class."""

    http: t.ClassVar[Http] = None
    """HTTP client to use to send requests."""

    auth: t.ClassVar[AuthModel] = None
    """Authentication object to use to send requests."""

    LOG: t.ClassVar[logging.Logger] = None
    """Logger for this object."""


# noinspection PyUnusedLocal
class ModelMixins(Model):
    """Mixins for API Models."""

    LOG: logging.Logger = None
    """Logger for this object."""

    auth: AuthModel = None
    """Authentication model with bound Http object to use for requests."""

    http: Http = None
    """Http object to use for requests."""

    def __init__(
        self,
        auth: AuthModel,
        log_level: t.Union[int, str] = LOG_LEVEL_API,
        **kwargs,
    ):
        """Mixins for API Models.

        Args:
            auth: object to use for auth and sending API requests
            log_level: logging level to use for this objects logger
            **kwargs: passed to :meth:`_init`
        """
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        self.auth: AuthModel = auth
        self.http: Http = auth.http
        self._init(**kwargs)
        self._init_auth(**kwargs)

    def _init_auth(self, **kwargs):
        """Post init method for subclasses to use for overriding auth setup."""
        self.auth.login()

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        pass

    def __str__(self) -> str:
        """Show info for this model object."""
        cls = self.__class__
        auth = self.auth.__class__.__name__
        url = self.http.url
        return f"{cls.__module__}.{cls.__name__}(auth={auth!r}, url={url!r})"

    def __repr__(self) -> str:
        """Show info for this model object."""
        return self.__str__()


class ChildMixins(Model):
    """Mixins model for API child objects."""

    parent: Model = None
    """Parent API model of this child."""

    LOG: logging.Logger = None
    """Logger for this object."""

    auth: AuthModel = None
    """Authentication model with bound Http object to use for requests."""

    http: Http = None
    """Http object to use for requests."""

    def __init__(self, parent: Model):
        """Mixins model for API child objects.

        Args:
            parent: parent API model of this child
        """
        self.parent: Model = parent
        self.http: Http = parent.http
        self.auth: AuthModel = parent.auth
        self.LOG: logging.Logger = parent.LOG.getChild(self.__class__.__name__)
        self._init(parent=parent)

    def _init(self, parent: Model):
        """Post init method for subclasses to use for extra setup.

        Args:
            parent: parent API model of this child
        """
        pass

    def __str__(self) -> str:
        """Show info for this model object."""
        return f"{self.__class__.__name__} for {self.parent}"

    def __repr__(self) -> str:
        """Show info for this model object."""
        return self.__str__()
