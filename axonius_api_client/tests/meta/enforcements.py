"""Metadata for enforcements."""
from __future__ import absolute_import, division, print_function, unicode_literals

import time

LINUX_QUERY = 'specific_data.data.os.type == "Linux"'
SHELL_ACTION_NAME = "Badwolf Shell Action"
SHELL_ACTION_CMD = "echo 'Badwolf' > /tmp/badwolf.txt"
DEPLOY_ACTION_NAME = "Badwolf Deploy Action"
DEPLOY_FILE_NAME = "badwolf.sh"
DEPLOY_FILE_CONTENTS = b"#!/bin/bash\necho badwolf!"

CREATE_EC_NAME = "Badwolf EC Example"
CREATE_EC_TRIGGER1 = {
    "name": "Trigger",
    "conditions": {
        "new_entities": False,
        "previous_entities": False,
        "above": 1,
        "below": 0,
    },
    "period": "never",
    "run_on": "AllEntities",
}

CREATE_EC_ACTION_MAIN = {
    "name": "Badwolf Create Notification {}".format(time.time()),
    "action": {"action_name": "create_notification", "config": {}},
}
