# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
from ..mixins import ChildMixins


class Discover(ChildMixins):
    """Child API model for working with discovery cycles."""

    def lifecycle(self):
        """Get lifecycle metadata.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        return self._lifecycle()

    @property
    def is_running(self):
        """Check if discovery cycle is running.

        Returns:
            :obj:`bool`: if discovery cycle is running
        """
        return not self.lifecycle()["status"] == "done"

    def start(self):
        """Start a discovery cycle if one is not running.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        if not self.is_running:
            self._start()
        return self.lifecycle()

    def stop(self):
        """Stop a discovery cycle if one is running.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        if self.is_running:
            self._stop()
        return self.lifecycle()

    def _lifecycle(self):
        """Direct API method to get discovery cycle metadata.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        path = self.router.discover_lifecycle
        return self.request(method="get", path=path)

    def _start(self):
        """Direct API method to start a discovery cycle."""
        path = self.router.discover_start
        return self.request(method="post", path=path)

    def _stop(self):
        """Direct API method to stop a discovery cycle.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        path = self.router.discover_stop
        return self.request(method="post", path=path)
