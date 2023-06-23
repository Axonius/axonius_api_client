"""Constants for the cf_token package."""
import sys
import typing as t
import pathlib

PathLike: t.TypeVar = t.TypeVar("PathLike", str, bytes, pathlib.Path)
StrList: t.TypeVar = t.TypeVar("StrList", str, bytes, t.Iterable[t.Union[str, bytes]])


def join_envs(values):
    """Join a list of environment variables into a string."""
    joined = " or ".join(values)
    plural = "s" if len(values) > 1 else ""
    return f"OS environment variable{plural} {joined}"


IS_WINDOWS: bool = sys.platform == "win32"
"""Running on a windows platform"""

IS_LINUX: bool = sys.platform == "linux"
"""Running on a linux platform"""

IS_MAC: bool = sys.platform == "darwin"
"""Running on a mac platform"""

ENVVAR_PREFIX: str = "CF"
"""Prefix for all OS environment variables used by this package"""

AX_ENVVAR_PREFIX: str = "AX"
"""Prefix used by axonshell to define OS environment variables"""

CLICK_CONTEXT: dict = {
    "show_default": True,
    "auto_envvar_prefix": ENVVAR_PREFIX,
}
"""Default context for click commands"""

CF_PATH: str = "cloudflared"
"""Default path to cloudflared binary - relies on `cloudflared` being in $PATH"""

TIMEOUT: t.Optional[int] = None
"""Timeout in seconds to use as default for `run`"""

TIMEOUT_ACCESS: t.Optional[int] = 60
"""Timeout in seconds to wait for CMD_ACCESS_STR to complete"""

TIMEOUT_LOGIN: t.Optional[int] = 60 * 3
"""Timeout in seconds to wait for CMD_LOGIN_STR to complete"""

CMD_ACCESS: t.List[str] = ["access", "token", "-app"]
"""Sub commands used to run to get a cloudflare access token"""

CMD_ACCESS_STR: str = f"{CF_PATH} {' '.join(CMD_ACCESS)} $url"
"""Command to run to get a cloudflare access token"""

CMD_LOGIN: t.List[str] = ["access", "login"]
"""Sub commands used to run to login and get a cloudflare access token"""

CMD_LOGIN_STR: str = f"{CF_PATH} {' '.join(CMD_LOGIN)} $url"
"""Command to run to login and get a cloudflare access token"""

PATH_ENV: str = "PATH"
"""OS environment variable to check for a path"""

PATH_HEADER: str = "--> OS Environment Variable $PATH:"
"""Header used to print the OS environment variable $PATH"""

PATHS_NOT_FOUND: t.List[str] = ["No paths found"]
"""Message used when no paths are found in the OS environment variable $PATH"""

URL_ENV: str = "URL"
"""OS environment variable to check for a url"""

URL_ENVS: t.Tuple[str, ...] = (f"{ENVVAR_PREFIX}_{URL_ENV}", f"{AX_ENVVAR_PREFIX}_{URL_ENV}")
"""OS environment variables to check for a url (in order of precedence)"""

URL_ENVS_STR: str = join_envs(URL_ENVS)
"""OS environment variables to check for a url"""

TOKEN_LENGTH: int = 870
"""Length used to validate a cloudflare access token"""

URL_LENGTH: int = 2
"""Length used to validate a cloudflare access url"""

TOKEN_ENV: str = "TOKEN"
"""OS environment variable to check for a token"""

TOKEN_ENVS: t.Tuple[str, ...] = (f"{ENVVAR_PREFIX}_{TOKEN_ENV}",)
"""OS environment variables to check for a token (in order of precedence)"""

TOKEN_ENVS_STR: str = join_envs(TOKEN_ENVS)
"""OS environment variables to check for a token"""

LEVEL_STYLES: t.Dict[str, t.Dict[str, t.Any]] = {
    "debug": {"fg": "blue", "bold": False},
    "info": {"fg": "green", "bold": True},
    "warning": {"fg": "yellow", "bold": True},
    "": {"fg": "red", "bold": True},
}
"""Style arguments for `click.style` to apply to echoed messages based on log level"""

LEVEL_PREFIXES: t.Dict[str, str] = {
    "debug": "-- ",
    "info": "** ",
    "warning": "++ ",
    "": "!! ",
}
"""Prefixes to add to echoed messages based on log level"""

STYLE_ARGS: t.List[str] = [
    "fg",
    "bg",
    "bold",
    "dim",
    "underline",
    "overline",
    "italic",
    "blink",
    "reverse",
    "strikethrough",
    "reset",
]
"""Valid args for `click.style`"""

ECHO_ARGS: t.List[str] = [
    "file",
    "nl",
    "err",
    "color",
]
"""Valid args for `click.echo`"""

ERROR: bool = True
"""Default value for `error` argument"""

ECHO: bool = False
"""Default value for `echo` argument"""

ECHO_STYLE: bool = True
"""Default for `style` argument for echoer."""

ECHO_PREFIX: bool = True
"""Default for `prefix` argument for echoer."""

ECHO_LOG: bool = True
"""Default for `log` argument for echoer."""

ECHO_STDERR: bool = True
"""Default for `stderr` argument for echoer."""

ECHO_LEVEL: str = "debug"
"""Default for `level` argument for echoer."""

ECHO_EXC_INFO: bool = True
"""Default for `exc_info` argument for echoer."""

RUN_INCLUDE_OUTPUT: bool = True
"""Default value for `include_output` argument used in runners"""

RUN_CAPTURE_OUTPUT: bool = True
"""Default value for `capture_output` argument used in runners"""

RUN_TEXT: bool = True
"""Default value for `text` argument used in runners"""

FLOW_ECHO: bool = True
"""Default value for `echo` argument used in workflows"""

FLOW_ECHO_VERBOSE: bool = False
"""Default value for `echo_checks` argument used in workflows"""

FLOW_ERROR: bool = True
"""Default value for `error` argument used in workflows"""

FLOW_ENV: bool = False
"""Default value for `env` argument used in workflows"""

FLOW_RUN: bool = True
"""Default value for `run` argument used in workflows"""

FLOW_RUN_LOGIN: bool = True
"""Default value for `login` argument used in workflows"""

FLOW_RUN_ACCESS: bool = True
"""Default value for `access` argument used in workflows"""

KEY_PREFIX: str = " " * 4
"""Prefix to use for keys in `dict_to_str`"""

CLI_LOGS: bool = False
"""Default value for `logs` argument used in cli"""

ACCESS_STDERR_CHECK: str = "login"
"""String to check for in stderr of `access token` command to determine if login is required

Line in STDERR of `access token` that means we need to run `access login`:
Unable to find token for provided application. Please run login command to generate token.
"""

ERR_RUN_ACCESS: str = "Failure while running `access token` command"
"""Error message used when `access token` command fails"""

ERR_RUN_LOGIN: str = "Failure while running `access login` command"
"""Error message used when `access login` command fails"""

ERR_RUN_ACCESS_LOGIN: str = "Failed to get token from `access token` or `access login` commands"
"""Error message used when `access token` or `access login` commands fail"""

ERR_TOKEN_ENV: str = "Failed while validating token OS env"
"""Error message used when validating token OS env fails"""

ERR_RUN_NONE: str = "Failed to get token from any method"
"""Error message used when all methods to get a token fail"""

ERR_TRY_URL: str = f"Try supplying url as {URL_ENVS_STR}"
"""Error message used when url is not supplied"""

ERR_FILE_NOT_FOUND: str = "Could not find"
"""Error message used when a file is not found"""

ERR_FILE_NOT_EXECUTABLE: str = "Found a non-executable"
"""Error message used when a file is not executable"""

ERR_TOKEN_FOUND: str = "Found a valid"
"""Error message used when a token is found and is valid"""

ERR_TOKEN_FOUND_INVALID: str = "Found an invalid"
"""Error message used when a token is found and is invalid"""

ERR_TOKEN_NOT_FOUND: str = "Did not find a valid"
"""Error message used when a token is not found"""

ERR_NO_LOGIN_STDERR: str = (
    f"Setting `run_login` to false because {ACCESS_STDERR_CHECK!r} not found in STDERR"
)
"""Error message used when 'login' is not found in STDERR"""

CLIENT_RUN: bool = False
"""Default value for `run` argument used in clients"""

CLIENT_DESC: str = "CLOUDFLARE ACCESS TOKEN: "
"""Description to add to click option for client"""

CLIENT_ERROR: bool = False
"""Default value for `error` argument used in clients"""

HELP_RUN: str = f"running the login command manually: {CMD_LOGIN_STR}"
"""Help text for `run` argument used in clients"""

HELP_REMOVE: str = f"removing the token in {TOKEN_ENVS_STR}"
"""Help text for invalid token"""

HELP_SET_ENV_FALSE: str = f"setting env to false"
"""Help text for invalid token"""

HELP_SET_RUN_TRUE: str = f"setting run to true"
"""Help text for invalid token"""

HELP_SET_RUN_LOGIN_TRUE: str = f"setting run_login to true"
"""Help text for invalid token"""

HELP_SET_RUN_ACCESS_TRUE: str = f"setting run_access to true"
"""Help text for invalid token"""

HELP_SET_ENV_TRUE: str = f"setting env to true and setting {TOKEN_ENVS_STR}"
"""Help text for invalid token"""

HELP_RUN_MANUAL: str = "running the following command manually:"
"""Help text for running cloudflared"""

LOG_START: str = "Start "
"""Prefix for log messages"""

LEVEL_ERROR_FALSE: str = "warning"
"""Log level to use when `error` is false"""

_CF_URL: str = "https://developers.cloudflare.com/cloudflare-one/connections/connect-apps"

_CF_MAC: str = """
Please ensure cloudflared is in your $PATH by trying these commands:

# To check if cloudflared is in your $PATH
which cloudflared

# To print your $PATH
echo $PATH

# To add cloudflared to your $PATH
export PATH="/path/to/cloudflared":$PATH

# To check if cloudflared is in your $PATH after updating it
which cloudflared

If cloudflared is not in your $PATH, please try installing cloudflared with the following command:
brew install cloudflared
"""

_CF_WIN: str = f"""
Please ensure cloudflared is in your %PATH% by trying these commands:

# To check if cloudflared is in your %PATH%
where cloudflared

# To print your %PATH%
echo %PATH%

# To add cloudflared to your %PATH%
SET PATH="C:\\path\\to\\cloudflared";%PATH%
    
If cloudflared is not in your %PATH%, please try installing cloudflared from the following URL:
{_CF_URL}/install-and-setup/installation/#windows
"""

_CF_NIX: str = f"""
Please ensure cloudflared is in your $PATH by trying these commands:

# To check if cloudflared is in your $PATH
which cloudflared

# To print your $PATH
echo $PATH

# To add cloudflared to your $PATH
PATH="/path/to/cloudflared":$PATH

# To check if cloudflared is in your $PATH after updating it
which cloudflared

If cloudflared is not in your %PATH%, please try installing cloudflared from the following URL:
  {_CF_URL}/install-and-setup/installation/#linux
"""

CF_INSTALL: str = _CF_WIN if IS_WINDOWS else _CF_MAC if IS_MAC else _CF_NIX
"""Command to install cloudflared for this particular OS."""
