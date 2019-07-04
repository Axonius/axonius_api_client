# -*- coding: utf-8 -*-
"""Conf for py.test."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import re


@pytest.fixture
def log_check():
    """Pass."""
    # moo
    def _log_check(caplog, entries):
        """Pass."""
        msgs = [rec.message for rec in caplog.records]
        for entry in entries:
            if not any(re.search(entry, m) for m in msgs):
                error = "Did not find entry in log: {!r}\nAll entries:\n{}"
                error = error.format(entry, "\n".join(msgs))
                raise Exception(error)

    return _log_check
