# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.assets."""
import pytest


def load_test_data(apiobj):
    """Pass."""
    apiobj.TEST_DATA = getattr(apiobj, "TEST_DATA", {})

    if not apiobj.TEST_DATA.get("fields_map"):
        apiobj.TEST_DATA["fields_map"] = fields_map = apiobj.fields.get()

    if not apiobj.TEST_DATA.get("assets"):
        apiobj.TEST_DATA["assets"] = apiobj.get(max_rows=4000, fields_map=fields_map)

    return apiobj


class LabelsPrivate:
    """Pass."""

    def test_private_get(self, apiobj):
        """Pass."""
        fields = apiobj.labels._get()
        assert isinstance(fields, list)
        for x in fields:
            assert isinstance(x, str)

    def test_private_add_get_remove(self, apiobj):
        """Pass."""
        labels = ["badwolf1", "badwolf2"]

        # get a single asset to add a label to
        asset = apiobj.TEST_DATA["assets"][0]
        asset_id = asset["internal_axon_id"]

        # add the label to the asset
        add_label_result = apiobj.labels._add(labels=labels, ids=[asset_id])
        assert add_label_result == 1

        # re-get the asset and check that it has the label
        assets_added = apiobj.get_by_values(
            values=labels,
            field="labels",
            fields="labels",
            fields_map=apiobj.TEST_DATA["fields_map"],
        )
        assets_added_ids = [x["internal_axon_id"] for x in assets_added]
        assert asset_id in assets_added_ids

        # check the each label has been added
        for x in assets_added:
            for label in labels:
                assert label in x["labels"]

        # check that the label is in all the labels on the system
        all_labels_post_add = apiobj.labels._get()
        assert isinstance(all_labels_post_add, list)

        for label in all_labels_post_add:
            assert isinstance(label, str)

        for label in labels:
            assert label in all_labels_post_add

        # remove the label from an asset
        remove_label_result = apiobj.labels._remove(labels=labels, ids=assets_added_ids)
        assert remove_label_result >= 1

        # re-get the asset and check that it has the label
        assets_removed = apiobj.get_by_values(
            values=labels,
            field="labels",
            fields="labels",
            fields_map=apiobj.TEST_DATA["fields_map"],
        )
        assert not assets_removed

        # check that the label is not in all the labels on the system
        all_labels_post_remove = apiobj.labels._get()
        assert isinstance(all_labels_post_remove, list)

        for label in labels:
            assert label not in all_labels_post_remove


class LabelsPublic:
    """Pass."""

    def test_get(self, apiobj):
        """Pass."""
        fields = apiobj.labels.get()
        assert isinstance(fields, list)
        for x in fields:
            assert isinstance(x, str)

    def test_add_get_remove(self, apiobj):
        """Pass."""
        labels = ["badwolf1", "badwolf2"]

        # get a single asset to add a label to
        asset = apiobj.TEST_DATA["assets"][0]
        asset_id = asset["internal_axon_id"]

        # add the label to the asset
        add_label_result = apiobj.labels.add(labels=labels, rows=[asset])
        assert add_label_result == 1

        # re-get the asset and check that it has the label
        assets_added = apiobj.get_by_values(
            values=labels,
            field="labels",
            fields="labels",
            fields_map=apiobj.TEST_DATA["fields_map"],
        )
        assets_added_ids = [x["internal_axon_id"] for x in assets_added]
        assert asset_id in assets_added_ids

        # check the each label has been added
        for x in assets_added:
            for label in labels:
                assert label in x["labels"]

        # check that the label is in all the labels on the system
        all_labels_post_add = apiobj.labels.get()
        assert isinstance(all_labels_post_add, list)

        for label in all_labels_post_add:
            assert isinstance(label, str)

        for label in labels:
            assert label in all_labels_post_add

        # remove the label from an asset
        remove_label_result = apiobj.labels.remove(labels=labels, rows=assets_added)
        assert remove_label_result >= 1

        # re-get the asset and check that it has the label
        assets_removed = apiobj.get_by_values(
            values=labels,
            field="labels",
            fields="labels",
            fields_map=apiobj.TEST_DATA["fields_map"],
        )
        assert not assets_removed

        # check that the label is not in all the labels on the system
        all_labels_post_remove = apiobj.labels.get()
        assert isinstance(all_labels_post_remove, list)

        for label in labels:
            assert label not in all_labels_post_remove


class TestLabelsDevices(LabelsPrivate, LabelsPublic):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        """Pass."""
        return load_test_data(api_devices)


class TestLabelsUsers(LabelsPrivate, LabelsPublic):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        """Pass."""
        return load_test_data(api_users)
