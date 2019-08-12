# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from .. import exceptions, tools, constants

LOG = logging.getLogger(__name__)


def find_adapter(name, known=None):
    """Find an adapter by name.

    Args:
        name (:obj:`str`):
            Name of adapter to find.
        known (:obj:`list` of :obj:`str`, optional):
            List of known adapter names.

            Defaults to: None.

    Notes:
        If known is None, this will just ensure name ends with '_adapter'.

    Raises:
        :exc:`exceptions.UnknownError`: If name can not be found in known.

    Returns:
        :obj:`str`

    """
    postfix = "_adapter"
    name = name if name.endswith(postfix) else name + postfix

    if not known:
        found = name
    elif name in known:
        found = known[known.index(name)]
    else:
        known = tools.rstrip(obj=known, postfix=postfix)
        raise exceptions.UnknownError(
            value=name,
            known=known,
            reason_msg="adapter by name",
            valid_msg="adapter names",
        )

    msg = "Resolved adapter name {name!r} to {found!r}"
    msg = msg.format(name=name, found=found)
    LOG.debug(msg)

    return found


def find_field(name, adapter, fields=None):
    """Find a field for a given adapter.

    Args:
        name (:obj:`str`):
            Name of field to find.
        adapter (:obj:`str`):
            Name of adapter to look for field in.
            If 'generic' look for the field in generic fields.
        fields (:obj:`dict`, optional):
            Return from
            :meth:`axonius_api_client.api.interfaces.UserDeviceModel.get_fields`.

            Defaults to: None.

    Notes:
        If adapter 'generic', ensure name begins with
        :attr:`axonius_api_client.constants.GENERIC_FIELD_PREFIX`,
        otherwise ensure name begins with
        :attr:`axonius_api_client.constants.ADAPTER_FIELD_PREFIX`.

        If fields is None, we can't validate that the field exists, so we just ensure
        the name is fully qualified.

        If name in "all" or prefix, returns prefix.

    Raises:
        :exc:`exceptions.UnknownError`:
            If fields is not None and name can not be found in fields.

    Returns:
        :obj:`str`

    """
    if adapter == "generic":
        prefix = constants.GENERIC_FIELD_PREFIX
        container = fields["generic"] if fields else None
    else:
        known_adapters = list(fields["specific"].keys()) if fields else None
        adapter = find_adapter(name=adapter, known=known_adapters)
        prefix = constants.ADAPTER_FIELD_PREFIX.format(adapter_name=adapter)
        container = fields["specific"][adapter] if fields else None

    if not name.startswith(prefix):
        fq_name = ".".join([x for x in [prefix, name] if x])
    else:
        fq_name = name

    found = None

    if not container:
        found = name if name in ["adapters", "labels"] else fq_name
    else:
        known = [x["name"] for x in container]

        for check in [name, fq_name]:
            if check in ["all", prefix]:
                found = prefix
                break
            if check in known:
                found = known[known.index(check)]
                break

    if not found:
        known = tools.lstrip(obj=known, prefix=prefix + ".")
        known += ["all", prefix]
        raise exceptions.UnknownError(
            value=name,
            known=known,
            reason_msg="adapter {adapter} by field".format(adapter=adapter),
            valid_msg="field names",
        )

    msg = "Resolved {adapter!r} field name {name!r} to {found!r}"
    msg = msg.format(adapter=adapter, name=name, found=found)
    LOG.debug(msg)

    return found


def validate_fields(known_fields, **fields):
    """Validate provided fields are valid.

    Args:
        known_fields (:obj:`dict`):
            Known fields from
            :meth:`axonius_api_client.api.interfaces.UserDeviceModel.get_fields`.
        **fields: Fields to validate.
            * generic=['f1', 'f2'] for generic fields.
            * adapter=['f1', 'f2'] for adapter specific fields.

    Notes:
        This will try to use known_fields to validate the device
        fields, but if known_fields is empty it will just ensure the fields are
        fully qualified.

        * generic=['field1'] => ['specific_data.data.field1']
        * adapter=['field1'] =>['adapters_data.adapter_name.field1']

    Returns:
        :obj:`list` of :obj:`str`

    """
    validated_fields = []

    for name, afields in fields.items():
        if not isinstance(afields, (tuple, list)):
            continue
        for field in afields:
            field = find_field(name=field, fields=known_fields, adapter=name)
            if field not in validated_fields:
                validated_fields.append(field)

    msg = "Resolved fields {fields} to {validated_fields}"
    msg = msg.format(fields=fields, validated_fields=validated_fields)
    LOG.debug(msg)
    return validated_fields


def check_max_page_size(page_size):
    """Check if page size is over :data:`axonius_api_client.constants.MAX_PAGE_SIZE`.

    Args:
        page_size (:obj:`int`):
            Page size to check.

    Raises:
        :exc:`exceptions.ApiError`

    """
    if page_size > constants.MAX_PAGE_SIZE:
        msg = "Page size {page_size} is over maximum page size {max_size}"
        msg = msg.format(page_size=page_size, max_size=constants.MAX_PAGE_SIZE)
        raise exceptions.ApiError(msg)
