# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ... import INIT_DOTENV
from ...projects import cert_human, url_parser
from ...setup_env import KEY_CERTPATH, set_env
from ...tools import echo_ok, echo_warn, get_path, json_dump, path_write


def export_json(data, **kwargs):
    """Pass."""

    def dump(obj):
        return obj.to_dict()

    return json_dump([dump(x) for x in data] if isinstance(data, list) else dump(data))


def export_str(data, **kwargs):
    """Pass."""

    def dump(obj):
        return obj.to_str()

    barrier = "-" * 80
    return (
        f"\n\n{barrier}".join([dump(x) for x in data])
        if isinstance(data, (tuple, list))
        else dump(data)
    )


def export_pem(data, **kwargs):
    """Pass."""

    def dump(obj):
        return obj.to_pem(as_str=True)

    return "\n\n".join([dump(x) for x in data]) if isinstance(data, list) else dump(data)


EXPORT_FORMATS: dict = {
    "pem": export_pem,
    "str": export_str,
    "json": export_json,
}


OPT_EXPORT_FILE = click.option(
    "--export-file",
    "-xf",
    "export_file",
    default="",
    help="File to send data to (STDOUT if not supplied)",
    show_envvar=True,
    show_default=True,
    metavar="PATH",
)
OPT_EXPORT_OVERWRITE = click.option(
    "--export-overwrite/--no-export-overwrite",
    "-xo/-nxo",
    "export_overwrite",
    default=False,
    help="If --export-file supplied and it exists, overwrite it",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)

OPT_EXPORT_FORMAT = click.option(
    "--export-format",
    "-xt",
    "export_format",
    type=click.Choice(list(EXPORT_FORMATS)),
    help="Format to export data in",
    default="str",
    show_envvar=True,
    show_default=True,
)

OPT_CSR_EXPORT_FORMAT = click.option(
    "--export-format",
    "-xt",
    "export_format",
    type=click.Choice(list(EXPORT_FORMATS)),
    help="Format to export data in",
    default="pem",
    show_envvar=True,
    show_default=True,
)


OPT_CSR_COMMON_NAME = click.option(
    "--common-name",
    "-cn",
    "common_name",
    help="Common Name to use for certificate request",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_CSR_SUBJECT_ALT_NAMES = click.option(
    "--subject-altname",
    "-san",
    "subject_alt_names",
    help="Subject Alternative Names to use for certificate request (multiple)",
    required=False,
    multiple=True,
    show_envvar=True,
    show_default=True,
)

OPT_CSR_COUNTRY = click.option(
    "--country",
    "-co",
    "country",
    help="Country to use for certificate request",
    default="",
    required=False,
    show_envvar=True,
    show_default=True,
)
OPT_CSR_STATE = click.option(
    "--state",
    "-st",
    "state",
    help="State to use for certificate request",
    default="",
    required=False,
    show_envvar=True,
    show_default=True,
)
OPT_CSR_LOCALITY = click.option(
    "--locality",
    "-lo",
    "locality",
    help="Locality to use for certificate request",
    default="",
    required=False,
    show_envvar=True,
    show_default=True,
)

OPT_CSR_ORGANIZATION = click.option(
    "--organization",
    "-org",
    "organization",
    help="Organization to use for certificate request",
    default="",
    required=False,
    show_envvar=True,
    show_default=True,
)

OPT_CSR_ORGANIZATIONAL_UNIT = click.option(
    "--organizational_unit",
    "-ou",
    "organizational_unit",
    help="Organizational Unit to use for certificate request",
    default="",
    required=False,
    show_envvar=True,
    show_default=True,
)

OPT_CSR_EMAIL = click.option(
    "--email",
    "-em",
    "email",
    help="Email to use for certificate request",
    default="",
    required=False,
    show_envvar=True,
    show_default=True,
)

OPT_CSR_OVERWRITE = click.option(
    "--overwrite/--no-overwrite",
    "-ow/-now",
    "overwrite",
    default=False,
    help="If a Certificate Request is already pending, cancel it and create a new one",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)

OPT_UPDATE_ENV = click.option(
    "--update-env/--no-update-env",
    "-ue/-nue",
    "update_env",
    default=False,
    help=f"Add '{KEY_CERTPATH}={{path_to_leaf_cert}}' to {INIT_DOTENV!r}",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
OPT_PROMPT = click.option(
    "--prompt/--no-prompt",
    "-p/-np",
    "prompt",
    default=True,
    help="Show certificate details and prompt for confirmation",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
OPT_EXPORT_FILE_PEM = click.option(
    "--export-file",
    "-xf",
    "export_file",
    default="{hostname}.pem",
    help="File to save certificate to (existing file will be renamed)",
    show_envvar=True,
    show_default=True,
    metavar="PATH",
)

OPTS_EXPORT = [
    OPT_EXPORT_OVERWRITE,
    OPT_EXPORT_FILE,
    OPT_EXPORT_FORMAT,
]

OPTS_CSR_EXPORT = [
    OPT_EXPORT_OVERWRITE,
    OPT_EXPORT_FILE,
    OPT_CSR_EXPORT_FORMAT,
]
OPTS_CSR = [
    OPT_CSR_COMMON_NAME,
    OPT_CSR_SUBJECT_ALT_NAMES,
    OPT_CSR_COUNTRY,
    OPT_CSR_STATE,
    OPT_CSR_LOCALITY,
    OPT_CSR_ORGANIZATION,
    OPT_CSR_ORGANIZATIONAL_UNIT,
    OPT_CSR_EMAIL,
    OPT_CSR_OVERWRITE,
]


def handle_export(
    data, export_format, export_file, export_overwrite=False, export_backup=False, **kwargs
):
    """Pass."""
    count = len(data) if isinstance(data, list) else 1
    output = EXPORT_FORMATS[export_format](data=data)
    if export_file:
        export_path = get_path(obj=export_file)
        if export_path.is_file() and export_backup:
            pass

        export_path, data = path_write(
            obj=export_path, data=output, overwrite=export_overwrite, backup=export_backup
        )
        byte_len, backup_path = data
        if backup_path:
            echo_warn(f"Backed up existing {export_path} to {backup_path}")

        echo_ok(
            f"Wrote {count} certificates in {export_format} format to: '{export_path}' "
            f"({byte_len} bytes)"
        )
    else:
        click.secho(output)
        echo_ok(f"Wrote {count} certificates in {export_format} format to STDOUT")


def split_leaf(chain):
    """Pass."""
    leaf_cert, intm_certs = chain[0], chain[1:]

    echo_ok(f"Received {len(chain)} certificates from {leaf_cert.SOURCE}")
    echo_ok(f"{leaf_cert}")
    for intm_cert in intm_certs:
        echo_ok(f"{intm_cert}")
    click.secho("")
    return leaf_cert, intm_certs


def from_url(url, split=True, ca_only=False):
    """Pass."""
    url_parsed = url_parser.UrlParser(url=url, default_scheme="https")
    echo_ok(f"Parsed {url} to {url_parsed}")
    chain = cert_human.Cert.from_requests_chain(url=url_parsed.url)
    leaf_cert, intm_certs = split_leaf(chain=chain)
    if ca_only:
        return [x for x in chain if x.is_certificate_authority]
    if split:
        return leaf_cert, intm_certs
    return chain


def from_path(path, split=True, ca_only=False):
    """Pass."""
    chain = cert_human.Cert.from_file(path=path)
    leaf_cert, intm_certs = split_leaf(chain=chain)
    if ca_only:
        return [x for x in chain if x.is_certificate_authority]
    if split:
        return leaf_cert, intm_certs
    return chain


def confirm_cert_replace(client, prompt):
    """Pass."""
    chain = client.HTTP.get_cert_chain()
    leaf_cert, intm_certs = split_leaf(chain=chain)
    prompt = confirm_cert(
        prompt=prompt,
        cert=leaf_cert,
        pre="View the details of the current certificate before replacing it?",
        post="Are you sure you want to replace this certificate?",
    )
    return leaf_cert, intm_certs


def confirm_cert(
    prompt,
    cert,
    pre="View the details for this certificate",
    post="Please confirm that this certificate looks correct",
):
    """Pass."""
    prompt = confirm(prompt=prompt, text=f"Certificate: {cert}\n{pre}")
    if prompt:
        click.secho(message=cert.to_str(), fg="green", err=True)
    confirm_abort(prompt=prompt, text=f"{post}")
    return prompt


def confirm(prompt, text, default=True, fg="cyan", fg_false="blue", abort=False):
    """Pass."""
    if prompt:
        stext = click.style(text=text, fg=fg)
        prompt = click.confirm(text=stext, default=default, err=True, abort=abort)
    else:
        click.secho(message=f"Prompting disabled, not asking: {text}", fg=fg_false)
    return prompt


def confirm_abort(prompt, text, default=False, fg="red", fg_false="blue"):
    """Pass."""
    return confirm(prompt=prompt, text=text, default=default, fg=fg, fg_false=fg_false, abort=True)


def handle_update_env(update_env, export_file):
    """Pass."""
    entry = f'{KEY_CERTPATH}="{export_file}"'
    uenv = f"update_env={update_env}"
    if update_env:
        set_env(key=KEY_CERTPATH, value=export_file)
        click.secho(
            message=f"{uenv} Updated {INIT_DOTENV!r} with:\n{entry}",
            err=True,
            fg="green",
        )
    else:
        click.secho(
            message=f"{uenv} Not updating {INIT_DOTENV!r} file with:\n{entry}",
            err=True,
            fg="blue",
        )


def pathify_export_file(client, export_file):
    """Pass."""
    hostname = client.HTTP.URLPARSED.hostname

    if "{hostname}" in export_file:
        export_file = export_file.format(hostname=hostname)

    return get_path(obj=export_file)
