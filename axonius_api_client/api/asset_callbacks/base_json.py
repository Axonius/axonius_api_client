# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import json

import jsonstreams

from ...tools import listify
from .base import Base


class Json(Base):
    """Pass."""

    CB_NAME = "json"

    def start(self, **kwargs):
        """Create jsonstream and associated file descriptor."""
        super(Json, self).start(**kwargs)
        self.open_fd()
        self._stream = JsonStream(fd=self._fd)

    def stop(self, **kwargs):
        """Close jsonstream and associated file descriptor."""
        super(Json, self).stop(**kwargs)
        self.do_export_schema()
        self._stream.close()
        self._fd.write("\n")
        self.close_fd()

    def process_row(self, row):
        """Write row to jsonstreams and delete it."""
        return_row = [{"internal_axon_id": row["internal_axon_id"]}]

        new_rows = self._process_row(row=row)

        for new_row in listify(new_rows):
            self._stream.write(new_row)
            del new_row

        del new_rows
        del row

        return return_row

    def do_export_schema(self):
        """Pass."""
        export_schema = self.GETARGS.get("export_schema", False)
        if export_schema:
            self._stream.write({"schemas": self.schemas_final()})


class JsonStream:
    """Wrap jsonstreams.Stream object."""

    def __init__(self, fd, **kwargs):
        """Wrap jsonstreams.Stream object."""
        self.__fd = fd

        encoder = kwargs.get("encoder", json.JSONEncoder)
        indent = kwargs.get("indent", 2)

        self.__inst = jsonstreams.Array(
            fd=self.__fd,
            indent=indent,
            baseindent=0,
            encoder=encoder(indent=indent),
            pretty=kwargs.get("pretty", True),
        )

        self.subobject = self.__inst.subobject
        self.subarray = self.__inst.subarray

    def close(self):
        """Close the root element and print a message."""
        self.__inst.close()

    def write(self, *args, **kwargs):
        """Write values into the stream."""
        self.__inst.write(*args, **kwargs)
