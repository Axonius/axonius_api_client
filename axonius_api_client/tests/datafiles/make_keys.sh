#!/bin/bash -e

# Reset
Color_Off='\033[0m'       # Text Reset

# Regular Colors
Black='\033[0;30m'        # Black
Red='\033[0;31m'          # Red
Green='\033[0;32m'        # Green
Yellow='\033[0;33m'       # Yellow
Blue='\033[0;34m'         # Blue
Purple='\033[0;35m'       # Purple
Cyan='\033[0;36m'         # Cyan
White='\033[0;37m'        # White

# Bold
BBlack='\033[1;30m'       # Black
BRed='\033[1;31m'         # Red
BGreen='\033[1;32m'       # Green
BYellow='\033[1;33m'      # Yellow
BBlue='\033[1;34m'        # Blue
BPurple='\033[1;35m'      # Purple
BCyan='\033[1;36m'        # Cyan
BWhite='\033[1;37m'       # White

OPENSSL_BIN=$(which openssl)
ROOT="rsa_root_ca"
ROOT_DAYS=1024
ROOT_KEY_SIZE=2048
ROOT_KEY="${ROOT}.key"
ROOT_CRT="${ROOT}.crt"
ROOT_COUNTRY="US"
ROOT_STATE="New York"
ROOT_LOCALITY="New York City"
ROOT_ORG="Axonius, Inc"
ROOT_OU="${ROOT}"
ROOT_CN="${ROOT}"
ROOT_EMAIL="support@axonius.com"
ROOT_SUBJECT="/C=${ROOT_COUNTRY}/ST=${ROOT_STATE}/L=${ROOT_LOCALITY}/O=${ROOT_ORG}/OU=${ROOT_OU}/CN=${ROOT_CN}/emailAddress=${ROOT_EMAIL}"
ROOT_KEY_ARGS=(
    "genrsa"
    "-out" "${ROOT_KEY}"
    "${ROOT_KEY_SIZE}"
)
ROOT_CRT_ARGS=(
    "req"
    "-x509"
    "-new"
    "-nodes"
    "-sha256"
    "-subj" "${ROOT_SUBJECT}"
    "-key" "${ROOT_KEY}"
    "-days" "${ROOT_DAYS}"
    "-out" "${ROOT_CRT}"
    "-addext" "basicConstraints = critical,CA:TRUE"
    "-addext" "subjectAltName = DNS:${ROOT_CN}"
    "-addext" "keyUsage = digitalSignature,keyAgreement,keyCertSign,cRLSign"
    "-addext" "extendedKeyUsage = serverAuth,clientAuth"
)

function echo_ok(){ echo -e "${BGreen}${@}${Color_Off}" 1>&2; }
function echo_debug(){ echo -e "${Blue}${@}${Color_Off}" 1>&2; }
function echo_err(){ echo -e "${Bred}${@}${Color_Off}" 1>&2; }
function echo_warn(){ echo -e "${BYellow}${@}${Color_Off}" 1>&2; }

function echo_cert(){
    file="${1}"
    ARGS=(
        "x509"
        "-text"
        "-in" "${file}"
        "-noout"
    )
    echo_ok "Displaying cert ${file}"
    echo_debug "command: ${OPENSSL_BIN}" "${ARGS[@]}"
    ${OPENSSL_BIN} "${ARGS[@]}"
    echo_ok "Displayed cert ${file}"
}

echo_ok "Generating ${ROOT_KEY}"
echo_debug "command: ${OPENSSL_BIN}" "${ROOT_KEY_ARGS[@]}"
${OPENSSL_BIN} "${ROOT_KEY_ARGS[@]}"
echo_ok "Generated ${ROOT_KEY}"

echo_ok "Generating ${ROOT_CRT}"
echo_debug "command: ${OPENSSL_BIN} ${ROOT_CRT_ARGS[@]}"
${OPENSSL_BIN} "${ROOT_CRT_ARGS[@]}"
echo_ok "Generated ${ROOT_CRT}"

echo_cert "${ROOT_CRT}"

# openssl req \
#     -x509 \
#     -nodes \
#     -days 365 \
#     -newkey rsa:2048 \
#     -subj "/C=US/ST=New York/L=New York City/O=Axonius, Inc/OU=axonius/CN=axonius/emailAddress=support@axonius.com" \
#     -addext "subjectAltName = DNS:axonius" \
#     -keyout axonius_with_san.key \
#     -out axonius_with_san.crt

# openssl req \
#     -x509 \
#     -nodes \
#     -days 365 \
#     -newkey rsa:2048 \
#     -subj "/C=US/ST=New York/L=New York City/O=Axonius, Inc/OU=axonius/CN=axonius/emailAddress=support@axonius.com" \
#     -keyout axonius_no_san.key \
#     -out axonius_no_san.crt

# # Create rootCA Certificate - this command works only on posix machines or WSL on windows
# openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.crt
# # Sign the csr with our rootCA
# openssl x509 -req -in cert.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out cert.crt -days 500 -sha256


# -copy_extensions copy
# If arg is none or this option is not present then extensions are ignored.
# If arg is copy or copyall then all extensions in the request are copied to the certificate.
