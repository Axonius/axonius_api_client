# -*- coding: utf-8 -*-
"""Test suite."""
import datetime

import pytest
from axonius_api_client.api.json_api.folders import (
    Folder,
    FolderBase,
    FolderPaths,
    RootFolders,
    RootNames,
)
from axonius_api_client.api.json_api.saved_queries import SavedQuery
from axonius_api_client.exceptions import FolderNotFoundError, NotAllowedError


class FoldersBase:
    @pytest.fixture(scope="class")
    def root_folders(self, api_client):
        data = api_client.folders.get()
        return data


class TestRootFolders(FoldersBase):
    @pytest.mark.parametrize(
        "value, exp",
        [
            [
                " / x / a1",
                ["", "x", "a1"],
            ],
            [
                "a/b/",
                ["a", "b", ""],
            ],
        ],
    )
    def test__split_path(self, root_folders, value, exp):
        ret = root_folders._split_path(value)
        assert ret == exp

    def test_get(self, root_folders):
        assert isinstance(root_folders, RootFolders)
        assert root_folders.root_folders == root_folders

    def test__str__(self, root_folders):
        assert str(root_folders)

    def test__repr__(self, root_folders):
        assert repr(root_folders)

    def test_property_depth(self, root_folders):
        assert root_folders.depth == RootFolders.depth

    def test_property_id(self, root_folders):
        assert root_folders.id == RootFolders._id

    def test_property_name(self, root_folders):
        assert root_folders.name == RootFolders.name

    def test_property_root_type(self, root_folders):
        assert root_folders.root_type == RootFolders.root_type

    def test_property_parent_id(self, root_folders):
        assert root_folders.parent_id == RootFolders.parent_id

    def test_property_root_id(self, root_folders):
        assert root_folders.root_id == RootFolders.root_id

    def test_property_created_by(self, root_folders):
        assert root_folders.created_by == RootFolders.created_by

    def test_property_path(self, root_folders):
        assert root_folders.path == RootFolders.path

    def test_property_read_only(self, root_folders):
        assert root_folders.read_only == RootFolders.read_only

    def test_property_created_at(self, root_folders):
        assert root_folders.created_at == RootFolders.created_at

    def test_property_updated_at(self, root_folders):
        assert root_folders.updated_at == RootFolders.updated_at

    def test_property_children_ids(self, root_folders):
        assert root_folders.children_ids
        assert isinstance(root_folders.children_ids, list)
        for x in root_folders.children_ids:
            assert isinstance(x, str)

    def test_property_children(self, root_folders):
        assert root_folders.children
        assert isinstance(root_folders.children, list)
        for x in root_folders.children:
            assert isinstance(x, dict)

    def test_property_is_public(self, root_folders):
        assert root_folders.is_public is False

    def test_property_is_private(self, root_folders):
        assert root_folders.is_private is False

    def test_property_is_asset_scope(self, root_folders):
        assert root_folders.is_asset_scope is False

    def test_property_root_public(self, root_folders):
        assert isinstance(root_folders.root_public, Folder)
        assert root_folders.root_public.name == RootNames.public.value
        assert root_folders.root_public.depth == 1

    def test_property_root_private(self, root_folders):
        assert isinstance(root_folders.root_private, Folder)
        assert root_folders.root_private.name == RootNames.private.value
        assert root_folders.root_private.depth == 1

    def test_property_root_asset_scope(self, root_folders, api_client):
        if api_client.data_scopes.is_feature_enabled:
            assert isinstance(root_folders.root_asset_scope, Folder)
            assert root_folders.root_asset_scope.name == RootNames.asset_scope.value
            assert root_folders.root_asset_scope.depth == 1
        else:
            with pytest.raises(FolderNotFoundError):
                root_folders.root_asset_scope

    def test_property_count(self, root_folders):
        assert root_folders.count >= 2

    def test_property_count_subfolders(self, root_folders):
        assert root_folders.count_subfolders > 0

    def test_property_count_objects(self, root_folders):
        assert root_folders.count_objects == 0

    def test_property_count_queries(self, root_folders):
        assert root_folders.count_queries == 0

    def test_property_count_recursive(self, root_folders):
        assert root_folders.count_recursive >= 2

    def test_property_count_recursive_subfolders(self, root_folders):
        assert root_folders.count_recursive_subfolders >= root_folders.count_subfolders

    def test_property_count_recursive_objects(self, root_folders):
        assert root_folders.count_recursive_objects >= root_folders.count_objects

    def test_property_count_recursive_queries(self, root_folders):
        assert root_folders.count_recursive_queries >= root_folders.count_queries

    def test_property_root(self, root_folders):
        assert root_folders.root is None

    def test_property_parent(self, root_folders):
        assert root_folders.parent is None

    def test_property_all_folders_by_id(self, root_folders):
        assert root_folders.all_folders_by_id
        assert isinstance(root_folders.all_folders_by_id, dict)
        for k, v in root_folders.all_folders_by_id.items():
            assert isinstance(k, str) and k.strip()
            assert isinstance(v, FolderBase)

    def test_property_all_folders_by_id_summary(self, root_folders):
        assert root_folders.all_folders_by_id_summary
        assert isinstance(root_folders.all_folders_by_id_summary, list)
        for x in root_folders.all_folders_by_id_summary:
            assert isinstance(x, str)

    def test_property_subfolders(self, root_folders):
        assert root_folders.subfolders
        assert isinstance(root_folders.subfolders, list)
        for x in root_folders.subfolders:
            assert isinstance(x, Folder)
            assert x.depth == 1
            assert x.root == root_folders
            assert x.parent == root_folders

    def test_property_subfolders_summary(self, root_folders):
        assert root_folders.subfolders_summary
        assert isinstance(root_folders.subfolders_summary, list)
        for x in root_folders.subfolders_summary:
            assert isinstance(x, str)

    def test_property_subfolders_by_name(self, root_folders):
        assert root_folders.subfolders_by_name
        assert isinstance(root_folders.subfolders_by_name, dict)
        for k, v in root_folders.subfolders_by_name.items():
            assert isinstance(k, str) and k.strip()
            assert isinstance(v, Folder)

    def test_property_subfolders_by_id_recursive(self, root_folders):
        assert root_folders.subfolders_by_id_recursive
        assert isinstance(root_folders.subfolders_by_id_recursive, dict)
        for k, v in root_folders.subfolders_by_id_recursive.items():
            assert isinstance(k, str) and k.strip()
            assert isinstance(v, Folder)

    def test_property_subfolders_by_path_recursive(self, root_folders):
        assert root_folders.subfolders_by_path_recursive
        assert isinstance(root_folders.subfolders_by_path_recursive, dict)
        for k, v in root_folders.subfolders_by_path_recursive.items():
            assert isinstance(k, str) and RootFolders.sep in k
            assert isinstance(v, Folder)

    def test_property_refresh_dt(self, root_folders):
        assert isinstance(root_folders.refresh_dt, datetime.datetime)

    def test_property_refresh_elapsed(self, root_folders):
        assert isinstance(root_folders.refresh_elapsed, float)

    def test_get_tree(self, root_folders):
        data = root_folders.get_tree()
        assert len(data) > 1
        assert isinstance(data, list)
        for x in data:
            assert isinstance(x, str) and x.strip()

    def test_get_tree_max_depth_0(self, root_folders):
        data = root_folders.get_tree(max_depth=0)
        assert len(data) == 1
        assert "recursive" in data[0]

    def test_get_tree_max_depth_1(self, root_folders):
        data = root_folders.get_tree(max_depth=1)
        data_txt = "\n".join(data)
        assert len(data) >= root_folders.count
        assert "recursive" in data_txt

    def test_get_tree_include_details(self, root_folders):
        data = root_folders.get_tree(include_details=True)
        assert len(data) >= root_folders.count
        assert "id=" in data[0]

    def test_get_tree_include_objects(self, root_folders):
        data = root_folders.get_tree(include_objects=True)
        data_txt = "\n".join(data)
        assert len(data) >= root_folders.count_recursive
        assert SavedQuery.__name__ in data_txt

    def test_get_tree_include_objects_include_details(self, root_folders):
        data = root_folders.get_tree(include_details=True, include_objects=True)
        data_txt = "\n".join(data)
        assert len(data) >= root_folders.count_recursive
        assert SavedQuery.__name__ in data_txt

    def test_get_tree_include_objects_include_details_max_depth_3(self, root_folders):
        data = root_folders.get_tree(max_depth=3, include_details=True, include_objects=True)
        data_txt = "\n".join(data)
        assert len(data) >= root_folders.count
        assert SavedQuery.__name__ in data_txt
        assert "recursive" in data_txt

    def test_find_self(self, root_folders):
        found = root_folders.find(root_folders)
        assert found == root_folders

    def test_find_root_path(self, root_folders):
        found = root_folders.find(root_folders.sep)
        assert found == root_folders

    def test_find_root_id(self, root_folders):
        found = root_folders.find(root_folders._id)
        assert found == root_folders

    @pytest.mark.parametrize("refresh", [True, "yes"])
    def test_refresh_true(self, root_folders, refresh):
        refresh_dt = root_folders.refresh_dt
        removed = root_folders.folders.pop()

        root_folders.refresh(refresh=refresh)

        assert refresh_dt != root_folders.refresh_dt
        assert removed in root_folders.folders

    @pytest.mark.parametrize("refresh", [False, "no"])
    def test_refresh_false(self, root_folders, refresh):
        refresh_dt = root_folders.refresh_dt
        removed = root_folders.folders.pop()

        root_folders.refresh(refresh=refresh)

        assert refresh_dt == root_folders.refresh_dt
        assert removed not in root_folders.folders
        root_folders.folders.append(removed)

    @pytest.mark.parametrize("refresh,seconds", [[2, 3], ["4", 5], [6.6, 7], ["8.8", 9]])
    def test_refresh_num_true(self, root_folders, refresh, seconds):
        delta = datetime.timedelta(seconds=seconds)
        root_folders.refresh_dt = root_folders.refresh_dt - delta
        refresh_dt = root_folders.refresh_dt
        removed = root_folders.folders.pop()

        root_folders.refresh(refresh=refresh)

        assert refresh_dt != root_folders.refresh_dt
        assert removed in root_folders.folders

    @pytest.mark.parametrize("refresh,seconds", [[10, 1], ["20", 1], [30.30, 1], ["40.40", 1]])
    def test_refresh_num_false(self, root_folders, refresh, seconds):
        delta = datetime.timedelta(seconds=seconds)
        root_folders.refresh_dt = root_folders.refresh_dt - delta
        refresh_dt = root_folders.refresh_dt
        removed = root_folders.folders.pop()

        root_folders.refresh(refresh=refresh)

        assert refresh_dt == root_folders.refresh_dt
        assert removed not in root_folders.folders
        root_folders.folders.append(removed)

    def test_find_subfolder_valid(self, root_folders):
        folder = root_folders.find_subfolder(RootNames.public.value)
        assert isinstance(folder, Folder)
        assert folder.name == RootNames.public.value

    def test_find_subfolder_invalid(self, root_folders):
        with pytest.raises(FolderNotFoundError):
            root_folders.find_subfolder("badwolf")

    def test_find_by_path_absolute_valid(self, root_folders):
        folder = root_folders.find_by_path(f"{root_folders.sep}{RootNames.public.value}")
        assert isinstance(folder, Folder)
        assert folder.name == RootNames.public.value

    def test_find_by_path_absolute_invalid(self, root_folders):
        with pytest.raises(FolderNotFoundError):
            root_folders.find_by_path("{root_folders.sep}badwolf")

    def test_find_by_path_relative_valid(self, root_folders):
        folder = root_folders.find_by_path(f"{RootNames.public.value}")
        assert isinstance(folder, Folder)
        assert folder.name == RootNames.public.value

    def test_find_by_path_relative_invalid(self, root_folders):
        with pytest.raises(FolderNotFoundError):
            root_folders.find_by_path("badwolf")

    def test_create(self, root_folders):
        with pytest.raises(NotAllowedError):
            root_folders.create("badwolf")

    def test_delete(self, root_folders):
        with pytest.raises(NotAllowedError):
            root_folders.delete("badwolf")

    def test_delete_root(self, root_folders):
        with pytest.raises(NotAllowedError):
            root_folders.root_public.delete("badwolf")


class TestFolder(FoldersBase):
    def test_find_self(self, root_folders):
        folder = root_folders.root_public
        found = folder.find(folder)
        assert found == folder

    def test_property_parent(self, root_folders):
        folder = root_folders.find(FolderPaths.predefined.value)
        assert folder.parent == folder.root_public

    def test_property_root(self, root_folders):
        folder = root_folders.find(FolderPaths.predefined.value)
        assert folder.root == folder.root_public
