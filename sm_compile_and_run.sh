#!/usr/bin/env bash
set -e

if [ "x${SHAREMIND_CONFIG_PATH}" = "x" ]; then
    SHAREMIND_CONFIG_PATH="/etc/sharemind"
fi

if [ "x${SHAREMIND_INSTALL_PATH}" = "x" ]; then
    SHAREMIND_INSTALL_PATH="/usr"
fi

echo "Using SHAREMIND_CONFIG_PATH='${SHAREMIND_CONFIG_PATH}'"
echo "Using SHAREMIND_INSTALL_PATH='${SHAREMIND_INSTALL_PATH}'"

SCC="${SHAREMIND_INSTALL_PATH}/bin/scc"
SHAREMIND_RUNSCRIPT="${SHAREMIND_INSTALL_PATH}/bin/sharemind-runscript"
STDLIB="${SHAREMIND_INSTALL_PATH}/lib/sharemind/stdlib"
SCRIPT_PATH="${SHAREMIND_CONFIG_PATH}/scripts"
USER=`whoami`
CLIENT_PATH="${SHAREMIND_CONFIG_PATH}/client"
CLIENT_CONF_FILE="client.conf"
MPC_SERVERS=`grep "Address=" < ${CLIENT_PATH}/${CLIENT_CONF_FILE} | awk -F = '{print $2}'`

if [ $# -eq 0 ]; then
    echo "No arguments given."
    exit 1
fi

for SC in "$@"; do
    if [ ! -e "${SC}" ]; then
        echo "File '${SC}' does not exist" && false
    fi

    SC_ABSS=`readlink -f "${SC}"`

    [ -f "${SC_ABSS}" ]

    SC_ABSSP=`dirname "${SC_ABSS}"`
    SC_BN=`basename "${SC}"`
    SB_BN=`echo "${SC_BN}" | sed 's/sc$//' | sed 's/$/sb/'`

    SB=`mktemp -t "${SB_BN}.XXXXXXXXXX"`

    echo "Compiling: '${SC}' to '${SB}'"
    "${SCC}" --include "${STDLIB}" --include "${SC_ABSSP}" --input "${SC}" --output "${SB}"

    for SERVER in ${MPC_SERVERS}; do
        echo "Installing: '${SB}' to '${SERVER}:${SCRIPT_PATH}/${SB_BN}'"
        scp "${SB}" "${USER}@${SERVER}:${SCRIPT_PATH}/${SB_BN}"
    done

    rm -f "${SB}"

    echo "Running: '${SB}'"
    (cd "${CLIENT_PATH}" && "${SHAREMIND_RUNSCRIPT}" --run "${SB_BN}" --conf "${CLIENT_CONF_FILE}")
done
