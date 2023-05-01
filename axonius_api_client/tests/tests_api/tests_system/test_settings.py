# -*- coding: utf-8 -*-
"""Test suite."""

# import os
# import subprocess

import pytest

from axonius_api_client.projects import cert_human
from axonius_api_client.api.json_api.generic import ApiBase
from axonius_api_client.api.json_api.system_settings import CertificateDetails
from axonius_api_client.exceptions import ApiError, NotFoundError

GUI_SECTION_WITH_SUBS = "system_settings"
GUI_SECTION_NO_SUBS = "mutual_tls_settings"
GUI_NON_SUB_SECTION = "exactSearch"
GUI_SUB_SECTION = "timeout_settings"
GUI_SUB_KEYS = ["disable_remember_me", "enabled", "timeout"]


class SettingsBasePublic:
    def val_schemas(self, schemas, config):
        for name, schema in schemas.items():
            assert schema["name"] == name
            assert schema["name"] in config
            assert isinstance(schema["required"], bool)

    def val_sub_section(self, name, meta, settings):
        assert isinstance(meta, dict) and meta
        assert meta["settings_title"] == settings["settings_title"]
        assert meta["name"] == name
        assert isinstance(meta["title"], str)
        assert isinstance(meta["schemas"], dict) and meta["schemas"]
        # pre-4.3 sub section "login_settings" of "system_settings" (GUI SettingsUpdate)
        # has its own sub section ldap_login
        assert isinstance(meta["sub_sections"], dict)  # and not meta["sub_sections"]
        assert isinstance(meta["parent_name"], str) and meta["parent_name"]
        assert isinstance(meta["parent_title"], str) and meta["parent_title"]

        assert isinstance(meta["config"], dict)

        # pre-4.3 sub sections exist so config items can be dicts
        # for k, v in meta["config"].items():
        #     assert not isinstance(v, dict)

        self.val_schemas(schemas=meta["schemas"], config=meta["config"])

    def val_section(self, name, meta, settings):
        assert isinstance(meta, dict) and meta
        assert meta["settings_title"] == settings["settings_title"]
        assert meta["name"] == name
        assert isinstance(meta["title"], str) and meta["title"]
        assert isinstance(meta["schemas"], dict) and meta["schemas"]
        assert isinstance(meta["sub_sections"], dict)
        assert isinstance(meta["parent_name"], str) and not meta["parent_name"]
        assert isinstance(meta["parent_title"], str) and not meta["parent_title"]

        assert isinstance(meta["config"], dict)

        self.val_schemas(schemas=meta["schemas"], config=meta["config"])
        for sub_name, sub_meta in meta["sub_sections"].items():
            self.val_sub_section(name=sub_name, meta=sub_meta, settings=settings)

    def test_get(self, apiobj):
        settings = apiobj.get()
        assert isinstance(settings, dict)

        assert isinstance(settings["settings_title"], str) and settings["settings_title"]
        assert isinstance(settings["sections"], dict) and settings["sections"]
        assert isinstance(settings["config"], dict) and settings["config"]

        for name, meta in settings["sections"].items():
            self.val_section(name=name, meta=meta, settings=settings)
            assert name in settings["config"]


class TestSettingsGui(SettingsBasePublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_settings_gui):
        return api_settings_gui

    def test_get_section_full_config_true(self, apiobj):
        result = apiobj.get_section(section=GUI_SECTION_WITH_SUBS, full_config=True)
        assert isinstance(result, dict)
        assert "full_config" in result

    def test_get_sub_section_full_config_true(self, apiobj):
        result = apiobj.get_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION, full_config=True
        )
        assert isinstance(result, dict)
        assert "full_config" in result

    def test_get_section_full_config_false(self, apiobj):
        result = apiobj.get_section(section=GUI_SECTION_WITH_SUBS, full_config=False)
        assert isinstance(result, dict)
        assert "full_config" not in result

    def test_get_sub_section_full_config_false(self, apiobj):
        result = apiobj.get_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION, full_config=False
        )
        assert isinstance(result, dict)
        assert "full_config" not in result

    def test_get_section_error(self, apiobj):
        with pytest.raises(NotFoundError) as exc:
            apiobj.get_section(section="badwolf")
        assert "not found in" in str(exc.value)

    def test_get_sub_section_error(self, apiobj):
        with pytest.raises(NotFoundError) as exc:
            apiobj.get_sub_section(section=GUI_SECTION_WITH_SUBS, sub_section="badwolf")
        assert "not found in under" in str(exc.value)
        assert "Sub Section Name" in str(exc.value)

    def test_get_sub_section_no_subsections(self, apiobj):
        with pytest.raises(ApiError) as exc:
            apiobj.get_sub_section(section=GUI_SECTION_NO_SUBS, sub_section="badwolf")
        assert "has no sub sections" in str(exc.value)

    def test_update_section(self, apiobj):
        old_section = apiobj.get_section(section=GUI_SECTION_WITH_SUBS)
        old_config = old_section["config"]
        old_value = old_config[GUI_NON_SUB_SECTION]

        update_value = not old_value

        new_section_args = {GUI_NON_SUB_SECTION: update_value}
        new_section = apiobj.update_section(section=GUI_SECTION_WITH_SUBS, **new_section_args)
        new_value = new_section["config"][GUI_NON_SUB_SECTION]
        assert new_value == update_value and old_value != new_value

        reset_section_args = {GUI_NON_SUB_SECTION: old_value}
        reset_section = apiobj.update_section(section=GUI_SECTION_WITH_SUBS, **reset_section_args)
        reset_value = reset_section["config"][GUI_NON_SUB_SECTION]
        assert reset_value == old_value and reset_value != new_value

    def test_update_sub_section(self, apiobj):
        old_section = apiobj.get_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION
        )
        sub_key = GUI_SUB_KEYS[0]
        old_config = old_section["config"]
        old_value = old_config[sub_key]
        update_value = old_value + 1

        new_section_args = {sub_key: update_value}
        new_section = apiobj.update_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION, **new_section_args
        )
        new_value = new_section["config"][sub_key]
        assert new_value == update_value and old_value != new_value

        reset_section_args = {sub_key: old_value}
        reset_section = apiobj.update_sub_section(
            section=GUI_SECTION_WITH_SUBS, sub_section=GUI_SUB_SECTION, **reset_section_args
        )
        reset_value = reset_section["config"][sub_key]
        assert reset_value == old_value and reset_value != new_value


class TestSettingsGlobal(SettingsBasePublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_settings_global):
        return api_settings_global

    @staticmethod
    def check_ca_config(config):
        assert isinstance(config, dict)
        assert isinstance(config["ca_files"], list)
        assert all([isinstance(x, dict) for x in config["ca_files"]])

    @staticmethod
    def check_chain(chain):
        assert isinstance(chain, list) and chain
        assert all([isinstance(x, cert_human.Cert) for x in chain])

    @staticmethod
    def get_ca_filenames(config):
        return [x["filename"] for x in config["ca_files"]]

    @pytest.mark.datafiles("certs/server_rsa.crt.pem")
    def test_file_upload_path(self, apiobj, datafiles):
        datafile = datafiles[0]
        data = apiobj.file_upload_path(field_name="x", path=datafile)
        assert isinstance(data, ApiBase)
        assert data.filename == datafile.name

    @pytest.mark.datafiles("certs/server_rsa.crt.pem")
    def test_ca_add_non_ca(self, apiobj, datafiles):
        datafile = datafiles[0]
        with pytest.raises(cert_human.exceptions.InvalidCertError):
            apiobj.ca_add_path(path=str(datafile))

    @pytest.mark.datafiles("certs/ca_ec.crt.pem")
    def test_ca_add_remove_path(self, apiobj, datafiles):
        datafile = datafiles[0]
        path, config = apiobj.ca_add_path(path=str(datafile))
        self.check_ca_config(config)
        assert path == datafile
        assert datafile.name in self.get_ca_filenames(config)
        assert config["enabled"] is True

        ca_strs = apiobj.cas_to_str(config)
        assert isinstance(ca_strs, list) and ca_strs
        assert all([isinstance(x, str) for x in ca_strs])
        assert "is enabled: True" in ca_strs[0]

        config = apiobj.ca_remove(filename=path.name)
        self.check_ca_config(config)
        assert datafile.name not in self.get_ca_filenames(config)

    def test_ca_remove_not_found(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.ca_remove(filename="badwolf_sney")

    def test_ca_enable_true(self, apiobj):
        config = apiobj.ca_enable(True)
        self.check_ca_config(config)
        assert config["enabled"] is True

    def test_ca_enable_false(self, apiobj):
        config = apiobj.ca_enable(False)
        self.check_ca_config(config)
        assert config["enabled"] is False

    def test_gui_cert_info(self, apiobj):
        data = apiobj.gui_cert_info()
        assert isinstance(data, CertificateDetails)
        assert "Issued To: " in str(data)

    def test_gui_cert_reset_false(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.gui_cert_reset()

    def test_gui_cert_reset_true(self, apiobj):
        chain = apiobj.gui_cert_reset(True)
        self.check_chain(chain)

    @pytest.mark.datafiles("certs/server_rsa.crt.pem", "certs/server_rsa.key")
    def test_gui_cert_update(self, apiobj, datafiles):
        path_cert, path_key = datafiles
        chain = apiobj.gui_cert_update_path(
            cert_file_path=path_cert, key_file_path=path_key, host="axonius"
        )
        self.check_chain(chain)

        cert_uploaded = apiobj._cert_uploaded()
        assert isinstance(cert_uploaded, dict)
        assert cert_uploaded["enabled"] is True

        chain = apiobj.gui_cert_reset(True)
        self.check_chain(chain)

    def test_csr_cancel(self, apiobj):
        current_csr = apiobj.csr_get(error=False)
        data = apiobj.csr_cancel(error=False)
        if current_csr is None:
            assert data is None
        else:
            assert isinstance(data, cert_human.CertRequest)

        with pytest.raises(ApiError):
            apiobj.csr_cancel(error=True)

    def test_csr_create(self, apiobj):
        cname = "axonius_csr.com"
        csr = apiobj.csr_create(common_name=cname, overwrite=True)
        assert isinstance(csr, cert_human.CertRequest)
        assert csr.section_subject["common_name"] == cname

        with pytest.raises(ApiError):
            apiobj.csr_create(common_name=cname, overwrite=False)

        csr_get = apiobj.csr_get()
        assert isinstance(csr_get, cert_human.CertRequest)
        assert csr_get.section_subject["common_name"] == cname

        csr_cancel = apiobj.csr_cancel()
        assert isinstance(csr_cancel, cert_human.CertRequest)
        assert csr_cancel.section_subject["common_name"] == cname

    def test_configure_destroy(self, apiobj):
        ret = apiobj.configure_destroy(enabled=True, destroy=True, reset=True)
        assert ret["config"] == {
            "enable_destroy": True,
            "enable_factory_reset": True,
            "enabled": True,
            "minimize_output": False,
        }
        ret = apiobj.configure_destroy(enabled=False, destroy=False, reset=False)
        assert ret["config"] == {
            "enable_destroy": False,
            "enable_factory_reset": False,
            "enabled": False,
            "minimize_output": False,
        }
        """
        {
            "settings_title": "Global SettingsUpdate",
            "name": "api_settings",
            "title": "API SettingsUpdate",
            "schemas": {
                "enabled": {
                    "name": "enabled",
                    "title": "Enable advanced API settings",
                    "type": "bool",
                    "required": True,
                },
                "enable_destroy": {
                    "name": "enable_destroy",
                    "title": "Enable API destroy endpoints",
                    "type": "bool",
                    "required": True,
                },
                "enable_factory_reset": {
                    "name": "enable_factory_reset",
                    "title": "Enable factory reset endpoints",
                    "type": "bool",
                    "required": True,
                },
                "minimize_output": {
                    "name": "minimize_output",
                    "title": "Shorten assets response field names",
                    "type": "bool",
                    "required": True,
                },
            },
            "sub_sections": {},
            "parent_name": "",
            "parent_title": "",
            "config": {
                "enable_destroy": True,
                "enable_factory_reset": True,
                "enabled": True,
                "minimize_output": False,
            },
        }
        """


class TestSettingsLifecycle(SettingsBasePublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_settings_lifecycle):
        return api_settings_lifecycle


class TestSettingsIdentityProviders(SettingsBasePublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_settings_ip):
        return api_settings_ip
