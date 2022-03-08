#!/bin/bash -e
# FUTURE: turn into python
# ref: https://knowledge.digicert.com/solution/SO26449.html
SERVER_IP="${1}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERTS_DIR="${SCRIPT_DIR}/certs"

test -z "${SERVER_IP}" && echo "must provide build server IP" && exit 1

source ${SCRIPT_DIR}/common.sh
test ! -x "${OPENSSL_BIN}" && echo "openssl bin ${OPENSSL_BIN} not found" && exit 1

mkdir -p "${CERTS_DIR}"


ARG_DAYS=1024
ARG_RSA_KEY_SIZE=2048
ARG_EC_NAME="prime256v1"

SUBJECT_COUNTRY="US"
SUBJECT_STATE="New York"
SUBJECT_LOCALITY="New York City"
SUBJECT_ORG="Axonius, Inc"
SUBJECT_EMAIL="support@axonius.com"
SUBJECT_BASE="/C=${SUBJECT_COUNTRY}/ST=${SUBJECT_STATE}/L=${SUBJECT_LOCALITY}/O=${SUBJECT_ORG}"

SUBJECT_CA_OU="axonius_ca_ou"
SUBJECT_CA_CN="axonius_ca_cn"
SUBJECT_CA="${SUBJECT_BASE}/OU=${SUBJECT_CA_OU}/CN=${SUBJECT_CA_CN}/emailAddress=${SUBJECT_EMAIL}"

SUBJECT_SERVER_OU="axonius_server_ou"
SUBJECT_SERVER_CN="axonius"
SUBJECT_SERVER="${SUBJECT_BASE}/OU=${SUBJECT_SERVER_OU}/CN=${SUBJECT_SERVER_CN}/emailAddress=${SUBJECT_EMAIL}"

# >>> RSA
RSA_CA_BASE="${CERTS_DIR}/ca_rsa"
RSA_CA_KEY_FILE="${RSA_CA_BASE}.key"
RSA_CA_CERT_FILE="${RSA_CA_BASE}.crt.pem"

RSA_SERVER_BASE="${CERTS_DIR}/server_rsa"
RSA_SERVER_CSR_FILE="${RSA_SERVER_BASE}.csr.pem"
RSA_SERVER_KEY_FILE="${RSA_SERVER_BASE}.key"
RSA_SERVER_CERT_FILE="${RSA_SERVER_BASE}.crt.pem"
RSA_SERVER_CERT_PKCS7_FILE="${RSA_SERVER_BASE}.crt.p7b"

# --- RSA CA
echo_debug "\n\t\tNow generating RSA certs\n"

echo_debug "Generating ${RSA_CA_KEY_FILE}"
"${OPENSSL_BIN}" genrsa -out "${RSA_CA_KEY_FILE}" "${ARG_RSA_KEY_SIZE}"
echo_ok "Generated ${RSA_CA_KEY_FILE}"

echo_debug "Generating ${RSA_CA_CERT_FILE}"
"${OPENSSL_BIN}" req -x509 -new -nodes -sha256 \
    -key "${RSA_CA_KEY_FILE}" \
    -out "${RSA_CA_CERT_FILE}" \
    -days "${ARG_DAYS}" \
    -subj "${SUBJECT_CA}" \
    -addext "basicConstraints = critical,CA:TRUE" \
    -addext "subjectAltName = DNS:axonius" \
    -addext "keyUsage = digitalSignature,keyAgreement,keyCertSign,cRLSign" \
    -addext "extendedKeyUsage = serverAuth,clientAuth"
echo_cert "${RSA_CA_CERT_FILE}"

echo_debug "Generating ${RSA_SERVER_KEY_FILE}"
"${OPENSSL_BIN}" genrsa -out "${RSA_SERVER_KEY_FILE}" "${ARG_RSA_KEY_SIZE}"
echo_ok "Generated ${RSA_SERVER_KEY_FILE}"

# --- RSA SERVER
echo_debug "Generating ${RSA_SERVER_CSR_FILE}"
"${OPENSSL_BIN}" req -new -nodes -sha256 \
    -key "${RSA_SERVER_KEY_FILE}" \
    -out "${RSA_SERVER_CSR_FILE}" \
    -subj "${SUBJECT_SERVER}" \
    -addext "subjectAltName = IP:${SERVER_IP}" \
    -addext "keyUsage = digitalSignature,keyAgreement" \
    -addext "extendedKeyUsage = serverAuth,clientAuth"
echo_csr "${RSA_SERVER_CSR_FILE}"

echo_debug "Generating ${RSA_SERVER_CERT_FILE}"
"${OPENSSL_BIN}" x509 -req \
    -in "${RSA_SERVER_CSR_FILE}" \
    -out "${RSA_SERVER_CERT_FILE}" \
    -CA "${RSA_CA_CERT_FILE}" \
    -CAkey "${RSA_CA_KEY_FILE}" \
    -set_serial 0x$("${OPENSSL_BIN}" rand -hex 19) \
    -days "${ARG_DAYS}" \
    -copy_extensions copy
echo_cert "${RSA_SERVER_CERT_FILE}"
pem_to_pkcs7 "${RSA_SERVER_CERT_FILE}" "${RSA_SERVER_CERT_PKCS7_FILE}" "${RSA_CA_CERT_FILE}"
# <<< RSA

# >>> EC
echo_debug "\n\t\tNow generating EC certs\n"
EC_CA_BASE="${CERTS_DIR}/ca_ec"
EC_CA_KEY_FILE="${EC_CA_BASE}.key"
EC_CA_CERT_FILE="${EC_CA_BASE}.crt.pem"

EC_SERVER_BASE="${CERTS_DIR}/server_ec"
EC_SERVER_CSR_FILE="${EC_SERVER_BASE}.csr.pem"
EC_SERVER_KEY_FILE="${EC_SERVER_BASE}.key"
EC_SERVER_CERT_FILE="${EC_SERVER_BASE}.crt.pem"
EC_SERVER_CERT_PKCS7_FILE="${EC_SERVER_BASE}.crt.p7b"

# --- EC CA
echo_debug "Generating ${EC_CA_KEY_FILE}"
"${OPENSSL_BIN}" ecparam -genkey -out "${EC_CA_KEY_FILE}" -name "${ARG_EC_NAME}"
echo_ok "Generated ${EC_CA_KEY_FILE}"

echo_debug "Generating ${EC_CA_CERT_FILE}"
"${OPENSSL_BIN}" req -x509 -new -nodes -sha256 \
    -key "${EC_CA_KEY_FILE}" \
    -out "${EC_CA_CERT_FILE}" \
    -days "${ARG_DAYS}" \
    -subj "${SUBJECT_CA}" \
    -addext "basicConstraints = critical,CA:TRUE" \
    -addext "subjectAltName = DNS:axonius" \
    -addext "keyUsage = digitalSignature,keyAgreement,keyCertSign,cRLSign" \
    -addext "extendedKeyUsage = serverAuth,clientAuth"
echo_cert "${EC_CA_CERT_FILE}"

# --- EC SERVER
echo_debug "Generating ${EC_SERVER_KEY_FILE}"
"${OPENSSL_BIN}" ecparam -genkey -out "${EC_SERVER_KEY_FILE}" -name "${ARG_EC_NAME}"
echo_ok "Generated ${EC_SERVER_KEY_FILE}"

echo_debug "Generating ${EC_SERVER_CSR_FILE}"
"${OPENSSL_BIN}" req -new -nodes -sha256 \
    -key "${EC_SERVER_KEY_FILE}" \
    -out "${EC_SERVER_CSR_FILE}" \
    -subj "${SUBJECT_SERVER}" \
    -addext "subjectAltName = IP:${SERVER_IP}" \
    -addext "keyUsage = digitalSignature,keyAgreement" \
    -addext "extendedKeyUsage = serverAuth,clientAuth"
echo_csr "${EC_SERVER_CSR_FILE}"

echo_debug "Generating ${EC_SERVER_CERT_FILE}"
"${OPENSSL_BIN}" x509 -req \
    -in "${EC_SERVER_CSR_FILE}" \
    -out "${EC_SERVER_CERT_FILE}" \
    -CA "${EC_CA_CERT_FILE}" \
    -CAkey "${EC_CA_KEY_FILE}" \
    -set_serial 0x$("${OPENSSL_BIN}" rand -hex 19) \
    -days "${ARG_DAYS}" \
    -copy_extensions copy
echo_cert "${EC_SERVER_CERT_FILE}"
pem_to_pkcs7 "${EC_SERVER_CERT_FILE}" "${EC_SERVER_CERT_PKCS7_FILE}" "${EC_CA_CERT_FILE}"
# <<< EC
