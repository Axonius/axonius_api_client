# -*- coding: utf-8 -*-
"""API models for working with adapters and connections."""
import time
from typing import IO, List, Union

from ...constants import CNX_GONE, CNX_RETRY, CNX_SANE_DEFAULTS, DEFAULT_NODE
from ...exceptions import (
    CnxAddError,
    CnxGoneError,
    CnxTestError,
    CnxUpdateError,
    ConfigInvalidValue,
    ConfigRequired,
    NotFoundError,
)
from ...tools import json_load, pathlib
from ..mixins import ChildMixins
from ..parsers.config import (
    config_build,
    config_default,
    config_empty,
    config_info,
    config_required,
    config_unchanged,
    config_unknown,
)
from ..parsers.tables import tablize_cnxs, tablize_schemas


class Cnx(ChildMixins):
    """API model for working with adapter connections."""

    def add(self, adapter_name: str, adapter_node: str = DEFAULT_NODE, **kwargs) -> dict:
        """Pass."""
        kwargs_config = kwargs.pop("kwargs_config", {})
        kwargs.update(kwargs_config)

        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node)
        cnx_schemas = adapter["schemas"]["cnx"]
        adapter_name = adapter["name"]
        adapter_node_name = adapter["node_name"]
        adapter_name_raw = adapter["name_raw"]
        adapter_node_id = adapter["node_id"]

        source = f"adding connection for adapter {adapter_name!r}"

        new_config = self.build_config(
            cnx_schemas=cnx_schemas,
            old_config={},
            new_config=kwargs,
            source=source,
            adapter_name=adapter_name,
            adapter_node=adapter_node_name,
        )

        sane_defaults = self.get_sane_defaults(adapter_name=adapter_name)

        config_default(
            schemas=cnx_schemas,
            new_config=new_config,
            source=source,
            sane_defaults=sane_defaults,
        )

        config_empty(schemas=cnx_schemas, new_config=new_config, source=source)

        config_required(schemas=cnx_schemas, new_config=new_config, source=source)

        result = self._add(
            adapter_name_raw=adapter_name_raw,
            adapter_node_id=adapter_node_id,
            new_config=new_config,
        )

        error_in_status = result.get("status", "") == "error"
        error_empty = bool(result.get("error", ""))

        cnx_new = self.get_by_uuid(
            cnx_uuid=result["id"],
            adapter_name=adapter_name,
            adapter_node=adapter_node,
            retry=CNX_RETRY,
        )

        if any([error_in_status, error_empty]):
            rkw = ["{}: {}".format(k, v) for k, v in result.items()]
            rkw = "\n  " + "\n  ".join(rkw)

            err = f"Connection was added but had a failure connecting:{rkw}"
            exc = CnxAddError(err)

            exc.result = result
            exc.cnx_new = cnx_new
            raise exc

        return cnx_new

    def get_sane_defaults(self, adapter_name: str) -> dict:
        """Pass."""
        return CNX_SANE_DEFAULTS.get(adapter_name, CNX_SANE_DEFAULTS["all"])

    def get_by_adapter(
        self, adapter_name: str, adapter_node: str = DEFAULT_NODE
    ) -> List[dict]:
        """Get connections from an adapter."""
        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node)
        cnxs = adapter["cnx"]

        for cnx in cnxs:
            cnx["schemas"] = adapter["schemas"]["cnx"]

        return cnxs

    def get_by_key(
        self,
        value: str,
        value_key: str,
        adapter_name: str,
        adapter_node: str = DEFAULT_NODE,
        retry: int = 0,
        sleep: int = 1,
    ) -> dict:
        """Pass."""
        tries = 1
        cnxs = self.get_by_adapter(adapter_name=adapter_name, adapter_node=adapter_node)
        while True:
            for cnx in cnxs:
                if cnx[value_key] == value:
                    return cnx

            tries += 1

            if tries > retry:
                break

            time.sleep(sleep)

            cnxs = self.get_by_adapter(
                adapter_name=adapter_name, adapter_node=adapter_node
            )

        value_key = value_key.upper()
        err = (
            f"No connection found on adapter {adapter_name!r} node {adapter_node!r} "
            f"with {value_key} of {value!r}"
        )
        raise NotFoundError(tablize_cnxs(cnxs=cnxs, err=err))

    def get_by_uuid(
        self,
        cnx_uuid: str,
        adapter_name: str,
        adapter_node: str = DEFAULT_NODE,
        **kwargs,
    ) -> dict:
        """Pass."""
        kwargs["value_key"] = "uuid"
        return self.get_by_key(
            value=cnx_uuid,
            adapter_name=adapter_name,
            adapter_node=adapter_node,
            **kwargs,
        )

    def get_by_id(
        self, cnx_id: str, adapter_name: str, adapter_node: str = DEFAULT_NODE, **kwargs
    ) -> dict:
        """Pass."""
        kwargs["value_key"] = "id"
        return self.get_by_key(
            value=cnx_id, adapter_name=adapter_name, adapter_node=adapter_node, **kwargs
        )

    # XXX add get_by_label
    def test_by_id(
        self, cnx_id: str, adapter_name: str, adapter_node: str = DEFAULT_NODE
    ) -> str:
        """Pass."""
        cnx_test = self.get_by_id(
            cnx_id=cnx_id, adapter_name=adapter_name, adapter_node=adapter_node
        )
        return self.test_cnx(cnx_test=cnx_test)

    def test_cnx(self, cnx_test: dict, **kwargs) -> str:
        """Pass."""
        test_adapter_meta = {
            "adapter_name": cnx_test["adapter_name"],
            "adapter_name_raw": cnx_test["adapter_name_raw"],
            "adapter_node_id": cnx_test["node_id"],
            "adapter_node_name": cnx_test["node_name"],
            "cnx_schemas": cnx_test["schemas"],
        }

        test_old_config = cnx_test["config"]

        return self.do_test(
            test_adapter_meta=test_adapter_meta,
            test_old_config=test_old_config,
            **kwargs,
        )

    def test(self, adapter_name: str, adapter_node: str = DEFAULT_NODE, **kwargs) -> str:
        """Pass."""
        adapter = self.parent.get_by_name(name=adapter_name, node=adapter_node)

        test_adapter_meta = {
            "adapter_name": adapter["name"],
            "adapter_name_raw": adapter["name_raw"],
            "adapter_node_id": adapter["node_id"],
            "adapter_node_name": adapter["node_name"],
            "cnx_schemas": adapter["schemas"]["cnx"],
        }

        test_old_config = {}

        return self.do_test(
            test_adapter_meta=test_adapter_meta,
            test_old_config=test_old_config,
            **kwargs,
        )

    def do_test(self, test_adapter_meta: dict, test_old_config: dict, **kwargs) -> str:
        """Pass."""
        kwargs_config = kwargs.pop("kwargs_config", {})
        kwargs.update(kwargs_config)
        adapter_name = test_adapter_meta["adapter_name"]
        adapter_name_raw = test_adapter_meta["adapter_name_raw"]
        adapter_node_id = test_adapter_meta["adapter_node_id"]
        adapter_node_name = test_adapter_meta["adapter_node_name"]
        cnx_schemas = test_adapter_meta["cnx_schemas"]

        source = f"reachability test for adapter {adapter_name!r}"

        new_config = self.build_config(
            cnx_schemas=cnx_schemas,
            old_config=test_old_config,
            new_config=kwargs,
            source=source,
            adapter_name=adapter_name,
            adapter_node=adapter_node_name,
        )

        config_empty(schemas=cnx_schemas, new_config=new_config, source=source)

        result = self._test(
            adapter_name_raw=adapter_name_raw,
            adapter_node_id=adapter_node_id,
            config=new_config,
        )

        rtext = (result.text or "").strip()
        rjson = json_load(obj=rtext, error=False) if rtext else {}

        had_error = not result.ok or bool(rtext)

        if had_error:
            if rjson.get("type") == "AttributeError":
                err = (
                    "Reachability test failed due to settings required for "
                    "testing reachability (supply at least hostname/domain/etc)"
                )
                msg = tablize_schemas(schemas=cnx_schemas, err=err)
                raise ConfigRequired(msg)
            else:
                rkw = ["{}: {}".format(k, v) for k, v in rjson.items()]
                rkw = "\n  " + "\n  ".join(rkw)
                msg = f"Reachability test failed:{rkw}"
                raise CnxTestError(msg)
        return rtext

    def update_cnx(self, cnx_update: dict, **kwargs) -> dict:
        """Pass."""
        kwargs_config = kwargs.pop("kwargs_config", {})
        kwargs.update(kwargs_config)

        adapter_name = cnx_update["adapter_name"]
        adapter_name_raw = cnx_update["adapter_name_raw"]
        adapter_node_name = cnx_update["node_name"]
        adapter_node_id = cnx_update["node_id"]
        cnx_schemas = cnx_update["schemas"]

        old_config = cnx_update["config"]
        old_uuid = cnx_update["uuid"]
        old_id = cnx_update["id"]

        source = (
            f"updating settings for connection ID {old_id!r} on adapter {adapter_name!r}"
        )

        new_config = self.build_config(
            cnx_schemas=cnx_schemas,
            old_config=old_config,
            new_config=kwargs,
            source=source,
            adapter_name=adapter_name,
            adapter_node=adapter_node_name,
        )

        config_empty(schemas=cnx_schemas, new_config=new_config, source=source)

        config_unchanged(
            schemas=cnx_schemas,
            old_config=old_config,
            new_config=new_config,
            source=source,
        )

        result = self._update(
            adapter_name_raw=adapter_name_raw,
            adapter_node_id=adapter_node_id,
            new_config=new_config,
            cnx_uuid=old_uuid,
        )

        result = {} if not isinstance(result, dict) else result

        self.check_if_gone(
            result=result,
            cnx_id=old_id,
            adapter_name=adapter_name,
            adapter_node=adapter_node_name,
        )

        if result.get("id"):
            cnx_new = self.get_by_uuid(
                cnx_uuid=result["id"],
                adapter_name=adapter_name,
                adapter_node=adapter_node_name,
                retry=CNX_RETRY,
            )
        else:
            cnx_new = self.get_by_id(
                cnx_id=old_id, adapter_name=adapter_name, adapter_node=adapter_node_name
            )

        error_in_status = result.get("status", "") == "error"
        error_empty = bool(result.get("error", ""))

        if any([error_in_status, error_empty]):
            rkw = ["{}: {}".format(k, v) for k, v in result.items()]
            rkw = "\n  " + "\n  ".join(rkw)

            err = f"Connection was updated but had a failure connecting:{rkw}"
            exc = CnxUpdateError(err)

            exc.result = result
            exc.cnx_old = cnx_update
            exc.cnx_new = cnx_new

            raise exc

        return cnx_new

    def check_if_gone(
        self, result: dict, cnx_id: str, adapter_name: str, adapter_node: str
    ):
        """Pass."""
        message = result.get("message", "")
        if message == CNX_GONE:
            cnxs = self.get_by_adapter(
                adapter_name=adapter_name, adapter_node=adapter_node
            )
            err = f"Connection with ID {cnx_id!r} no longer exists!"
            raise CnxGoneError(tablize_cnxs(cnxs=cnxs, err=err))

    def update_by_id(
        self, cnx_id: str, adapter_name: str, adapter_node: str = DEFAULT_NODE, **kwargs
    ) -> dict:
        """Pass."""
        cnx_update = self.get_by_id(
            cnx_id=cnx_id, adapter_name=adapter_name, adapter_node=adapter_node
        )
        return self.update_cnx(cnx_update=cnx_update, **kwargs)

    def delete_cnx(self, cnx_delete: dict, delete_entities: bool = False) -> str:
        """Pass."""
        adapter_name_raw = cnx_delete["adapter_name_raw"]
        adapter_node_id = cnx_delete["node_id"]
        cnx_uuid = cnx_delete["uuid"]

        return self._delete(
            adapter_name_raw=adapter_name_raw,
            adapter_node_id=adapter_node_id,
            cnx_uuid=cnx_uuid,
            delete_entities=delete_entities,
        )

    def delete_by_id(
        self,
        cnx_id: str,
        adapter_name: str,
        adapter_node: str = DEFAULT_NODE,
        delete_entities: bool = False,
    ) -> str:
        """Pass."""
        cnx_delete = self.get_by_id(
            cnx_id=cnx_id, adapter_name=adapter_name, adapter_node=adapter_node
        )
        return self.delete_cnx(cnx_delete=cnx_delete, delete_entities=delete_entities)

    def build_config(
        self,
        cnx_schemas: List[dict],
        old_config: dict,
        new_config: dict,
        source: str,
        adapter_name: str,
        adapter_node: str,
    ) -> dict:
        """Pass."""
        callbacks = {
            "cb_file": self.cb_file_upload,
            "adapter_name": adapter_name,
            "adapter_node": adapter_node,
        }

        config_unknown(
            schemas=cnx_schemas,
            new_config=new_config,
            source=source,
            callbacks=callbacks,
        )

        new_config = config_build(
            schemas=cnx_schemas,
            old_config=old_config,
            new_config=new_config,
            source=source,
            callbacks=callbacks,
        )

        return new_config

    def cb_file_upload(
        self,
        value: Union[str, pathlib.Path, IO],
        schema: dict,
        callbacks: dict,
        source: str,
    ) -> dict:
        """Pass."""
        adapter_name = callbacks["adapter_name"]
        adapter_node = callbacks["adapter_node"]
        field_name = schema["name"]

        if isinstance(value, str):
            check = pathlib.Path(value).expanduser().resolve()
            if check.is_file():
                value = check

        if isinstance(value, pathlib.Path):
            value = value.expanduser().resolve()
            if not value.is_file():
                sinfo = config_info(schema=schema, value=str(value), source=source)
                raise ConfigInvalidValue(f"{sinfo}\nFile does not exist!")

            file_name = value.name
            file_content = value.read_text()
        elif hasattr(value, "read"):
            file_content = value.read()
            file_name = file_content[:20]
        else:
            sinfo = config_info(schema=schema, value=str(value), source=source)
            raise ConfigInvalidValue(
                f"{sinfo}\nFile is not an existing file or a file-like object!"
            )

        return self.parent.file_upload(
            name=adapter_name,
            field_name=field_name,
            file_name=file_name,
            file_content=file_content,
            node=adapter_node,
        )

    def _add(self, adapter_name_raw: str, adapter_node_id: str, new_config: dict) -> str:
        """Direct API method to add a connection to an adapter.

        Args:
            adapter: name of adapter
            node_id: id of node running **adapter**
            config: configuration values for new connection

        Returns:
            an empty str
        """
        data = {}
        data.update(new_config)
        data["instanceName"] = adapter_node_id

        path = self.parent.router.cnxs.format(adapter_name_raw=adapter_name_raw)

        return self.parent.request(
            method="put",
            path=path,
            json=data,
            error_json_bad_status=False,
            error_status=False,
        )

    def _test(self, adapter_name_raw: str, adapter_node_id: str, config: dict) -> str:
        """Direct API method to add a connection to an adapter.

        Args:
            adapter: name of adapter
            node_id: id of node running **adapter**
            config: configuration values to test reachability for

        Returns:
            an empty str
        """
        data = {}
        data.update(config)
        data["instanceName"] = adapter_node_id
        data["oldInstanceName"] = adapter_node_id

        path = self.parent.router.cnxs.format(adapter_name_raw=adapter_name_raw)

        return self.parent.request(method="post", path=path, json=data, raw=True)

    def _delete(
        self,
        adapter_name_raw: str,
        adapter_node_id: str,
        cnx_uuid: str,
        delete_entities: bool = False,
    ) -> str:
        """Direct API method to delete a connection from an adapter.

        Args:
            name_raw: name_raw of adapter
            node_id: id of node running **adapter**
            uuid: uuid of connection to delete
            delete_entities: default ``False`` -

                * if ``True`` delete the connection and also delete all asset entities
                  fetched by this connection
                * if ``False`` just delete the connection

        Returns:
            an empty str
        """
        data = {}
        data["instanceName"] = adapter_node_id

        params = {"deleteEntities": delete_entities}

        path = self.parent.router.cnxs_uuid.format(
            adapter_name_raw=adapter_name_raw, cnx_uuid=cnx_uuid
        )

        return self.parent.request(
            method="delete",
            path=path,
            json=data,
            params=params,
            error_json_bad_status=False,
            error_status=False,
        )

    def _update(
        self,
        adapter_name_raw: str,
        adapter_node_id: str,
        new_config: dict,
        cnx_uuid: str,
    ) -> str:
        """Direct API method to update a connection on an adapter.

        Args:
            name_raw: name_raw of adapter
            node_id: id of node running **adapter**
            config: configuration of connection to update
            uuid: uuid of connection to update

        Returns:
            an empty str
        """
        data = {}
        data.update(new_config)
        data["instanceName"] = adapter_node_id
        data["oldInstanceName"] = adapter_node_id

        path = self.parent.router.cnxs_uuid.format(
            adapter_name_raw=adapter_name_raw, cnx_uuid=cnx_uuid
        )
        return self.parent.request(
            method="put",
            path=path,
            json=data,
            error_json_bad_status=False,
            error_status=False,
        )
