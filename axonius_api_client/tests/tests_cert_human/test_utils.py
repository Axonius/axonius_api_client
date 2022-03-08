# -*- coding: utf-8 -*-
"""Test suite."""
import pytest
from axonius_api_client.cert_human import utils


class TestTypeStr:
    def test_max_len(self):
        exp = "type=<class 'str'>, length=50, value='xxxxxxxxxx...snip...'"
        data = utils.type_str(value="x" * 50, max_len=10)
        assert data == exp


class TestHumanKeyValue:
    def test_list(self):
        exp = "  - TEST                        : [1, 2, 3]"
        data = utils.human_key_value(key="TEST", value=[1, 2, 3])
        assert data == exp


class TestHumanKey:
    @pytest.mark.parametrize(
        "value, exp",
        (
            ("test_human_key", "Test Human Key"),
            ("TEST_HUMAN_KEY", "TEST HUMAN KEY"),
            ("test_ssl_caps", "Test SSL Caps"),
        ),
    )
    def test_variants(self, value, exp):
        data = utils.human_key(value=value)
        assert data == exp


class TestHumanDict:
    def test_multi(self):
        exp = [
            "  - Key With List               : ['value']",
            "  - Key With Str                : value",
            "  - Key With Lod Item #1:       ",
            "    - P1                        : 3",
            "    - P2                        : 4",
            "  - Key With Lod Item #2:       ",
            "    - P2                        : 4",
        ]
        data = utils.human_dict(
            value={
                "key_with_list": ["value"],
                "key_with_str": "value",
                "key_with_lod": [{"p1": 3, "p2": 4}, {"p2": 4}],
            }
        )
        assert data == exp


class TestCheckType:
    def test_none_bad(self):
        with pytest.raises(TypeError):
            utils.check_type(value=None, exp=str, allow_none=False)

    def test_none_ok(self):
        utils.check_type(value="xx", exp=(str, int))

    def test_bad_type(self):
        with pytest.raises(TypeError):
            utils.check_type(value=1, exp=str)


class TestGetSubcls:
    def test_get_subcls(self):
        class A:
            pass

        class B(A):
            pass

        class C(B):
            pass

        class D:
            pass

        exp = [B, C]
        notexp = [A, D]
        data = utils.get_subcls(cls=A)
        for i in exp:
            assert i in data
        for i in notexp:
            assert i not in data


class TestBytesToStr:
    def test_unstrict(self):
        exp = "C�"
        data = utils.bytes_to_str(value=b"\x43\x8e", strict=False)
        assert data == exp

    def test_strict(self):
        with pytest.raises(UnicodeDecodeError):
            utils.bytes_to_str(value=b"\x43\x8e", strict=True)


class TestB64ToBytes:
    def test_there_and_back_again(self):
        exp = "Q++/vQ=="
        data = utils.bytes_to_b64(value="C�")
        assert data == exp

        exp2 = b"C\xef\xbf\xbd"
        data2 = utils.b64_to_bytes(value=data)
        assert data2 == exp2

        exp3 = "43:EF:BF:BD"
        data3 = utils.b64_to_hex(value=data)
        assert data3 == exp3


class TestIntToHex:
    def test_valid(self):
        exp = "CC:D5:04:58:7E:1E:08:5"
        data = utils.int_to_hex(value=922481758243512453)
        assert data == exp


class TestStrStipToInt:
    def test_valid(self):
        exp = 24
        data = utils.str_strip_to_int(value="asd 24 ")
        assert data == exp


class TestBytesToHex:
    def test_valid(self):
        exp = "04:CE:E9:33:0D:04:53:6E:21:61:1F:CE:29:F0:F6:ED:42:01:34:A6:D2:D7:F0:82:CE:25"
        data = utils.bytes_to_hex(
            b"\x04\xce\xe93\r\x04Sn!a\x1f\xce)\xf0\xf6\xedB\x014\xa6\xd2\xd7\xf0\x82\xce%"
        )
        assert data == exp


class TestListify:
    """Test listify."""

    def test_dict_keys(self):
        """Simple test."""
        x = utils.listify(value={"x": 1, "y": 1}, dictkeys=True)
        assert x == ["x", "y"]

    def test_dict_notkeys(self):
        """Simple test."""
        x = utils.listify(value={"x": 1, "y": 1}, dictkeys=False)
        assert x == [{"x": 1, "y": 1}]

    def test_tuple(self):
        """Simple test."""
        x = utils.listify(value=(1, 2))
        assert x == [1, 2]

    def test_list(self):
        """Simple test."""
        x = utils.listify(value=[1, 2])
        assert x == [1, 2]

    def test_int(self):
        """Simple test."""
        x = utils.listify(value=1)
        assert x == [1]

    def test_str(self):
        """Simple test."""
        x = utils.listify(value="1")
        assert x == ["1"]

    def test_none(self):
        """Simple test."""
        x = utils.listify(value=None)
        assert x == []
