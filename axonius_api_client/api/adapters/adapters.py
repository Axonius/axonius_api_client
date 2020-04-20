# -*- coding: utf-8 -*-
"""API models for working with adapters and connections."""
from ...constants import DEFAULT_NODE
from ...exceptions import ApiError, NotFoundError
from ...tools import path_read
from ..mixins import ModelMixins
from ..parsers.adapters import parse_adapters, parse_schema
from ..parsers.config import config_build, config_unchanged, config_unknown
from ..parsers.tables import tablize_adapters
from ..routers import API_VERSION
from .cnx import Cnx


class Adapters(ModelMixins):
    """API model for working with adapters."""

    @property
    def router(self):
        """Router for this API model."""
        return API_VERSION.adapters

    def get(self):
        """Pass."""
        parsed = parse_adapters(raw=self._get())
        parsed = sorted(parsed, key=lambda x: [x["node_name"], x["name"]])
        return parsed

    def get_by_name(self, name, node=DEFAULT_NODE):
        """Pass."""
        adapters = self.get()

        keys = ["node_name", "node_id"]
        nodes = [x for x in adapters if node.lower() in [x[k].lower() for k in keys]]

        if not nodes:
            err = f"No node named {node!r} found"
            raise NotFoundError(tablize_adapters(adapters=adapters, err=err))

        keys = ["name", "name_raw", "name_plugin"]
        for adapter in nodes:
            if any([adapter[k].lower() == name.lower() for k in keys]):
                return adapter

        err = f"No adapter named {name!r} found on node {node!r}"
        raise NotFoundError(tablize_adapters(adapters=adapters, err=err))

    def config_get(self, name, node=DEFAULT_NODE, generic=True):
        """Pass."""
        adapter = self.get_by_name(name=name, node=node)
        return self.config_refetch(adapter=adapter, generic=generic)

    def config_refetch(self, adapter, generic=True):
        """Pass."""
        name_config = "generic_name" if generic else "specific_name"
        name_config = adapter["schemas"][name_config]
        name_plugin = adapter["name_plugin"]

        if not generic and not name_config:
            name = adapter["name"]
            raise ApiError(f"Adapter {name} has no adapter specific advanced settings!")

        data = self._config_get(name_plugin=name_plugin, name_config=name_config)

        data["schema"] = parse_schema(raw=data["schema"])

        return data

    def config_update(self, name, node=DEFAULT_NODE, generic=True, **kwargs):
        """Pass."""
        kwargs_config = kwargs.pop("kwargs_config", {})
        kwargs.update(kwargs_config)
        adapter = self.get_by_name(name=name, node=node)

        name_config = "generic_name" if generic else "specific_name"
        name_config_src = "generic" if generic else "adapter specific"
        name_config = adapter["schemas"][name_config]

        config_map = self.config_refetch(adapter=adapter, generic=generic)
        old_config = config_map["config"]
        schemas = config_map["schema"]

        source = f"adapter {name!r} {name_config_src} advanced settings"
        config_unknown(schemas=schemas, new_config=kwargs, source=source)
        new_config = config_build(
            schemas=schemas, old_config=old_config, new_config=kwargs, source=source
        )
        config_unchanged(
            schemas=schemas, old_config=old_config, new_config=new_config, source=source
        )

        self._config_update(
            name_raw=adapter["name_raw"], name_config=name_config, new_config=new_config,
        )

        return self.config_refetch(adapter=adapter, generic=generic)

    def file_upload(
        self,
        name,
        field_name,
        file_name,
        file_content,
        file_content_type=None,
        node=DEFAULT_NODE,
    ):
        """Upload a str as a file to a specific adapter on a specific node.

        Args:
            adapter (:obj:`str` or :obj:`dict`):

                * If :obj:`str`, the name of the adapter to get the metadata for
                * If :obj:`dict`, the metadata for a previously fetched adapter
            field (:obj:`str`): name of field to store data in
            name (:obj:`str`): filename to use when uploading file
            content (:obj:`str` or :obj:`bytes`): content of file to upload
            node (:obj:`str`, optional): default
                :data:`.DEFAULT_NODE` -
                node name running ``adapter``
            content_type (:obj:`str`, optional): default ``None`` -
                mime type of **content**

        Returns:
            :obj:`dict`: dict that can be used in a connection parameter of type
            file that contains the keys:

              * uuid: UUID of uploaded file
              * filename: filename of uploaded file
        """
        adapter = self.get_by_name(name=name, node=node)

        return self._file_upload(
            name_raw=adapter["name_raw"],
            node_id=adapter["node_id"],
            file_name=file_name,
            field_name=field_name,
            file_content=file_content,
            file_content_type=file_content_type,
        )

    def file_upload_path(self, path, **kwargs):
        """Upload the contents of a file to a specific adapter on a specific node.

        Args:
            adapter (:obj:`str` or :obj:`dict`):

                * If :obj:`str`, the name of the adapter to get the metadata for
                * If :obj:`dict`, the metadata for a previously fetched adapter
            field (:obj:`str`): name of field to store data in
            name (:obj:`str`): filename to use when uploading file
            path (:obj:`str` or :obj:`pathlib.Path`): path to file containing contents
                to upload
            node (:obj:`str`, optional): default
                :data:`.DEFAULT_NODE` -
                node name running ``adapter``
            content_type (:obj:`str`, optional): default ``None`` -
                mime type of **content**

        Returns:
            :obj:`dict`: dict that can be used in a connection parameter of type
            file that contains the keys:

              * uuid: UUID of uploaded file
              * filename: filename of uploaded file
        """
        path, file_content = path_read(obj=path, binary=True, is_json=False)
        kwargs.setdefault("field_name", path.name)
        kwargs.setdefault("file_name", path.name)
        kwargs["file_content"] = file_content
        return self.file_upload(**kwargs)

    def _init(self, auth, **kwargs):
        """Post init method for subclasses to use for extra setup.

        Args:
            auth (:obj:`.auth.Model`): object to use for auth and sending API requests
        """
        self.cnx = Cnx(parent=self)
        super(Adapters, self)._init(auth=auth, **kwargs)

    def _get(self):
        """Direct API method to get all adapters.

        Returns:
            :obj:`dict`: raw metadata for all adapters
        """
        path = self.router.root
        return self.request(method="get", path=path)

    def _config_update(self, name_raw, name_config, new_config):
        """Direct API method to set advanced settings for an adapter.

        Args:
            name_raw (:obj:`str`): unique plugin name of adapter to set
                advanced settings for. unique plugin name refers to the name of
                an adapter for a specific node
            name_config (:obj:`str`): name of advanced settings to set -
                either AdapterBase for generic advanced settings or
                AwsSettings for adapter specific settings, if applicable
            config (:obj:`dict`): the configuration values to set

        Returns:
            :obj:`str`: empty str
        """
        path = self.router.config_set.format(
            adapter_name_raw=name_raw, adapter_config_name=name_config
        )
        return self.request(
            method="post", path=path, json=new_config, error_json_invalid=False
        )

    def _config_get(self, name_plugin, name_config):
        """Direct API method to set advanced settings for an adapter.

        Args:
            name_plugin (:obj:`str`): unique plugin name of adapter to set
                advanced settings for. unique plugin name refers to the name of
                an adapter for a specific node i.e. aws_adapter_0
            name_config (:obj:`str`): name of advanced settings to set -
                either AdapterBase for generic advanced settings or
                AwsSettings for adapter specific settings, if applicable

        Returns:
            :obj:`dict`: current settings for name_config of name_plugin
        """
        path = self.router.config_get.format(
            adapter_name_plugin=name_plugin, adapter_config_name=name_config
        )
        return self.request(method="get", path=path)

    def _file_upload(
        self,
        name_raw,
        node_id,
        field_name,
        file_name,
        file_content,
        file_content_type=None,
        file_headers=None,
    ):
        """Direct API method to upload a file to a specific adapter on a specifc node.

        Args:
            name_raw (:obj:`str`): name of the adapter to upload a file to
            node_id (:obj:`str`): ID of node running **adapter**
            field_name (:obj:`str`): name of setting this file is intended for
            file_name (:obj:`str`): filename to use when uploading file
            file_content (:obj:`str` or :obj:`bytes`): content to upload
            file_content_type (:obj:`str`, optional): default ``None`` -
                mime type of **content**
            file_headers (:obj:`dict`, optional): default ``None`` -
                headers to use for file **content**

        Returns:
            :obj:`dict`: dict that can be used in a connection parameter of type
            file that contains the keys:

              * uuid: UUID of uploaded file
              * filename: filename of uploaded file
        """
        data = {"field_name": field_name}
        files = {"userfile": (file_name, file_content, file_content_type, file_headers)}
        path = self.router.file_upload.format(
            adapter_name_raw=name_raw, adapter_node_id=node_id
        )
        ret = self.request(method="post", path=path, data=data, files=files)
        ret["filename"] = file_name
        return ret

    # def _download_file(self, name, node_id, cnx_id, schema_key):
    #     """Direct API method to download a file.

    #     Notes:
    #         WORK IN PROGRESS!

    #     """
    #     data = {"uuid": cnx_id, "schema_key": schema_key}
    #     path = self.router.download_file.format(
    #         name=name, node_id=node_id
    #     )
    #     ret = self.request(method="post", path=path, json=data, raw=True)
    #     return ret
