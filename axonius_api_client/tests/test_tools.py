# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import axonius_api_client


def test_schemehostport443():
    """Test."""
    u = axonius_api_client.tools.UrlParser('https://host:443/blah')
    assert u.hostname == 'host'
    assert u.port == 443
    assert u.scheme == 'https'
    assert u.parsed.path == '/blah'
    assert u.url_full == 'https://host:443/blah'
    assert u.url == 'https://host:443'
    assert u.parsed.path in format(u)
    assert u.parsed.path in repr(u)


def test_schemehost_noport443():
    """Test."""
    u = axonius_api_client.tools.UrlParser('https://host')
    assert u.hostname == 'host'
    assert u.port == 443
    assert u.scheme == 'https'


def test_host_noschemeport():
    """Test."""
    exc = axonius_api_client.exceptions.PackageError
    match = 'no \'port\''
    with pytest.raises(exc, match=match):
        axonius_api_client.tools.UrlParser('host')


def test_unknownschemehost_noport():
    """Test."""
    exc = axonius_api_client.exceptions.PackageError
    match = 'no \'port\''
    with pytest.raises(exc, match=match):
        axonius_api_client.tools.UrlParser('httpx://host')


def test_hostport443_withslash():
    """Test."""
    u = axonius_api_client.tools.UrlParser('host:443/')
    assert u.hostname == 'host'
    assert u.port == 443
    assert u.scheme == 'https'


def test_hostport443_noscheme():
    """Test."""
    u = axonius_api_client.tools.UrlParser('host:443')
    assert u.hostname == 'host'
    assert u.port == 443
    assert u.scheme == 'https'


def test_hostport80_noscheme():
    """Test."""
    u = axonius_api_client.tools.UrlParser('host:80')
    assert u.hostname == 'host'
    assert u.port == 80
    assert u.scheme == 'http'


def test_schemehost_noport80():
    """Test."""
    u = axonius_api_client.tools.UrlParser('http://host')
    assert u.hostname == 'host'
    assert u.port == 80
    assert u.scheme == 'http'
