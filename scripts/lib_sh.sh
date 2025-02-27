# -*- mode: sh; sh-shell: bash -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

## Definitions that make working with bash a little more comfortable

## Methods for simplified access to shell types

sh.list.is-in() {

    # usage: sh.list.is-in "two, three" mylist || echo "value is not in list"
    #
    # In the usage example mylist is an one-dimensional indexed array like:
    #
    #   mylist=("one" "one, two" "one, two, three")

    local -n arr=${2}

    for i in "${arr[@]}"
    do
    if [[ ${i} == "${1}" ]]; then
        return 0
    fi
    done
    return 1
}

## Methods to terminate the execution with a detailed error message

sh.prompt-err() {

    ## Use this as last command in your function to prompt an ERROR message if
    ## the exit code is not zero.

    local err=$1
    [ "$err" -ne "0" ] && msg.err "${FUNCNAME[1]} exit with error ($err)"
    return "$err"
}

sh.die() {
    msg.err "${BASH_SOURCE[1]}: line ${BASH_LINENO[0]}: ${2-died ${1-1}}"
    exit "${1-1}"
}

sh.die.caller() {
    msg.err "${BASH_SOURCE[2]}: line ${BASH_LINENO[1]}: ${FUNCNAME[1]}(): ${2-died ${1-1}}"
    exit "${1-1}"
}

sh.die.err() {
    msg.err "(${1-1}) ${2-died} "
    exit "${1-1}"
}


## Management of the shell libraries

SH_LIB_PATH="$(dirname "${BASH_SOURCE[0]}")"
SH_LIBS_IMPORTED=()

# in the bootstrap procedure the lib-msg and lib-tui is not yet imported
msg.debug() { [ "${V}" -ge 3 ] && echo -e "\e[0;33mDEBUG:\e[0m $*" >&2; }
msg.err()  { echo -e "\e[0;31mERROR:\e[0m $*" >&2; }

sh.lib.import() {

    local lib_path="${SH_LIB_PATH}/lib_${1}.sh"
    local caller="${BASH_SOURCE[1]}:${BASH_LINENO[0]}: ${FUNCNAME[0]} -"

    if sh.list.is-in "${lib_path}" SH_LIBS_IMPORTED; then
    msg.debug "[sh.lib.import] ${caller} skip already sourced ${lib_path}"
    return 0
    fi

    msg.debug "[sh.lib.import] ${caller} source ${lib_path}"
    SH_LIBS_IMPORTED+=("${lib_path}")
    # shellcheck source=/dev/null
    source "${lib_path}" || sh.die.caller 42 "[sh.lib.import] ${lib_path} not found"

    if [[ $(type -t "${1}.init") == function ]]; then
    msg.debug "[sh.lib.import] ${1}.init()"
    "${1}.init"
    else
    msg.debug "[sh.lib.import] lib_${1}.sh has no ${1}.init()"
    fi
}
