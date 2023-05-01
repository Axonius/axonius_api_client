# -*- coding: utf-8 -*-
"""API for working with adapters."""
import datetime
import pathlib
import typing as t

from cachetools import TTLCache, cached

from ...constants.ctypes import PatternLikeListy
from ...exceptions import ApiError, NotFoundError  # , StopFetch
from ...parsers.config import config_build, config_unchanged, config_unknown
from ...parsers.tables import tablize_adapters
from ...tools import path_read
from ..api_endpoints import ApiEndpoints
from ..json_api.adapters import (
    Adapter,
    AdapterFetchHistoryRequest,
    AdapterSettings,
    AdaptersList,
    CnxLabels,
    AdapterFetchHistory,
    AdapterFetchHistoryFilters,
)
from ..json_api.paging_state import PagingState
from ..json_api.system_settings import SystemSettings
from ..json_api.time_range import UnitTypes
from ..mixins import ModelMixins

HIST_MOD = AdapterFetchHistory
HIST_GEN = t.Generator[HIST_MOD, None, None]
HIST_LIST = t.List[HIST_MOD]

CACHE_HISTORY_FILTERS: TTLCache = TTLCache(maxsize=4096, ttl=60)
CACHE_GET_BASIC: TTLCache = TTLCache(maxsize=1024, ttl=60)


class Adapters(ModelMixins):
    """API model for working with adapters.

    Examples:
        Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

        * Get metadata of all adapters: :meth:`get`
        * Get an adapter by name: :meth:`get_by_name`
        * Get the advanced settings for an adapter: :meth:`config_get`
        * Update the advanced settings for an adapter: :meth:`config_update`
        * Upload a file to an adapter: :meth:`file_upload`
        * Work with adapter connections :obj:`axonius_api_client.api.adapters.cnx.Cnx`

    Notes:
        All methods use the Core instance by default, but you can work with another instance by
        passing the name of the instance to ``node``.

        Supplying unknown keys/values for configurations will throw an error showing the
        valid keys/values.
    """

    def get(self, get_clients: bool = False) -> t.List[dict]:
        """Get all adapters on all nodes.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Get all adapters

            >>> adapters = client.adapters.get()

            Get details of each adapter

            >>> for adapter in adapters:
            ...     print(adapter["name"])  # name of adapter
            ...     print(adapter["node_name"])  # name of node adapter is running on

        Args:
            get_clients (bool, optional): Include the connections and schemas in the response

        Returns:
            t.List[dict]: list of adapter metadata

        """
        return [
            adapter_node.to_dict_old()
            for adapter in self._get(get_clients=get_clients)
            for adapter_node in adapter.adapter_nodes
        ]

    def get_by_name_basic(self, value: str) -> dict:
        """Get an adapters basic metadata (including display title) by name.

        Args:
            value (str): short name of adapter (i.e. ``aws``)

        Returns:
            dict: adapter basic metadata
        """
        data = self.get_basic()
        return data.find_by_name(value=value)

    def get_by_name(
        self, name: str, node: t.Optional[str] = None, get_clients: bool = False
    ) -> dict:
        """Get an adapter by name on a single node.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Get an adapter by name

            >>> adapter = client.adapters.get_by_name(name="aws")

            Get details of adapter

            >>> adapter['status']               # overall adapter status
            'success'
            >>> adapter['cnx_count_total']      # total connection count
            1
            >>> adapter['cnx_count_broken']     # broken connection count
            0
            >>> adapter['cnx_count_working']    # working connection count
            1

            Get details of each connection of the adapter

            >>> for cnx in adapter["cnx"]:
            ...     print(cnx["working"])  # bool if connection is working or not
            ...     print(cnx["error"])  # error from last fetch attempt
            ...     print(cnx["config"])  # configuration of connection
            ...     print(cnx["id"])  # ID of connection
            ...     print(cnx["uuid"])  # UUID of connection

        Args:
            name (str): name of adapter to get
            node (Optional[str], optional): name of node to get adapter from
            get_clients (bool, optional): Include the connections and schemas in the response

        Raises:
            NotFoundError: when no node found or when no adapter found on node

        Returns:
            dict: adapter metadata
        """
        node_meta = self.instances.get_by_name_id_core(value=node)
        adapters = self.get(get_clients=get_clients)

        node_name = node_meta["name"]
        adapters = [adapter for adapter in adapters if adapter["node_name"] == node_name]

        keys = ["name", "name_raw", "name_plugin"]
        for adapter in adapters:
            if any([adapter[k].lower() == name.lower() for k in keys]):
                adapter["node_meta"] = node_meta
                return adapter

        err = f"No adapter named {name!r} found on instance {node_name!r}"
        raise NotFoundError(tablize_adapters(adapters=adapters, err=err))

    @cached(cache=CACHE_GET_BASIC)
    def get_basic_cached(self) -> AdaptersList:
        """Get basic adapter data cached."""
        return self.get_basic()

    def get_basic(self) -> AdaptersList:
        """Get basic adapter data."""
        return self._get_basic()

    @cached(cache=CACHE_HISTORY_FILTERS)
    def get_fetch_history_filters(self) -> AdapterFetchHistoryFilters:
        """Get filter values for use in adapters history."""
        return self._get_fetch_history_filters()

    def get_fetch_history(self, generator: bool = False, **kwargs) -> t.Union[HIST_GEN, HIST_LIST]:
        """Get adapter fetch history.

        Args:
            generator (bool, optional): Return a generator or a list
            **kwargs: passed to :meth:`get_fetch_history_generator`

        Returns:
            t.Union[HIST_GEN, HIST_LIST]: t.Generator or list of history event models
        """
        gen = self.get_fetch_history_generator(**kwargs)
        return gen if generator else list(gen)

    def get_fetch_history_generator(
        self,
        adapters: t.Optional[PatternLikeListy] = None,
        connection_labels: t.Optional[PatternLikeListy] = None,
        clients: t.Optional[PatternLikeListy] = None,
        instances: t.Optional[PatternLikeListy] = None,
        statuses: t.Optional[PatternLikeListy] = None,
        discoveries: t.Optional[PatternLikeListy] = None,
        exclude_realtime: bool = False,
        relative_unit_type: UnitTypes = UnitTypes.get_default(),
        relative_unit_count: t.Optional[int] = None,
        absolute_date_start: t.Optional[datetime.datetime] = None,
        absolute_date_end: t.Optional[datetime.datetime] = None,
        sort_attribute: t.Optional[str] = None,
        sort_descending: bool = False,
        search: t.Optional[str] = None,
        filter: t.Optional[str] = None,
        page_sleep: int = PagingState.page_sleep,
        page_size: int = PagingState.page_size,
        row_start: int = PagingState.row_start,
        row_stop: t.Optional[int] = PagingState.row_stop,
        log_level: t.Union[int, str] = PagingState.log_level,
        history_filters: t.Optional[AdapterFetchHistoryFilters] = None,
        request_obj: t.Optional[AdapterFetchHistoryRequest] = None,
    ) -> HIST_GEN:
        """Get adapter fetch history.

        Notes:
            Use ~ prefix for regex in adapters, connection_labels, clients, instances, statuses

        Args:
            adapters (t.Optional[PatternLikeListy], optional): Filter for records with matching
                adapters
            connection_labels (t.Optional[PatternLikeListy], optional): Filter for records with
                connection labels
            clients (t.Optional[PatternLikeListy], optional): Filter for records with matching
                client ids
            instances (t.Optional[PatternLikeListy], optional): Filter for records with matching
                instances
            statuses (t.Optional[PatternLikeListy], optional): Filter for records with matching
                statuses
            discoveries (t.Optional[PatternLikeListy], optional): Filter for records with matching
                discovery IDs
            exclude_realtime (bool, optional): Exclude records for realtime adapters
            relative_unit_type (UnitTypes, optional): Type of unit to use when supplying
                relative_unit_count
            relative_unit_count (Optional[int], optional): Filter records for the past N units of
                relative_unit_type
            absolute_date_start (Optional[datetime.datetime], optional): Filter records that are
                after this date. (overrides relative values)
            absolute_date_end (Optional[datetime.datetime], optional): Filter records that are
                before this date. (defaults to now if start but no end)
            sort_attribute (Optional[str], optional): Sort records based on this attribute
            sort_descending (bool, optional): Sort sort_attribute descending or ascending
            page_sleep (int, optional): Sleep N seconds between pages
            page_size (int, optional): Get N records per page
            row_start (int, optional): Start at row N
            row_stop (Optional[int], optional): Stop at row N
            log_level (t.Union[int, str], optional): log level to use for paging
            history_filters (Optional[AdapterFetchHistoryFilters], optional): response
                from :meth:`get_fetch_history_filters` (will be fetched if not supplied)
            request_obj (Optional[AdapterFetchHistoryRequest], optional): Request object to use
                for options
        """
        if not isinstance(history_filters, AdapterFetchHistoryFilters):
            history_filters = self.get_fetch_history_filters()

        if not isinstance(request_obj, AdapterFetchHistoryRequest):
            request_obj = AdapterFetchHistoryRequest()

        request_obj.set_filters(
            history_filters=history_filters,
            value_type="adapters",
            value=adapters,
        )
        request_obj.set_filters(
            history_filters=history_filters,
            value_type="connection_labels",
            value=connection_labels,
        )
        request_obj.set_filters(
            history_filters=history_filters,
            value_type="clients",
            value=clients,
        )
        request_obj.set_filters(
            history_filters=history_filters,
            value_type="instances",
            value=instances,
        )
        request_obj.set_filters(
            history_filters=history_filters,
            value_type="statuses",
            value=statuses,
        )
        request_obj.set_filters(
            history_filters=history_filters,
            value_type="discoveries",
            value=discoveries,
        )
        request_obj.set_sort(
            value=sort_attribute,
            descending=sort_descending,
        )
        request_obj.set_exclude_realtime(
            value=exclude_realtime,
        )
        request_obj.set_time_range(
            relative_unit_type=relative_unit_type,
            relative_unit_count=relative_unit_count,
            absolute_date_start=absolute_date_start,
            absolute_date_end=absolute_date_end,
        )
        request_obj.set_search_filter(
            search=search,
            filter=filter,
        )

        with PagingState(
            purpose="Get Adapter Fetch History Events",
            page_sleep=page_sleep,
            page_size=page_size,
            row_start=row_start,
            row_stop=row_stop,
            log_level=log_level,
        ) as state:
            while not state.stop_paging:
                page = state.page(method=self._get_fetch_history, request_obj=request_obj)
                yield from page.rows

    def config_get(
        self,
        name: str,
        node: t.Optional[str] = None,
        config_type: str = "generic",
    ) -> dict:
        """Get the advanced settings for an adapter.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Get the generic advanced settings for an adapter

            >>> config = client.adapters.config_get(name="aws")

            Get the adapter specific advanced settings for an adapter

            >>> config = client.adapters.config_get(name="aws", config_type="specific")

            Get the discovery advanced settings for an adapter

            >>> config = client.adapters.config_get(name="aws", config_type="discovery")

            See the current values of a configuration

            >>> import pprint
            >>> pprint.pprint(config['config'])
            {'connect_client_timeout': 300,
             'fetching_timeout': 43200,
             'last_fetched_threshold_hours': 48,
             'last_seen_prioritized': False,
             'last_seen_threshold_hours': 24,
             'minimum_time_until_next_fetch': None,
             'realtime_adapter': False,
             'user_last_fetched_threshold_hours': 48,
             'user_last_seen_threshold_hours': None}

            Investigate the schema and current values of a configuration

            >>> for setting, info in config['schema'].items():
            ...    current_value = config['config'][setting]
            ...    title = info['title']
            ...    description = info.get('description')
            ...    print(f"name of setting: {setting}")
            ...    print(f"  title of setting in GUI: {title}")
            ...    print(f"  description of setting: {description}")
            ...    print(f"  current value of setting: {current_value}")

        Args:
            name (str): name of adapter to get advanced settings of
            node (Optional[str], optional): name of node to get adapter from [NO LONGER USED]
            config_type (str, optional): One of generic, specific, or discovery

        Returns:
            dict: configuration for ``config_type``
        """
        adapter = self.get_by_name(name=name, node=node, get_clients=False)
        adapters = self._config_get(adapter_name=adapter["name_raw"])
        type_map = adapters.type_map
        if config_type not in type_map:
            valid = ", ".join(list(type_map))
            raise ApiError(f"Adapter {name} has no config type {config_type!r}, valids: {valid}!")

        adapter_config = type_map[config_type]
        adapter_config["adapter"] = adapter
        return adapter_config

    def config_update(
        self, name: str, node: t.Optional[str] = None, config_type: str = "generic", **kwargs
    ) -> dict:
        """Update the advanced settings for an adapter.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Update the generic advanced settings for the adapter

            >>> updated_config = client.adapters.config_update(
            ...     name="aws", last_seen_threshold_hours=24
            ... )

            Update the adapter specific advanced settings

            >>> updated_config = client.adapters.config_update(
            ...     name="aws", config_type="specific", fetch_s3=True
            ... )


        Args:
            name (str): name of adapter to update advanced settings of
            node (Optional[str], optional): name of node to get adapter from
            config_type (str, optional): One of generic, specific, or discovery
            **kwargs: configuration to update advanced settings of config_type

        Returns:
            dict: updated configuration for ``config_type``
        """
        kwargs_config = kwargs.pop("kwargs_config", {})
        kwargs.update(kwargs_config)

        config_map = self.config_get(name=name, config_type=config_type)

        adapter_meta = config_map["adapter"]
        old_config = config_map["config"]
        schemas = config_map["schema"]

        source = f"adapter {name!r} {config_type} advanced settings"
        config_unknown(schemas=schemas, new_config=kwargs, source=source)
        new_config = config_build(
            schemas=schemas, old_config=old_config, new_config=kwargs, source=source
        )
        config_unchanged(
            schemas=schemas, old_config=old_config, new_config=new_config, source=source
        )

        self._config_update(
            adapter_name=adapter_meta["name_raw"],
            config_name=config_map["config_name"],
            config=new_config,
        )
        return self.config_get(name=name, config_type=config_type)

    def file_upload(
        self,
        name: str,
        field_name: str,
        file_name: str,
        file_content: t.Union[str, bytes],
        file_content_type: t.Optional[str] = None,
        node: t.Optional[str] = None,
    ) -> dict:
        """Upload a file to a specific adapter on a specific node.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Upload content as a file for use in a connection later

            >>> content = "content of file to upload"
            >>> file_uuid = client.adapters.file_upload(
            ...     name="aws",
            ...     file_name="name_of_file",
            ...     file_content=content,
            ...     field_name="name_of_field",
            ... )
            >>> file_uuid
            {'uuid': '5f78b7dee33f0a113700a6fc', 'filename': 'name_of_file'}

        Args:
            name: name of adapter to upload file to
            node: name of node to upload file to
            field_name: name of field (should match configuration schema key name)
            file_name: name of file to upload
            file_content: content of file to upload
            file_content_type: mime type of file to upload

        Returns:
            dict: with keys 'filename' and 'uuid'
        """
        adapter = self.get_by_name(name=name, node=node, get_clients=False)

        return self._file_upload(
            adapter_name=adapter["name_raw"],
            node_id=adapter["node_id"],
            file_name=file_name,
            field_name=field_name,
            file_content=file_content,
            file_content_type=file_content_type,
        )

    def file_upload_path(self, path: t.Union[str, pathlib.Path], **kwargs) -> dict:
        """Upload the contents of a file to a specific adapter on a specific node.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

            Upload a file for use in a connection later

            >>> file_uuid = client.adapters.file_upload_path(name="aws", path="test.csv")
            >>> file_uuid
            {'uuid': '5f78b674e33f0a113700a6fa', 'filename': 'test.csv'}

        Args:
            path (t.Union[str, pathlib.Path]): path to file containing contents to upload
            **kwargs: passed to :meth:`file_upload`

        Returns:
            dict: with keys 'filename' and 'uuid'
        """
        path, file_content = path_read(obj=path, binary=True, is_json=False)
        if path.suffix == ".csv":
            kwargs.setdefault("file_content_type", "text/csv")
        kwargs.setdefault("field_name", path.name)
        kwargs.setdefault("file_name", path.name)
        kwargs["file_content"] = file_content
        return self.file_upload(**kwargs)

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        from ..system.instances import Instances
        from .cnx import Cnx

        self.cnx: Cnx = Cnx(parent=self)
        """Work with adapter connections"""

        self.instances: Instances = Instances(auth=self.auth)
        """Work with instances"""

    def _get(self, get_clients: bool = False, filter: t.Optional[str] = None) -> t.List[Adapter]:
        """Private API method to get all adapters.

        Args:
            get_clients (bool, optional): Include the connections and schemas in the response
            filter (Optional[str], optional): unk

        Returns:
            t.List[Adapter]: t.List of Adapter dataclass models
        """
        api_endpoint = ApiEndpoints.adapters.get
        request_obj = api_endpoint.load_request(get_clients=get_clients, filter=filter)
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _config_update(self, adapter_name: str, config_name: str, config: dict) -> SystemSettings:
        """Private API method to set advanced settings for an adapter.

        Args:
            adapter_name (str): raw name of the adapter i.e. ``aws_adapter``
            config_name (str): name of advanced settings to set

                * ``AdapterBase`` for generic advanced settings
                * ``AwsSettings`` for adapter specific advanced settings (name changes per adapter)
                * ``DiscoverySchema`` for discovery advanced settings
            config (dict): the advanced configuration key value pairs to set

        Returns:
            SystemSettings: dataclass model containing response
        """
        api_endpoint = ApiEndpoints.adapters.settings_update
        request_obj = api_endpoint.load_request(
            pluginId=adapter_name, configName=config_name, config=config
        )
        return api_endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            adapter_name=adapter_name,
            config_name=config_name,
        )

    def _get_basic(self) -> AdaptersList:
        """Get the basic metadata for all adapters.

        Returns:
            AdaptersList: dataclass model containing response
        """
        api_endpoint = ApiEndpoints.adapters.get_basic
        return api_endpoint.perform_request(http=self.auth.http)

    def _config_get(self, adapter_name: str) -> AdapterSettings:
        """Private API method to set advanced settings for an adapter.

        Args:
            adapter_name (str): raw name of the adapter, i.e. 'aws_adapter'

        Returns:
            AdapterSettings: dataclass model containing response
        """
        api_endpoint = ApiEndpoints.adapters.settings_get
        return api_endpoint.perform_request(http=self.auth.http, adapter_name=adapter_name)

    def _file_upload(
        self,
        adapter_name: str,
        node_id: str,
        field_name: str,
        file_name: str,
        file_content: t.Union[bytes, str],
        file_content_type: t.Optional[str] = None,
        file_headers: t.Optional[dict] = None,
    ) -> dict:
        """Private API method to upload a file to a specific adapter on a specifc node.

        Args:
            adapter_name (str): raw name of the adapter i.e. ``aws_adapter``
            node_id (str): ID of node running adapter
            field_name (str): name of field (should match configuration schema key name)
            file_name (str): name of file to upload
            file_content (t.Union[bytes, str]): content of file to upload
            file_content_type (Optional[str], optional): mime type of file to upload
            file_headers (Optional[dict], optional): headers to use for file

        Returns:
            dict: containing filename and uuid keys
        """
        api_endpoint = ApiEndpoints.adapters.file_upload

        data = {"field_name": field_name}
        files = {"userfile": (file_name, file_content, file_content_type, file_headers)}
        http_args = {"files": files, "data": data}

        response = api_endpoint.perform_request(
            http=self.auth.http, http_args=http_args, adapter_name=adapter_name, node_id=node_id
        )
        parsed = {"filename": file_name, "uuid": response["data"]["id"]}
        return parsed

    def _get_labels(self) -> CnxLabels:
        """Get labels metadata for all connections.

        Returns:
            CnxLabels: dataclass model containing response
        """
        api_endpoint = ApiEndpoints.adapters.cnx_get_labels
        response = api_endpoint.perform_request(http=self.http)
        return response

    def _get_fetch_history_filters(self) -> AdapterFetchHistoryFilters:
        """Get filter values for use in adapters history."""
        api_endpoint = ApiEndpoints.adapters.get_fetch_history_filters
        response = api_endpoint.perform_request(http=self.http)
        return response

    def _get_fetch_history(
        self, request_obj: t.Optional[AdapterFetchHistoryRequest] = None
    ) -> HIST_LIST:
        """Get adapter fetch history."""
        api_endpoint = ApiEndpoints.adapters.get_fetch_history
        if not request_obj:
            request_obj = AdapterFetchHistoryRequest()
        response = api_endpoint.perform_request(http=self.http, request_obj=request_obj)
        return response
