# -*- coding: utf-8 -*-
"""API model base classes and mixins."""
import logging

from .. import auth
from ..constants.logs import LOG_LEVEL_API
from ..logs import get_obj_log


class Model:
    """API model base class."""


class ModelMixins(Model):
    """Mixins for API Models."""

    def __init__(self, auth: auth.Model, **kwargs):
        """Mixins for API Models.

        Args:
            auth: object to use for auth and sending API requests
            **kwargs: passed to :meth:`_init`
        """
        log_level = kwargs.get("log_level", LOG_LEVEL_API)
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        """Logger for this object."""
        self.auth = auth
        """:obj:`axonius_api_client.auth.models.Mixins` authentication object."""
        self.http = auth.http
        """:obj:`axonius_api_client.http.Http` client to use to send requests,"""

        self._init(**kwargs)
        auth.check_login()

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


class ChildMixins:
    """Mixins model for API child objects."""

    def __init__(self, parent: Model):
        """Mixins model for API child objects.

        Args:
            parent: parent API model of this child
        """
        self.parent = parent
        self.http = parent.http
        self.auth = parent.auth
        self.LOG = parent.LOG.getChild(self.__class__.__name__)
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
