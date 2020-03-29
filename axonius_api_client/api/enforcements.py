# -*- coding: utf-8 -*-
"""API models for working with Enforcement Center."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import warnings

from .. import constants, exceptions, tools
from . import assets, mixins, routers


class RunAction(mixins.Child):
    """Child API model for working with actions.

    Notes:
        The REST API will need to be updated to allow more power in this library.
        Until then, this class should be considered **BETA**.
    """

    @property
    def _router(self):
        """Router for this API model.

        Returns:
            :obj:`.routers.Router`: REST API route defs
        """
        return routers.ApiV1.actions

    # sort of pointless
    def _get(self):
        """Direct API method to get all actions.

        Returns:
            :obj:`list` of :obj:`str`: all actions known to system
        """
        path = self._router.root
        return self._parent._request(method="get", path=path)

    def _deploy(self, action_name, ids, file_uuid, file_name, params=None):
        """Deploy an action.

        Args:
            name (:obj:`str`): name of action to deploy
            ids (:obj:`list` of :obj:`str`): internal_axon_ids of devices to process
            uuid (:obj:`str`): UUID of binary to use in deployment
            filename (:obj:`str`): filename of binary to use in deployment
            params (:obj:`str`, optional): parameters to pass to action

        Returns:
            :obj:`object`: response from deploying action
        """
        data = {}
        data["action_name"] = action_name
        data["internal_axon_ids"] = ids
        data["binary"] = {}
        data["binary"]["filename"] = file_name
        data["binary"]["uuid"] = file_uuid
        data["params"] = params

        path = self._router.deploy

        return self._parent._request(method="post", path=path, json=data)

    def _shell(self, action_name, ids, command):
        """Run an action.

        Args:
            action_name (:obj:`str`): name of action to run
            ids (:obj:`list` of :obj:`str`): internal_axon_ids of devices to process
            command (:obj:`str`): command to run

        Returns:
            :obj:`object`: response from running action
        """
        data = {}
        data["action_name"] = action_name
        data["internal_axon_ids"] = ids
        data["command"] = command

        path = self._router.shell
        return self._parent._request(method="post", path=path, json=data)

    def _upload_file(self, name, content, content_type=None, headers=None):
        """Upload a file to the system for use in deployment.

        Args:
            binary (:obj:`io.BytesIO`): binary bits of file to upload
            filename (:obj:`str`): name of file to upload

        Returns:
            :obj:`str`: UUID of uploaded file.
        """
        data = {"field_name": "binary"}
        files = {"userfile": (name, content, content_type, headers)}

        path = self._router.upload_file

        ret = self._parent._request(method="post", path=path, data=data, files=files)
        ret["filename"] = name
        return ret


class Enforcements(mixins.Model, mixins.Mixins):
    """API model for working with enforcement center.

    Notes:
        The REST API will need to be updated to allow more power in this library.
        Until then, this class should be considered **BETA**.
    """

    def _init(self, auth, **kwargs):
        """Post init method for subclasses to use for extra setup.

        Args:
            auth (:obj:`.auth.Model`): object to use for auth and sending API requests
        """
        # cross ref
        self.users = assets.Users(auth=auth, **kwargs)
        self.devices = assets.Devices(auth=auth, **kwargs)

        # children
        self.runaction = RunAction(parent=self)

        super(Enforcements, self)._init(auth=auth, **kwargs)

        warnings.warn(exceptions.BetaWarning(obj=self))

    @property
    def _router(self):
        """Router for this API model.

        Returns:
            :obj:`.routers.Router`: REST API route defs
        """
        return routers.ApiV1.alerts

    def _delete(self, ids):
        """Delete objects by internal axonius IDs.

        Args:
            ids (:obj:`list` of :obj:`str`): internal_axon_ids of devices to process
        """
        path = self._router.root

        return self._request(method="delete", path=path, json=ids)

    def _create(self, name, main, success=None, failure=None, post=None, triggers=None):
        """Create an enforcement set.

        Args:
            name (:obj:`str`): name of enforcement to create
            main (:obj:`dict`): main action
            success (:obj:`list` of :obj:`dict`, optional): success actions
            failure (:obj:`list` of :obj:`dict`, optional): failure actions
            post (:obj:`list` of :obj:`dict`, optional): post actions
            triggers (:obj:`list` of :obj:`dict`, optional): saved query trigger

        Notes:
            This will get a public create method once the REST API server has been
            updated to expose /enforcements/actions, /api/enforcements/actions/saved,
            and others.

        Returns:
            :obj:`str`: ID of created enforcement set.
        """
        data = {}
        data["name"] = name
        data["actions"] = {}
        data["actions"]["main"] = main
        data["actions"]["success"] = success or []
        data["actions"]["failure"] = failure or []
        data["actions"]["post"] = post or []
        data["triggers"] = triggers or []

        print(tools.json_reload(data))

        path = self._router.root
        return self._request(method="put", path=path, json=data, is_json=False)

    def _get(self, query=None, row_start=0, page_size=0):
        """Get a page for a given query."""
        if not page_size or page_size > constants.MAX_PAGE_SIZE:
            msg = "Changed page size from {ps} to max page size {mps}"
            msg = msg.format(ps=page_size, mps=constants.MAX_PAGE_SIZE)
            self._log.debug(msg)

            page_size = constants.MAX_PAGE_SIZE

        params = {}
        params["skip"] = row_start
        params["limit"] = page_size

        if query:
            params["filter"] = query

        path = self._router.root

        return self._request(method="get", path=path, params=params)

    def delete(self, rows):
        """Delete an enforcement by name."""
        return self._delete(
            ids=[x["uuid"] for x in tools.listify(obj=rows, dictkeys=False)]
        )

    def get(self, query=None, max_rows=None, max_pages=None, page_size=None):
        """Get enforcements."""
        if not page_size or page_size > constants.MAX_PAGE_SIZE:
            msg = "Changed page_size={ps} to max_page_size={mps}"
            msg = msg.format(ps=page_size, mps=constants.MAX_PAGE_SIZE)
            self._log.debug(msg)

            page_size = constants.MAX_PAGE_SIZE

        page_info = 0
        page_num = 0
        rows_fetched = 0
        rows = []
        fetch_start = tools.dt_now()

        msg = [
            "Starting get: page_size={}".format(page_size),
            "query={!r}".format(query or ""),
        ]
        self._log.debug(tools.join_comma(msg))

        while True:
            page_start = tools.dt_now()
            page_num += 1
            rows_left = max_rows - len(rows) if max_rows else -1

            if 0 < rows_left < page_size:
                msg = "Changed page_size={ps} to rows_left={rl} (max_rows={mr})"
                msg = msg.format(ps=page_size, rl=rows_left, mr=max_rows)
                self._log.debug(msg)

                page_size = rows_left

            msg = [
                "Fetching page_num={}".format(page_num),
                "page_size={}".format(page_size),
                "rows_fetched={}".format(rows_fetched),
            ]
            self._log.debug(tools.join_comma(obj=msg))

            page = self._get(query=query, page_size=page_size, row_start=rows_fetched)

            assets = page["assets"]
            page_info = page["page"]

            rows += assets
            rows_fetched += len(assets)

            msg = [
                "Fetched page_num={}".format(page_num),
                "page_took={}".format(tools.dt_sec_ago(obj=page_start)),
                "rows_fetched={}".format(rows_fetched),
                "page_info={}".format(page_info),
            ]
            self._log.debug(tools.join_comma(obj=msg))

            if not assets:
                msg = "Stopped fetch loop, page with no assets returned"
                self._log.debug(msg)
                break

            # add tests later once out of beta
            if max_pages and page_num >= max_pages:  # pragma: no cover
                msg = "Stopped fetch loop, hit max_pages={mp}"
                msg = msg.format(mp=max_pages)
                self._log.debug(msg)
                break

            if max_rows and len(rows) >= max_rows:
                msg = "Stopped fetch loop, hit max_rows={mr} with rows_fetched={rf}"
                msg = msg.format(mr=max_rows, rf=rows_fetched)
                self._log.debug(msg)
                break

        msg = [
            "Finished get: rows_fetched={}".format(rows_fetched),
            "total_rows={}".format(page_info["totalResources"]),
            "fetch_took={}".format(tools.dt_sec_ago(obj=fetch_start)),
            "query={!r}".format(query or ""),
        ]
        self._log.info(tools.join_comma(obj=msg))

        return rows

    def get_by_id(
        self, value, match_error=True, max_rows=None, max_pages=None, page_size=None
    ):
        """Get EC using paging."""
        rows = self.get(max_rows=max_rows, max_pages=max_pages, page_size=page_size)

        for row in rows:
            if row["uuid"] == value:
                return row

        if match_error:
            ktmpl = "name: {name!r}, uuid: {uuid!r}".format
            known = [ktmpl(**row) for row in rows]
            known_msg = "Enforcements"
            value_msg = "Enforcements by UUID"
            raise exceptions.ValueNotFound(
                value=value, value_msg=value_msg, known=known, known_msg=known_msg
            )

        return None

    def get_by_name(
        self,
        value,
        value_regex=False,
        value_not=False,
        match_count=None,
        match_error=True,
        eq_single=True,
        max_rows=None,
        max_pages=None,
        page_size=None,
    ):
        """Find actions by name."""
        if value_regex:  # pragma: no cover
            search = '== regex("{}", "i")'.format(value)
        else:
            search = '== "{}"'.format(value)

            if eq_single and not value_not:
                max_rows = 1
                match_count = 1
                match_error = True

        field = "name"
        not_flag = "not " if value_not else ""
        query = "{not_flag}{field} {search}"
        query = query.format(not_flag=not_flag, field=field, search=search).strip()

        rows = self.get(
            query=query, max_rows=max_rows, max_pages=max_pages, page_size=page_size
        )

        if (match_count and len(rows) != match_count) and match_error:
            ktmpl = "name: {name!r}, uuid: {uuid!r}".format
            known = [ktmpl(**row) for row in self.get()]
            known_msg = "Enforcements"
            value_msg = "Enforcements by name using query {q}".format(q=query)
            raise exceptions.ValueNotFound(
                value=value, value_msg=value_msg, known=known, known_msg=known_msg
            )

        if match_count == 1 and len(rows) == 1:
            return rows[0]

        return rows
