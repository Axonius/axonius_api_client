OPENSSL_BIN=$(which openssl)

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


function echo_ok(){ echo -e "${BGreen}${@}${Color_Off}" 1>&2; }
function echo_debug(){ echo -e "${Blue}${@}${Color_Off}" 1>&2; }
function echo_err(){ echo -e "${Bred}${@}${Color_Off}" 1>&2; }
function echo_warn(){ echo -e "${BYellow}${@}${Color_Off}" 1>&2; }

function echo_cert(){
    file="${1}"
    details=$("${OPENSSL_BIN}" x509 -in "${file}" -noout -subject -issuer -ext subjectAltName)
    echo_ok "${file} details:\n${details}"
}
function echo_csr(){
    file="${1}"
    details=$("${OPENSSL_BIN}" req -in "${file}" -noout -subject)
    echo_ok "${file} details:\n${details}"
}

function pem_to_pkcs7(){
    pem="${1}"
    p7b="${2}"
    certfile="${3}"
    "${OPENSSL_BIN}" crl2pkcs7 -nocrl -certfile "${pem}" -out "${p7b}" -certfile "${certfile}"
    echo_ok "Converted PEM ${pem} to PKCS7 ${p7b}"
}
