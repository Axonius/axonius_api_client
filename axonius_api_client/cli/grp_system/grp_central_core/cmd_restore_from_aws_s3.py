# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

KEY_NAME = click.option(
    "--key-name",
    "-kn",
    "key_name",
    help="Key name of file object in [bucket_name] to restore",
    required=True,
    show_envvar=True,
    show_default=True,
)

BUCKET_NAME = click.option(
    "--bucket-name",
    "-bn",
    "bucket_name",
    default=None,
    help="Name of bucket in S3 to get [key_name] from",
    show_envvar=True,
    show_default=True,
)

ACCESS_KEY_ID = click.option(
    "--access-key-id",
    "-aki",
    "access_key_id",
    default=None,
    help="AWS Access Key Id to use to access [bucket_name]",
    show_envvar=True,
    show_default=True,
)
SECRET_ACCESS_KEY = click.option(
    "--secret-access-key",
    "-sak",
    "secret_access_key",
    default=None,
    help="AWS Secret Access Key to use to access [bucket_name]",
    show_envvar=True,
    show_default=True,
)
PRESHARED_KEY = click.option(
    "--preshared-key",
    "-pk",
    "preshared_key",
    default=None,
    help="Password to use to decrypt [key_name]",
    show_envvar=True,
    show_default=True,
)

ALLOW_RE_RESTORE = click.option(
    "--allow-re-restore/--no-allow-re-restore",
    "-arr/-narr",
    "allow_re_restore",
    help="Restore [key_name] even if it has already been restored",
    is_flag=True,
    default=False,
    show_envvar=True,
    show_default=True,
)
DELETE_BACKUPS = click.option(
    "--delete-backups/--no-delete-backups",
    "-db/-ndb",
    "delete_backups",
    help="Delete [key_name] from [bucket_name] after restore has finished",
    is_flag=True,
    default=None,
    show_envvar=True,
    show_default=True,
)

OPTIONS = [
    *AUTH,
    ACCESS_KEY_ID,
    SECRET_ACCESS_KEY,
    PRESHARED_KEY,
    ALLOW_RE_RESTORE,
    DELETE_BACKUPS,
    BUCKET_NAME,
    KEY_NAME,
]

EPILOG = """
If values for these options are not provided, they will default to
the settings under Global Settings > Amazon S3 Settings:

\b
  * bucket-name: Amazon S3 bucket name
  * access-key-id: AWS Access Key Id
  * secret-access-key: AWS Secret Access Key
  * preshared-key: Backup encryption passphrase

"""


@click.command(
    name="restore-from-aws-s3",
    context_settings=CONTEXT_SETTINGS,
    epilog=EPILOG,
)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Perform a manual restore of a backup in AWS S3."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.central_core.restore_from_aws_s3(**kwargs)

    click.secho(json_dump(data))
