#!/bin/bash

# Copyright (C) Axonius
# Script Provided without warranty


# Script info
SCRIPT_FULL_PATH="$(realpath "${0}")"
SCRIPT_NAME="$(basename "${SCRIPT_FULL_PATH%.*}")"
SCRIPT_VERSION="1.0"


# Misc commands
MAKE_LOG_WORKING_DIRECTORY="mkdir -p ${LOG_FILE_DATED}"
SET_YELLOW_PROMPT="tput setaf 3"
SET_NORMAL_PROMPT="tput setaf 9"
CURRENT_DIRECTORY="$(pwd)"
BUILD_DIRECTORY=$CURRENT_DIRECTORY/${SCRIPT_NAME}_build

# Messages
BR="echo"
INSTANCE_ALREADY_RUNNING="An instance of ${SCRIPT_NAME} is already running.\n"
RUN_AS_ROOT_MESSAGE="${SCRIPT_NAME} must be run as root."
SCRIPT_COMPLETE_MESSAGE="Complete."

declare -i IS_REDHAT
IS_REDHAT=$(rpm -qf /etc/redhat-release | grep -c redhat)


# Installer script
IFS='' read -r -d '' INSTALLER <<"EOF"
#!/bin/bash

# Copyright (C) Axonius
# Script Provided without warranty


# Script info
SCRIPT_FULL_PATH="$(realpath "${0}")"
SCRIPT_NAME="$(basename "${SCRIPT_FULL_PATH%.*}")"
SCRIPT_VERSION="1.0"


# Misc commands
MAKE_LOG_WORKING_DIRECTORY="mkdir -p ${LOG_FILE_DATED}"
SET_YELLOW_PROMPT="tput setaf 3"
SET_NORMAL_PROMPT="tput setaf 9"


# Messages
BR="echo"
INSTANCE_ALREADY_RUNNING="An instance of ${SCRIPT_NAME} is already running.\n"
RUN_AS_ROOT_MESSAGE="${SCRIPT_NAME} must be run as root."
SCRIPT_COMPLETE_MESSAGE="Complete."

# Variables
PIP_CMD=

declare -i PIP_EXISTS
PIP_EXISTS=$(command -v pip3 | wc -l)


### Helper Functions

die() {
    declare -i EXIT_CODE
    EXIT_CODE=${1}

    [ "${EXIT_CODE}" == "" ] && exit 1 || exit "${EXIT_CODE}"
}

function catch() {
    ${BR}
    ${SET_NORMAL_PROMPT}
    rm -f "/var/tmp/${SCRIPT_NAME}.lock"
    ${DELETE_LOG_WORKING_DIRECTORY}
    die 255
}

function continueExitDialog() {
    PS3="Select the item number: "
    ${SET_YELLOW_PROMPT}
    echo "${1}"
    ${BR}

    select action in Continue Exit
    do
        case "${action}" in
        Continue)
            ${BR}
            break;;
        Exit)
            die 0;;
        *)
            echo "Invalid selection";;
        esac
    done
    ${SET_NORMAL_PROMPT} # Set prompt to normal
}

function help() {
declare MSG

MSG=$(cat <<-END
Usage: ${SCRIPT_NAME} [OPTION...]

Installer for the offline install of the Axonius API Client.

General options.
  -h, --help\t\t\tShow this message
  -v, --version\t\t\tDisplay version information
END
)

echo -e "${MSG}"
}

function version() {
declare MSG

MSG=$(cat <<-END
${SCRIPT_NAME} v${SCRIPT_VERSION}
Copyright (C) 2021 Axonius

Provided "As-is", and without warranty.
END
)

echo -e "${MSG}"
}

function incorrectOption() {
declare MSG

MSG=$(cat <<-END
${SCRIPT_NAME}: invalid option "${1}"
Try '${SCRIPT_NAME} --help' for more information.
END
)

echo -e "${MSG}"
echo
}


### Main Body

if [ ! ${#} -eq 0 ]; then
    for arg in "${@}"; do
       case $arg in
          -h | --help) # display Help
             help # Call the help function above
             die 0;;
         -v | --version)
             version # Call the version function above
             die 0;;
         *) # incorrect option
             incorrectOption "${arg}" # Call incorrectOption above
             die 0;;
       esac
    done
fi

# Create lock to ensure only one instance runs at a time, limit resource concurrency issues
exec 100>/var/tmp/"${SCRIPT_NAME}".lock || die 255
if ! flock -n 100; then
    ${SET_YELLOW_PROMPT} # Set text yellow text
    echo -e "${INSTANCE_ALREADY_RUNNING}"
    ${SET_NORMAL_PROMPT} # Set prompt to normal
    die 255
fi

# Cleanup on exit. In order; blank line, set text normal, delete lock file, exit abnormally
trap 'catch' SIGINT SIGTERM ERR EXIT

# Ensure the script is ran as root
if [[ ${EUID} -ne 0 ]]; then
   ${SET_YELLOW_PROMPT}
   echo "${RUN_AS_ROOT_MESSAGE}"
   die 255
fi

if [ "${PIP_EXISTS}" -eq "1" ]; then
    PIP_CMD=pip3
else
    echo "Please install pip3 and run this script again."
    die 255
fi

tar xzvf openssl.tar.gz -C /
${PIP_CMD} install --no-index --find-links wheel_files cryptography axonius-api-client

# Done, tell user where to find the output
printf "%s" "${SCRIPT_COMPLETE_MESSAGE}"

EOF


### Helper Functions

die() {
    declare -i EXIT_CODE
    EXIT_CODE=${1}

    [ "${EXIT_CODE}" == "" ] && exit 1 || exit "${EXIT_CODE}"
}

function catch() {
    ${BR}
    ${SET_NORMAL_PROMPT}
    rm -f "/var/tmp/${SCRIPT_NAME}.lock"
    #rm -rf ${BUILD_DIRECTORY}
    cd ${CURRENT_DIRECTORY}
}

function continueExitDialog() {
    PS3="Select the item number: "
    ${SET_YELLOW_PROMPT}
    echo "${1}"
    ${BR}

    select action in Continue Exit
    do
        case "${action}" in
        Continue)
            ${BR}
            break;;
        Exit)
            die 0;;
        *)
            echo "Invalid selection";;
        esac
    done
    ${SET_NORMAL_PROMPT} # Set prompt to normal
}

function help() {
declare MSG

MSG=$(cat <<-END
Usage: ${SCRIPT_NAME} [OPTION...]

Creates install package for offline install of the Axonius API Client.

General options.
  -h, --help\t\t\tShow this message
  -v, --version\t\t\tDisplay version information
END
)

echo -e "${MSG}"
}

function version() {
declare MSG

MSG=$(cat <<-END
${SCRIPT_NAME} v${SCRIPT_VERSION}
Copyright (C) 2021 Axonius

Provided "As-is", and without warranty.
END
)

echo -e "${MSG}"
}

function incorrectOption() {
declare MSG

MSG=$(cat <<-END
${SCRIPT_NAME}: invalid option "${1}"
Try '${SCRIPT_NAME} --help' for more information.
END
)

echo -e "${MSG}"
echo
}


function run() {
    # Declare local vars
    declare IFS
    declare FULL_COMMAND
    declare EXE
    declare ARGS
    declare RESULT

    IFS=' '
    FULL_COMMAND="${*:1:$#}"
    EXE="${1}"
    ARGS="${*:2:$#-1}"
    RESULT=0

    # Log the command that is about to run
    echo "RUNNING COMMAND: ${FULL_COMMAND}"
    echo "###"

    # Run the command and output both stderr and stdin to the log file
    # Word-splitting ARGS on purpose, suppressing shellcheck warning on next line
    # shellcheck disable=SC2086
    "${EXE}" ${ARGS}

    RESULT="${?}"

    if [ ! "${RESULT}" -eq "0" ]; then
        echo "Critical Error, ${FULL_COMMAND} failed with an exit value of ${RESULT}." | tee -a "${LOG_FILE}"
    fi

    echo "###"
}

### Main Body

if [ ! ${#} -eq 0 ]; then
    for arg in "${@}"; do
       case $arg in
          -h | --help) # display Help
             help # Call the help function above
             die 0;;
         -v | --version)
             version # Call the version function above
             die 0;;
         *) # incorrect option
             incorrectOption "${arg}" # Call incorrectOption above
             die 0;;
       esac
    done
fi

# Create lock to ensure only one instance runs at a time, limit resource concurrency issues
exec 100>/var/tmp/"${SCRIPT_NAME}".lock || die 255
if ! flock -n 100; then
    ${SET_YELLOW_PROMPT} # Set text yellow text
    echo -e "${INSTANCE_ALREADY_RUNNING}"
    ${SET_NORMAL_PROMPT} # Set prompt to normal
    die 255
fi

# Cleanup on exit. In order; blank line, set text normal, delete lock file, exit abnormally
trap 'catch' SIGINT SIGTERM ERR EXIT

# Ensure the script is ran as root
if [[ ${EUID} -ne 0 ]]; then
   ${SET_YELLOW_PROMPT}
   echo "${RUN_AS_ROOT_MESSAGE}"
   die 255
fi

mkdir -p ${BUILD_DIRECTORY} && cd ${BUILD_DIRECTORY}
yum groupinstall -y "Development Tools"

if [ "${IS_REDHAT}" -eq "1" ]; then
    yum -y --enablerepo=rhel-7-server-optional-rpms install python3 python3-devel libffi-devel wget curl
else
    yum install -y python3 python3-devel libffi-devel wget curl
fi

wget -O rustup.sh https://sh.rustup.rs
sh rustup.sh -y
source $HOME/.cargo/env

set -e
OPENSSL_VERSION="1.1.1j"
CWD=$(pwd)
python3 -m venv py36-venv
source py36-venv/bin/activate
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -U setuptools wheel
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -U setuptools_rust
curl -k -O https://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz
tar xvf openssl-${OPENSSL_VERSION}.tar.gz
cd openssl-${OPENSSL_VERSION}
mkdir -p /opt/openssl_${OPENSSL_VERSION}
./config no-shared no-ssl2 no-ssl3 -fPIC --prefix=/opt/openssl_${OPENSSL_VERSION}/openssl
make && make install
CFLAGS="-I/opt/openssl_${OPENSSL_VERSION}/openssl/include" LDFLAGS="-L/opt/openssl_${OPENSSL_VERSION}/openssl/lib" pip3 wheel --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-binary :all: cryptography

mkdir -p offline_axonius_api_client_installer/wheel_files
mv *.whl offline_axonius_api_client_installer/wheel_files
pip3 download -d offline_axonius_api_client_installer/wheel_files axonius-api-client==4.2.2

echo "${INSTALLER}" > offline_axonius_api_client_installer/offline_axonius_api_client_installer.sh
chmod u+x offline_axonius_api_client_installer/offline_axonius_api_client_installer.sh
tar czvf offline_axonius_api_client_installer/openssl.tar.gz -P /opt/openssl_${OPENSSL_VERSION}
tar czvf ${CURRENT_DIRECTORY}/offline_axonius_api_client_installer.tar.gz offline_axonius_api_client_installer

# Done, tell user where to find the output
printf "\n%s" "${SCRIPT_COMPLETE_MESSAGE}"
