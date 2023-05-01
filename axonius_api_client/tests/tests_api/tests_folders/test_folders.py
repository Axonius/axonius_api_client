# -*- coding: utf-8 -*-
"""Test suite."""
import datetime

import pytest

from axonius_api_client.api.json_api import folders
from axonius_api_client.data import BaseEnum
from axonius_api_client.exceptions import (  # SearchZeroObjectsError,
    AlreadyExists,
    ApiWarning,
    AxonTypeError,
    ConfirmNotTrue,
    FolderAlreadyExistsError,
    FolderNotFoundError,
    NotAllowedError,
    ResponseNotOk,
    SavedQueryNotFoundError,
    SearchNoMatchesError,
    SearchNoObjectsError,
    SearchUnmatchedError,
)


class FolderBase:
    def cleanup(self, apiobj, folder):
        if isinstance(folder, list):
            for x in folder:
                self.cleanup(apiobj, x)
            return

        try:
            apiobj.delete(folder=folder, confirm=True, delete_subfolders=True, delete_objects=True)
        except FolderNotFoundError:
            pass


class FolderBaseQueries(FolderBase):
    @pytest.fixture(scope="class")
    def apiobj(self, request, api_client):
        return api_client.folders.queries

    @pytest.fixture(scope="class")
    def jsonapi_module(self):
        return folders.queries

    @pytest.fixture(scope="function")
    def created_obj(self, apiobj, api_client):
        root = apiobj.get()
        api_name = root.api_folders.__class__.__name__
        obj_name = f"badwolf obj for {api_name}"
        create_object_args = {"name": obj_name, "query_type": "devices"}

        try:
            created_obj = root.create_object(**create_object_args)
        except AlreadyExists as exc:
            existing_object = exc.obj
            existing_object.delete(confirm=True)
            created_obj = root.create_object(**create_object_args)

        yield created_obj

        # does not fail like enforcements, api will just silently ignore that its already deleted
        created_obj.delete(confirm=True)
        with pytest.raises(SavedQueryNotFoundError):
            api_client.devices.saved_query.get_by_multi(obj_name)


class FolderBaseEnforcements(FolderBase):
    @pytest.fixture(scope="class")
    def apiobj(self, request, api_client):
        return api_client.folders.enforcements

    @pytest.fixture(scope="class")
    def jsonapi_module(self):
        return folders.enforcements

    @pytest.fixture(scope="function")
    def created_obj(self, apiobj, api_client):
        root = apiobj.get()
        api_name = root.api_folders.__class__.__name__
        obj_name = f"badwolf obj for {api_name}"
        query_name = api_client.devices.saved_query.get(as_dataclass=True, row_stop=1, page_size=1)[
            0
        ].name
        create_object_args = {"name": obj_name}
        custom_args = {
            "query_name": query_name,
            "query_type": "devices",
            "main_action_name": f"badwolf action for {api_name}",
            "main_action_type": "create_notification",
        }
        create_object_args.update(custom_args)

        with pytest.warns(ApiWarning):
            try:
                created_obj = root.create_object(**create_object_args)
            except AlreadyExists as exc:
                existing_object = exc.obj
                existing_object.delete(confirm=True)
                created_obj = root.create_object(**create_object_args)

        yield created_obj

        with pytest.raises(ResponseNotOk) as exc:
            created_obj.delete(confirm=True)
        # 2023-04-21 error changed from "...was not found" to "No enforcement was deleted"
        assert "was not found" in str(exc.value) or "No enforcement was deleted" in str(exc.value)


class FolderBase:
    def test_search_objects(self, apiobj, created_obj):
        root = apiobj.get()
        api_name = root.api_folders.__class__.__name__
        folder_path = root.path_public.join_under(f"badwolf search objects for {api_name}")
        folder_path_copy = root.path_public.join_under("badwolf search objects copy")
        folder_path_move = root.path_public.join_under("badwolf search objects move")
        obj_fake_name = "F12 makes aliens see rainbows"

        self.cleanup(apiobj, [folder_path_copy, folder_path_move])

        try:
            folder = root.find(folder=folder_path)
        except FolderNotFoundError:
            folder = root.find(folder=folder_path, create=True)
        else:
            folder.delete(confirm=True, delete_objects=True, delete_subfolders=True)
            folder = root.find(folder=folder_path, create=True)

        try:
            apiobj.delete(
                folder=folder_path_move, confirm=True, delete_subfolders=True, delete_objects=True
            )
        except FolderNotFoundError:
            pass

        copied_obj = created_obj.copy(folder=folder)
        created_obj.delete(confirm=True)
        assert copied_obj.folder.id == folder.id
        objs = folder.search_objects(searches=copied_obj.name)
        assert copied_obj.name in [x.name for x in objs]
        assert len(objs) == 1

        # test_search_objects_unmatched_exc
        with pytest.raises(SearchUnmatchedError):
            folder.search_objects(searches=[copied_obj.name, obj_fake_name])

        objs_mismatch = folder.search_objects(
            searches=[copied_obj.name, obj_fake_name], error_unmatched=False
        )
        assert copied_obj.name in [x.name for x in objs_mismatch]
        assert len(objs_mismatch) == 1

        # test_search_objects_copy_self
        folder, objs_copied_same_folder = folder.search_objects_copy(searches="~.*")
        assert copied_obj.name not in [x.name for x in objs_copied_same_folder]
        assert len(objs_copied_same_folder) == 1
        for x in objs_copied_same_folder:
            assert x.folder.id == folder.id

        assert len(folder.get_objects()) == 2

        # test_search_objects_copy_other_folder
        folder_copy, objs_copied_other_folder = folder.search_objects_copy(
            searches="~.*", folder=folder_path_copy, create=True
        )
        assert len(objs_copied_other_folder) == 2
        assert len(folder_copy.get_objects()) == 2

        # test_search_objects_copy_move
        folder_move, objs_moved = folder.search_objects_move(
            searches="~.*", folder=folder_path_move
        )
        assert copied_obj.name in [x.name for x in objs_moved]
        assert len(objs_moved) == 2
        for x in objs_moved:
            assert x.folder.id == folder_move.id

        assert len(folder_move.get_objects()) == 2

        # test_search_objects_delete
        with pytest.raises(ConfirmNotTrue):
            folder_copy.search_objects_delete(searches="~.*")
        objs_deleted = folder_copy.search_objects_delete(searches="~.*", confirm=True)
        assert len(objs_deleted) == 2
        assert len(folder_copy.get_objects()) == 0

        folder_move.delete(confirm=True, delete_objects=True, delete_subfolders=True)
        folder_copy.delete(confirm=True, delete_objects=True, delete_subfolders=True)
        folder.delete(confirm=True, delete_objects=True, delete_subfolders=True)
        self.cleanup(apiobj, [folder, folder_move, folder_copy])

    def test_search_objects_no_matches(self, apiobj):
        root = apiobj.get()
        api_name = root.api_folders.__class__.__name__
        name = f"badwolf search objects no matches for {api_name}"
        folder = root.path_public.create(folder=name)
        obj_fake_name = "Windy portrait makes noise"
        with pytest.raises(SearchNoMatchesError):
            folder.search_objects(searches=obj_fake_name, error_no_objects=False)

        objs_nomatch = folder.search_objects(
            searches=obj_fake_name,
            error_unmatched=False,
            error_no_matches=False,
            error_no_objects=False,
        )
        assert not objs_nomatch
        folder.delete(confirm=True)

    def test_search_objects_no_objects(self, apiobj):
        root = apiobj.get()
        api_name = root.api_folders.__class__.__name__
        name = f"badwolf search objects no objects for {api_name}"
        folder = root.path_public.create(folder=name)
        obj_fake_name = "Elevators do not make good people"
        with pytest.raises(SearchNoObjectsError):
            folder.search_objects(searches=obj_fake_name)

        folder.delete(confirm=True)

    def test_delete_delete_objects(self, apiobj, created_obj, jsonapi_module):
        root = apiobj.get()
        api_name = root.api_folders.__class__.__name__

        name = f"badwolf delete include objects for {api_name}"
        path = root.path_public.join_under(name)
        folder = root.create(folder=path)

        created_obj = created_obj.move(folder=folder)
        assert created_obj.folder.id == folder.id

        with pytest.raises(NotAllowedError) as exc:
            folder.delete(confirm=True)
        assert "delete_objects is False" in str(exc.value)

        deleted = folder.delete(delete_objects=True, confirm=True)
        assert isinstance(deleted, jsonapi_module.DeleteFolderResponseModel)

    def test_property_refresh_dt(self, apiobj):
        root = apiobj.get()
        assert isinstance(root.path_public.refresh_dt, datetime.datetime)

    def test_property_refreshed(self, apiobj):
        root = apiobj.get()
        assert isinstance(root.path_public.refreshed, bool)

    def test_find_self(self, apiobj):
        root = apiobj.get()
        folder = root.path_public
        found = folder.find(folder=folder)
        assert found == folder

    def test_property_parent_public_root(self, apiobj):
        root = apiobj.get()
        public_path: str = str(root.get_enum_paths().public)
        folder = root.find(folder=public_path)
        assert folder.parent == folder.root

    def test_property_path_public_root(self, apiobj):
        root = apiobj.get()
        public_path: str = str(root.get_enum_paths().public)
        folder = root.find(folder=public_path)
        assert folder.root == folder.root

    def test_property_parent_private_root(self, apiobj):
        root = apiobj.get()
        private_path: str = str(root.get_enum_paths().private)
        folder = root.find(folder=private_path)
        assert folder.parent == folder.root

    def test_property_path_private_root(self, apiobj):
        root = apiobj.get()
        private_path: str = str(root.get_enum_paths().private)
        folder = root.find(folder=private_path)
        assert folder.root == folder.root

    def test_property_subfolders_recursive(self, apiobj, jsonapi_module):
        root = apiobj.get()
        public = root.path_public

        assert isinstance(public.subfolders_recursive, list)
        assert root not in public.subfolders_recursive
        assert public not in public.subfolders_recursive
        for item in public.subfolders_recursive:
            assert isinstance(item, jsonapi_module.Folder)

    def test_property_all_folders(self, apiobj, jsonapi_module):
        root = apiobj.get()
        public = root.path_public

        assert public.all_folders
        assert isinstance(public.all_folders, list)
        assert root in public.all_folders
        assert public in public.all_folders
        for item in public.all_folders:
            assert isinstance(item, jsonapi_module.Folder)

    def test_create_delete_public(self, apiobj, jsonapi_module):
        root = apiobj.get()
        public = root.path_public
        badwolf = public.create(folder="badwolf_crud")
        assert badwolf.parent == root.path_public
        assert badwolf.root == root.path_public
        badwolf2 = public.create(folder="badwolf_crud")
        assert badwolf == badwolf2

        deleted_folder = badwolf.delete(confirm=True)
        assert isinstance(deleted_folder, jsonapi_module.DeleteFolderResponseModel)
        assert str(deleted_folder)
        assert repr(deleted_folder)
        assert deleted_folder.message

        with pytest.raises(NotAllowedError) as exc:
            badwolf.delete(confirm=True, delete_subfolders=True)
        assert "is already deleted" in str(exc.value)

        with pytest.raises(FolderNotFoundError):
            root.find(folder=badwolf, refresh=True)

    def test_echo_tree(self, apiobj):
        root = apiobj.get()
        root.echo_tree()

    def test__clear_objects_cache(self, apiobj):
        root = apiobj.get()
        root._clear_objects_cache()

    def test_delete_delete_subfolders(self, apiobj, jsonapi_module):
        root = apiobj.get()
        leaf1 = "badwolf delete include subfolders"
        leaf2 = "alpha"
        leaf3 = "beta"

        path1 = root.join_under(leaf1)
        path2 = root.join_under(leaf1, leaf2)
        path3 = root.join_under(leaf1, leaf2, leaf3)

        folder3 = root.create(folder=path3)
        folder2 = root.create(folder=path2)
        folder1 = root.create(folder=path1)

        assert folder3.name == leaf3
        assert folder2.name == leaf2
        assert folder1.name == leaf1

        assert folder3.root == root.path_public

        with pytest.raises(NotAllowedError) as exc:
            folder1.delete(confirm=True)
        assert "delete_subfolders is False" in str(exc.value)

        deleted1 = folder1.delete(delete_subfolders=True, confirm=True)
        assert isinstance(deleted1, jsonapi_module.DeleteFolderResponseModel)
        assert str(deleted1)
        assert repr(deleted1)
        assert deleted1.message

        with pytest.raises(NotAllowedError) as exc:
            folder1.delete(delete_subfolders=True, confirm=True)
        assert "is already deleted" in str(exc.value)

        with pytest.raises(FolderNotFoundError):
            root.find(folder=folder3, refresh=True)

    def test_find_subfolder_create_delete(self, apiobj, jsonapi_module):
        root = apiobj.get()
        public = root.path_public
        badwolf = public.find_subfolder(folder="badwolf crud", create=True)
        assert badwolf.name == "badwolf crud"
        assert badwolf.parent.name == public.name

        deleted_folder = badwolf.delete(confirm=True)
        assert isinstance(deleted_folder, jsonapi_module.DeleteFolderResponseModel)
        assert str(deleted_folder)
        assert repr(deleted_folder)
        assert deleted_folder.message

        with pytest.raises(NotAllowedError) as exc:
            badwolf.delete(delete_subfolders=True, confirm=True)
        assert "is already deleted" in str(exc.value)

        root.refresh(force=True)
        with pytest.raises(FolderNotFoundError):
            root.find_subfolder(folder=badwolf.name)

    def test_move_under_path_exc(self, apiobj):
        root = apiobj.get()
        public = root.path_public
        badwolf = public.find_subfolder(folder="badwolf under test", create=True)
        path = f"{badwolf.path}/test under"

        with pytest.raises(NotAllowedError) as exc:
            badwolf.move(folder=path)
        assert "is under this path" in str(exc.value)
        badwolf.delete(confirm=True, delete_subfolders=True)

    def test_rename_exc(self, apiobj):
        root = apiobj.get()
        with pytest.raises(NotAllowedError) as exc:
            root.path_public.rename("xxx/xx")
        assert "can not use" in str(exc.value)

    def test_rename(self, apiobj):
        root = apiobj.get()
        public = root.path_public
        try:
            found = public.find(f"{public.path}/badwolf renamed")
        except FolderNotFoundError:
            pass
        else:
            found.delete(confirm=True, delete_subfolders=True, delete_objects=True)
        badwolf = public.find_subfolder(folder="badwolf rename", create=True)
        badwolf.create(folder="a/b/c/")
        renamed = badwolf.rename(folder="badwolf renamed")
        assert "a" in renamed.subfolders_by_name
        renamed.delete(confirm=True, delete_subfolders=True, delete_objects=True)

    def test_rename_exists(self, apiobj):
        root = apiobj.get()
        name1 = "badwolf rename exists 1"
        name2 = "badwolf rename exists 2"

        path1 = root.path_public.join_under(name1)
        path2 = root.path_public.join_under(name2)

        folder1 = root.find(folder=path1, create=True)
        folder2 = root.find(folder=path2, create=True)

        folder1.refresh(force=True)
        with pytest.raises(FolderAlreadyExistsError) as exc:
            folder1.rename(folder=folder2.name)
        assert "already exists" in str(exc.value)

        folder1.delete(confirm=True, delete_subfolders=True, delete_objects=True)
        folder2.delete(confirm=True, delete_subfolders=True, delete_objects=True)

    def test_move(self, apiobj):
        root = apiobj.get()
        public = root.path_public
        try:
            found = public.find(f"{public.path}/badwolf moved")
        except FolderNotFoundError:
            pass
        else:
            found.delete(confirm=True, delete_subfolders=True, delete_objects=True)
        badwolf = public.find_subfolder(folder="badwolf move", create=True)
        badwolf.create(folder="a/b/c/")
        moved = badwolf.move(folder=f"{public.path}/badwolf moved")
        assert "a" in moved.subfolders_by_name
        moved.delete(confirm=True, delete_subfolders=True, delete_objects=True)

    def test_resolve_folder_default(self, apiobj):
        root = apiobj.get()

        folder = root.resolve_folder()
        assert folder == root.path_public

    def test_resolve_folder_default_supplied(self, apiobj):
        root = apiobj.get()

        folder = root.path_private.resolve_folder(default=root.path_public)
        assert folder == root.path_public

    def test_resolve_folder_private_true(self, apiobj):
        root = apiobj.get()

        folder = root.resolve_folder(private=True)
        assert folder == root.path_private

    def test_resolve_folder_value_model(self, apiobj):
        root = apiobj.get()

        folder = root.path_public.resolve_folder(folder=root.path_private)
        assert folder == root.path_private

    def test_resolve_folder_value_str(self, apiobj):
        root = apiobj.get()

        folder = root.path_public.resolve_folder(folder=f"{root.path_private.path}")
        assert folder == root.path_private


class FoldersBase:
    @pytest.mark.parametrize(
        "value, exp",
        [
            [
                ["abc"],
                "/abc",
            ],
            [
                [folders.queries.FolderNames.public],
                str(folders.queries.FolderPaths.public),
            ],
        ],
    )
    def test_join(self, apiobj, value, exp):
        root = apiobj.get()
        ret = root.join(*value)
        assert ret == exp

    def test_join_under(self, apiobj):
        root = apiobj.get()
        value = "x/y"
        exp = f"{root.path_public.path}/x/y"
        assert root.path_public.join_under(value) == exp

    @pytest.mark.parametrize(
        "value, exp",
        [
            [
                " / x / a1",
                ["x", "a1"],
            ],
            [
                "a/b/",
                ["a", "b"],
            ],
        ],
    )
    def test_split(self, apiobj, value, exp):
        root = apiobj.get()
        ret = root.split(value)
        assert ret == exp

    def test__load_folders_bad_type_exc(self, apiobj):
        root = apiobj.get()
        with pytest.raises(AxonTypeError):
            root._load_folders(values="")

    def test_find_bad_type_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(AxonTypeError):
            root.find(folder={})

    def test_find_bad_str_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(AxonTypeError):
            root.find(folder="")

    def test_find_by_id_bad_type_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(AxonTypeError):
            root.find_by_id(folder={})

    def test_find_by_path_bad_type_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(AxonTypeError):
            root.find_by_path(folder={})

    def test_find_subfolder_bad_type_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(AxonTypeError):
            root.find_subfolder(folder={})

    def test_create_bad_type_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(AxonTypeError):
            root.create(folder={})

    def test_create_bad_str_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(AxonTypeError):
            root.create(folder="")

    def test_get(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert isinstance(root, jsonapi_module.FoldersModel)
        assert root.root is None

    def test__str__(self, apiobj):
        root = apiobj.get()

        assert str(root)

    def test__repr__(self, apiobj):
        root = apiobj.get()
        assert repr(root)

    def test__parse_refresh_bool_False(self, apiobj):
        root = apiobj.get()
        assert root._parse_refresh(value=False) is False

    def test__parse_refresh_int_below_elapsed(self, apiobj, monkeypatch):
        root = apiobj.get()
        root.refresh_dt = datetime.datetime.now() - datetime.timedelta(seconds=30)
        assert root._parse_refresh(value=root.refresh_elapsed + 1) is False

    def test__parse_refresh_int_above_elapsed(self, apiobj):
        root = apiobj.get()
        root.refresh_dt = datetime.datetime.now() - datetime.timedelta(seconds=30)
        assert root._parse_refresh(value=root.refresh_elapsed - 1) is True

    def test_property_depth(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.depth == jsonapi_module.FoldersModel.depth

    def test_property_id(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.id == jsonapi_module.FoldersModel._id

    def test_property_name(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.name == jsonapi_module.FoldersModel.name

    def test_property_root_type(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.root_type == jsonapi_module.FoldersModel.root_type

    def test_property_parent_id(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.parent_id == jsonapi_module.FoldersModel.parent_id

    def test_property_root_id(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.root_id == jsonapi_module.FoldersModel.root_id

    def test_property_created_by(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.created_by == jsonapi_module.FoldersModel.created_by

    def test_property_path(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.path == jsonapi_module.FoldersModel.path

    def test_property_read_only(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.read_only == jsonapi_module.FoldersModel.read_only

    def test_property_created_at(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.created_at == jsonapi_module.FoldersModel.created_at

    def test_property_updated_at(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.updated_at == jsonapi_module.FoldersModel.updated_at

    def test_property_children_ids(self, apiobj):
        root = apiobj.get()
        assert root.children_ids
        assert isinstance(root.children_ids, list)
        for x in root.children_ids:
            assert isinstance(x, str)

    def test_property_children(self, apiobj):
        root = apiobj.get()
        assert root.children
        assert isinstance(root.children, list)
        for x in root.children:
            assert isinstance(x, dict)

    def test_property_path_private(self, apiobj, jsonapi_module):
        root = apiobj.get()
        private_name: str = str(root.get_enum_names().private)
        assert isinstance(root.path_private, jsonapi_module.FolderModel)
        assert root.path_private.name == private_name
        assert root.path_private.depth == 1

    def test_property_path_public(self, apiobj, jsonapi_module):
        root = apiobj.get()
        enum_names = root.get_enum_names()
        assert isinstance(root.path_public, jsonapi_module.FolderModel)
        expected_name = str(enum_names.public)
        assert root.path_public.name == expected_name
        assert root.path_public.depth == 1

    def test_property_count_total(self, apiobj):
        root = apiobj.get()
        assert root.count_total >= 2

    def test_property_count_subfolders(self, apiobj):
        root = apiobj.get()
        assert root.count_subfolders > 0

    def test_property_count_objects(self, apiobj):
        root = apiobj.get()
        assert root.count_objects == 0

    def test_property_count_recursive_total(self, apiobj):
        root = apiobj.get()
        assert root.count_recursive_total >= 2

    def test_property_count_recursive_subfolders(self, apiobj):
        root = apiobj.get()
        assert root.count_recursive_subfolders >= root.count_subfolders

    def test_property_count_recursive_objects(self, apiobj):
        root = apiobj.get()
        assert root.count_recursive_objects >= root.count_objects

    def test_property_root(self, apiobj):
        root = apiobj.get()
        assert root.root is None

    def test_property_parent(self, apiobj):
        root = apiobj.get()
        assert root.parent is None

    def test_property_subfolders_recursive(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.subfolders_recursive
        assert isinstance(root.subfolders_recursive, list)
        assert root not in root.subfolders_recursive
        for item in root.subfolders_recursive:
            assert isinstance(item, jsonapi_module.Folder)

    def test_property_all_folders(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.all_folders
        assert isinstance(root.all_folders, list)
        assert root in root.all_folders
        for item in root.all_folders:
            assert isinstance(item, jsonapi_module.Folder)

    def test_property_all_folders_by_id(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.all_folders_by_id
        assert isinstance(root.all_folders_by_id, dict)
        for k, v in root.all_folders_by_id.items():
            assert isinstance(k, str) and k.strip()
            assert isinstance(v, jsonapi_module.Folder)

    def test_property_all_folders_by_id_summary(self, apiobj):
        root = apiobj.get()
        assert root.all_folders_by_id_summary
        assert isinstance(root.all_folders_by_id_summary, list)
        for x in root.all_folders_by_id_summary:
            assert isinstance(x, str)

    def test_property_subfolders(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.subfolders
        assert isinstance(root.subfolders, list)
        for x in root.subfolders:
            assert isinstance(x, jsonapi_module.Folder)
            assert x.depth == 1
            assert x.root == root
            assert x.parent == root

    def test_property_subfolders_summary(self, apiobj):
        root = apiobj.get()
        assert root.subfolders_summary
        assert isinstance(root.subfolders_summary, list)
        for x in root.subfolders_summary:
            assert isinstance(x, str)

    def test_property_subfolders_by_name(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.subfolders_by_name
        assert isinstance(root.subfolders_by_name, dict)
        for k, v in root.subfolders_by_name.items():
            assert isinstance(k, str) and k.strip()
            assert isinstance(v, jsonapi_module.FolderModel)

    def test_property_subfolders_by_id_recursive(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.subfolders_by_id_recursive
        assert isinstance(root.subfolders_by_id_recursive, dict)
        for k, v in root.subfolders_by_id_recursive.items():
            assert isinstance(k, str) and k.strip()
            assert isinstance(v, jsonapi_module.FolderModel)

    def test_property_subfolders_by_path_recursive(self, apiobj, jsonapi_module):
        root = apiobj.get()
        assert root.subfolders_by_path_recursive
        assert isinstance(root.subfolders_by_path_recursive, dict)
        for k, v in root.subfolders_by_path_recursive.items():
            assert isinstance(k, str) and jsonapi_module.FoldersModel.sep in k
            assert isinstance(v, jsonapi_module.FolderModel)

    def test_property_refresh_elapsed(self, apiobj):
        root = apiobj.get()
        assert isinstance(root.refresh_elapsed, float)

    def test_get_objects_recursive(self, apiobj):
        root = apiobj.get()
        items = root.get_objects(recursive=True)
        assert isinstance(items, list)
        for item in items:
            assert root.is_models_objects(item)

    def test_get_objects_all_objects(self, apiobj):
        root = apiobj.get()
        items = root.get_objects(all_objects=True)
        assert isinstance(items, list)
        for item in items:
            assert root.is_models_objects(item)

    def test_get_tree(self, apiobj):
        root = apiobj.get()
        data = root.get_tree()
        assert len(data) > 1
        assert isinstance(data, list)
        for x in data:
            assert isinstance(x, str) and x.strip()

    def test_get_tree_maximum_depth_0(self, apiobj):
        root = apiobj.get()
        data = root.get_tree(maximum_depth=0)
        assert len(data) == 1
        assert "recursive" in data[0]

    def test_get_tree_maximum_depth_1(self, apiobj):
        root = apiobj.get()
        data = root.get_tree(maximum_depth=1)
        data_txt = "\n".join(data)
        assert len(data) >= root.count_total
        assert "recursive" in data_txt

    def test_get_tree_include_details(self, apiobj):
        root = apiobj.get()
        data = root.get_tree(include_details=True)
        assert len(data) >= root.count_total
        assert "id=" in data[0]

    def test_get_tree_include_objects(self, apiobj):
        root = apiobj.get()
        data = root.get_tree(include_objects=True)
        data_txt = "\n".join(data)
        assert len(data) >= root.count_recursive_total
        if root.count_recursive_objects:
            assert any([x.get_tree_type() in data_txt for x in root.get_models_objects()])

    def test_get_tree_include_objects_include_details(self, apiobj):
        root = apiobj.get()
        data = root.get_tree(include_details=True, include_objects=True)
        data_txt = "\n".join(data)
        assert len(data) >= root.count_recursive_total
        if root.count_recursive_objects:
            assert any([x.get_tree_type() in data_txt for x in root.get_models_objects()])

    def test_get_tree_include_objects_include_details_maximum_depth_4(self, apiobj):
        root = apiobj.get()
        leaf1 = "badwolf tree with 3 levels of leaves"
        leaf2 = "leaf1"
        leaf3 = "leaf2"
        leaf4 = "leaf3"
        path1 = root.path_public.join_under(leaf1)
        path2 = root.path_public.join_under(leaf1, leaf2)
        path3 = root.path_public.join_under(leaf1, leaf2, leaf3)
        path4 = root.path_public.join_under(leaf1, leaf2, leaf3, leaf4)

        folder4 = root.path_public.find(folder=path4, create=True)
        root = folder4.root

        assert folder4.name == leaf4
        assert folder4.path == path4
        folder3 = folder4.parent
        assert folder3.name == leaf3
        assert folder3.path == path3
        folder2 = folder3.parent
        assert folder2.name == leaf2
        assert folder2.path == path2
        folder1 = folder2.parent
        assert folder1.name == leaf1
        assert folder1.path == path1

        tree = apiobj.get_tree(
            maximum_depth=4, include_details=True, include_objects=True, as_str=True
        )
        assert len(tree) >= root.count_total
        assert path1 in tree
        assert path2 in tree
        assert path3 in tree
        assert path4 not in tree
        assert "subfolders_recursive=" in tree
        assert "objects_recursive=" in tree

        if root.count_recursive_objects:
            assert any([x.get_tree_type() in tree for x in root.get_models_objects()])

        folder1.delete(delete_subfolders=True, confirm=True)

        tree = apiobj.get_tree(include_details=True, include_objects=True, as_str=True)
        assert path1 not in tree
        assert path2 not in tree
        assert path3 not in tree
        assert path4 not in tree

    def test_find_self(self, apiobj):
        root = apiobj.get()
        found = root.find(root)
        assert found == root

    def test_find_root_path(self, apiobj):
        root = apiobj.get()
        found = root.find(root.sep)
        assert found == root

    def test_find_root_id(self, apiobj):
        root = apiobj.get()
        found = root.find(root._id)
        assert found == root

    @pytest.mark.parametrize("refresh", [True, "yes"])
    def test_refresh_true(self, apiobj, refresh):
        root = apiobj.get()

        removed = root.folders.pop()
        root = apiobj.get()
        root.refreshed = False
        root.refresh(value=refresh)
        assert root.refreshed is True
        assert removed in root.folders

    @pytest.mark.parametrize("refresh", [False, "no"])
    def test_refresh_false(self, apiobj, refresh):
        root = apiobj.get()
        removed = root.folders.pop()
        root.refresh_dt = datetime.datetime.now()
        root.refreshed = False
        root.refresh(value=refresh)
        assert root.refreshed is False
        assert removed not in root.folders
        root.folders.append(removed)

    @pytest.mark.parametrize("refresh,seconds", [[20, 30], ["40", 50], [66.6, 70], ["88.8", 90]])
    def test_refresh_num_true(self, apiobj, refresh, seconds):
        root = apiobj.get()
        delta = datetime.timedelta(seconds=seconds)
        root.refresh_dt = root.refresh_dt - delta
        removed = root.folders.pop()
        root.refreshed = False
        root.refresh(value=refresh)
        assert root.refreshed is True
        assert removed in root.folders

    @pytest.mark.parametrize("refresh,seconds", [[10, 1], ["20", 1], [30.30, 1], ["40.40", 1]])
    def test_refresh_num_false(self, apiobj, refresh, seconds):
        root = apiobj.get()
        delta = datetime.timedelta(seconds=seconds)
        root.refresh_dt = root.refresh_dt - delta
        removed = root.folders.pop()
        root.refreshed = False
        root.refresh(value=refresh)
        assert root.refreshed is False
        assert removed not in root.folders
        root.folders.append(removed)

    def test_property_refresh_dt(self, apiobj):
        root = apiobj.get()
        assert isinstance(root.refresh_dt, datetime.datetime)

    def test_property_refreshed(self, apiobj):
        root = apiobj.get()
        assert isinstance(root.refreshed, bool)

    def test_find_subfolder_found_enum(self, apiobj, jsonapi_module):
        root = apiobj.get()
        public_name = root.get_enum_names().public
        folder = root.find_subfolder(folder=public_name)
        assert isinstance(folder, jsonapi_module.FolderModel)
        assert folder.name == str(public_name)

    def test_find_subfolder_not_found_exc(self, apiobj):
        root = apiobj.get()
        with pytest.raises(FolderNotFoundError):
            root.find_subfolder("badwolf")

    def test_find_by_path_absolute_found(self, apiobj, jsonapi_module):
        root = apiobj.get()
        public_name: str = str(root.get_enum_names().public)
        public_path: str = str(root.get_enum_paths().public)
        folder = root.find_by_path(folder=public_path)
        assert isinstance(folder, jsonapi_module.FolderModel)
        assert folder.name == public_name

    def test_find_by_path_absolute_not_found_exc(self, apiobj):
        root = apiobj.get()
        with pytest.raises(FolderNotFoundError):
            root.find_by_path("{root.sep}badwolf")

    def test_find_by_path_relative_found(self, apiobj, jsonapi_module):
        root = apiobj.get()
        public_name: str = str(root.get_enum_names().public)
        folder = root.find_by_path(public_name)
        assert isinstance(folder, jsonapi_module.FolderModel)
        assert folder.name == public_name

    def test_find_by_path_relative_not_found_exc(self, apiobj):
        root = apiobj.get()
        with pytest.raises(FolderNotFoundError):
            root.find_by_path(folder="badwolf")

    def test_create_read_only_exc(self, apiobj):
        root = apiobj.get()
        with pytest.raises(NotAllowedError) as exc:
            root.create(folder="badwolf")
        assert "is read-only" in str(exc.value)

    def test_delete_read_only_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(NotAllowedError) as exc:
            root.delete(confirm=True)
        assert "is read-only" in str(exc.value)

    def test_delete_root_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(NotAllowedError) as exc:
            root.path_public.delete(confirm=True)
        assert "below minimum_depth" in str(exc.value)

    def test_get_model_folder(self, apiobj, jsonapi_module):
        root = apiobj.get()

        assert root.get_model_folder() == jsonapi_module.FolderModel

    def test_get_model_folders(self, apiobj, jsonapi_module):
        root = apiobj.get()

        assert root.get_model_folders() == jsonapi_module.FoldersModel

    def test_get_models_objects(self, apiobj, jsonapi_module):
        root = apiobj.get()

        models = root.get_models_objects()
        assert isinstance(models, tuple) and models

    def test_rename_not_allowed_root_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(NotAllowedError) as exc:
            root.rename(folder="zzz")
        assert "is read-only" in str(exc.value)

    def test_move_not_allowed_root_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(NotAllowedError) as exc:
            root.move(folder=f"{root.path_public.path}")
        assert "is read-only" in str(exc.value)

    def test_rename_not_allowed_depth_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(NotAllowedError) as exc:
            root.path_public.rename(folder="badwolf")
        assert "below minimum_depth" in str(exc.value)

    def test_move_not_allowed_depth_exc(self, apiobj):
        root = apiobj.get()

        with pytest.raises(NotAllowedError) as exc:
            root.path_public.move(folder=f"{root.path_public.path}/badwolf")
        assert "below minimum_depth" in str(exc.value)


class TestFolderNoMixups:
    def test_other_type(self, api_client):
        queries = api_client.folders.queries.get()
        enforcements = api_client.folders.enforcements.get()
        with pytest.raises(AxonTypeError):
            queries.find(enforcements.path_public)

        with pytest.raises(AxonTypeError):
            enforcements.find(queries.path_public)


class TestFolderQueries(FolderBase, FolderBaseQueries):
    pass


class TestFoldersQueries(FoldersBase, FolderBaseQueries):
    # NEXT: not in release yet
    # def test_property_path_archive(self, apiobj, jsonapi_module):
    #     root = apiobj.get()

    #     archive_name: str = str(root.get_enum_names().archive)
    #     assert isinstance(root.path_archive, jsonapi_module.FolderModel)
    #     assert root.path_archive.name == archive_name
    #     assert root.path_archive.depth == 1

    def test_property_path_public(self, api_client, apiobj, jsonapi_module):
        root = apiobj.get()
        enum_names = root.get_enum_names()
        assert isinstance(root.path_public, jsonapi_module.FolderModel)

        if api_client.data_scopes.is_feature_enabled:
            expected_name = str(enum_names.global_scope)
        else:
            expected_name = str(enum_names.public)

        assert root.path_public.name == expected_name
        assert root.path_public.depth == 1

    def test_property_path_predefined(self, apiobj, jsonapi_module):
        root = apiobj.get()

        predefined_name: str = str(root.get_enum_names().predefined)
        assert isinstance(root.path_predefined, jsonapi_module.FolderModel)
        assert root.path_predefined.name == predefined_name
        assert root.path_predefined.depth == 2

    def test_property_path_asset_scope(self, apiobj, api_client, jsonapi_module):
        root = apiobj.get()

        asset_scope_name: str = str(root.get_enum_names().asset_scope)

        if api_client.data_scopes.is_feature_enabled:
            assert isinstance(root.path_asset_scope, jsonapi_module.FolderModel)
            assert root.path_asset_scope.name == asset_scope_name
            assert root.path_asset_scope.depth == 1
        else:
            with pytest.raises(FolderNotFoundError):
                root.path_asset_scope

    def test_resolve_folder_asset_scope_true(self, apiobj, api_client):
        root = apiobj.get()

        if api_client.data_scopes.is_feature_enabled:
            folder = root.resolve_folder(asset_scope=True)
            assert folder == root.path_asset_scope
        else:
            with pytest.raises(FolderNotFoundError):
                root.resolve_folder(asset_scope=True)

    def test_get_root_types(self, apiobj):
        root = apiobj.get()

        assert issubclass(root.get_root_types(), BaseEnum)


class TestFoldersEnforcements(FoldersBase, FolderBaseEnforcements):
    pass


class TestFolderEnforcements(FolderBase, FolderBaseEnforcements):
    pass
