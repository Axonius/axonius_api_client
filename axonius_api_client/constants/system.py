# -*- coding: utf-8 -*-
"""Constants for system objects."""


class Role:
    """Keys for role objects."""

    PERMS: str = "permissions"
    PERMS_FLAT: str = f"{PERMS}_flat"
    PERMS_PRE: str = PERMS
    CATS: str = "categories"
    ACTS: str = "actions"
    UUID: str = "uuid"
    NAME: str = "name"
    ALL: str = "all"
    COMP: str = "compliance"
    CATS_DESC: str = f"{CATS}_desc"
    ACTS_DESC: str = f"{ACTS}_desc"
    LENS: str = "lengths"
    TABLES: dict = {"Name": NAME, "UUID": UUID}
    TABLES_PERMS: str = "Categories: actions"
    R_ADMIN: str = "Admin"
    R_VIEWER: str = "Viewer"
    R_NOACCESS: str = "No Access"
    R_RESTRICTED: str = "Restricted"


class User:
    """Keys for user objects."""

    EMAIL: str = "email"
    FIRST_NAME: str = "first_name"
    LAST_LOGIN: str = "last_login"
    LAST_NAME: str = "last_name"
    FULL_NAME: str = "full_name"
    PASSWORD: str = "password"
    PIC_NAME: str = "pic_name"
    ROLE_ID: str = "role_id"
    ROLE_NAME: str = "role_name"
    ROLE_OBJ: str = "role_obj"
    SOURCE: str = "source"
    USER_NAME: str = "user_name"
    IGNORE_RULES: str = "ignore_role_assignment_rules"
    NAME: str = USER_NAME
    UUID: str = "uuid"
    TABLES: dict = {
        "Name": NAME,
        "UUID": UUID,
        "Full Name": FULL_NAME,
        "Role Name": ROLE_NAME,
        "Email": EMAIL,
        "Last Login": LAST_LOGIN,
        "Source": SOURCE,
    }
    INTERNAL: str = "internal"
    ADMIN_NAME: str = "admin"
