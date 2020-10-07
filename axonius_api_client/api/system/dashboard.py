# -*- coding: utf-8 -*-
"""API for working with dashboards and discovery lifecycle."""
from ...parsers.system import parse_lifecycle
from ..mixins import ModelMixins
from ..routers import API_VERSION, Router


class Dashboard(ModelMixins):
    """API for working with dashboards and discovery lifecycle.

    Examples:
        * Get discover lifecycle metadata: :meth:`get`
        * See if a lifecycle is currently running: :meth:`is_running`
        * Start a discover lifecycle: :meth:`start`
        * Stop a discover lifecycle: :meth:`stop`

    """

    def get(self) -> dict:
        """Get lifecycle metadata.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.dashboard.get()
            >>> data['next_in_minutes']
            551
            >>> data['is_running']
            False
        """
        return parse_lifecycle(raw=self._get())

    @property
    def is_running(self) -> bool:
        """Check if discovery cycle is running.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.dashboard.is_running
            False
        """
        return self.get()["is_running"]

    def start(self) -> dict:
        """Start a discovery cycle if one is not running.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.dashboard.start()
            >>> data['is_running']
            True
            >>> j(data['phases_pending'])
            [
              "Fetch_Devices",
              "Fetch_Scanners",
              "Clean_Devices",
              "Pre_Correlation",
              "Run_Correlations",
              "Post_Correlation",
              "Run_Queries",
              "Save_Historical"
            ]
            >>> j(data['phases_done'])
            []

        """
        if not self.is_running:
            self._start()
        return self.get()

    def stop(self) -> dict:
        """Stop a discovery cycle if one is running.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.dashboard.start()
            >>> data['is_running']
            True
        """
        if self.is_running:
            self._stop()
        return self.get()

    def _get(self) -> dict:
        """Direct API method to get discovery cycle metadata."""
        path = self.router.lifecycle
        return self.request(method="get", path=path)

    def _start(self) -> str:
        """Direct API method to start a discovery cycle."""
        path = self.router.discover_start
        return self.request(method="post", path=path)

    def _stop(self) -> str:
        """Direct API method to stop a discovery cycle."""
        path = self.router.discover_stop
        return self.request(method="post", path=path)

    @property
    def router(self) -> Router:
        """Router for this API model."""
        return API_VERSION.dashboard
