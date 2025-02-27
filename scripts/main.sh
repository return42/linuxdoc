#!/usr/bin/env bash
# -*- mode: sh; sh-shell: bash -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

_REQUIREMENTS=( "${_REQUIREMENTS[@]}" )
SH_LIB_PATH="$(dirname "${BASH_SOURCE[0]}")"

MAIN="$(basename "$0")"

MAIN_CMD_LIST=
## MAIN_CMD_LIST: Array with functions available from the command line
#
# Assume you have a function (incl. help)::
#
#   foobar.help() {
#       $FMT <<EOF
#   prints first and second argument to stdout
#
#     usage:
#       ${MAIN} ${MAIN_CMD}
#
#   Just a demo how to implement a function wich is available in the command line
#   EOF
#   }
#   foobar() { echo "prompt from foobar -> $1 $2"; }
#
# and a group 'foo' of functions::
#
#   foo.foo.help() { echo "prints first argument to stdout"; }
#   foo.foo() { echo "prompt from foo.foo -> $1"; }
#   foo.bar.help() { echo "prints second argument to stdout"; }
#   foo.bar() { echo "prompt from foo.foo -> $1"; }
#
# To move these functions to the command line define::
#
#   MAIN_CMD_LIST=(
#       "foo: foo.foo foo.bar"
#       "foobar"
#   )
#
# With the setup from above the output of --help looks like::
#
#   $ ./myscript --help
#   usage:
#      myscript [<option>, ..] cmd
#   foo.:
#     foo         : prints first argument to stdout
#     bar         : prints second argument to stdout
#   foobar        : prints first and second argument to stdout
#
#  $ ./myscript foobar --help
#  Prints first and second argument to stdout.
#
#   usage: lxc-suite prepare
#
#  Just a demo how to implement a function wich is available in the
#  command line.

V="${V:=0}"

# shellcheck source=./lib_sh.sh
source "${SH_LIB_PATH}/lib_sh.sh"

sh.lib.import msg

main.usage() {
    cat <<EOF
usage:
   ${MAIN} [<option>, ..] cmd
EOF
}

main.source.config() {
    # usage: main.source.config lxc-incus.env
    local cfg
    [ -z "${1}" ] && msg.err "missing config file name" && return 42

    if [[ -e "./${1}" ]]; then
    cfg="./${1}"
    elif [[ -e "/etc/${1}" ]]; then
    cfg="/etc/${1}"
    else
    cfg="$(cd "$(dirname "${BASH_SOURCE[0]}")/../etc" && pwd -P)/${1}"
    if [[ ! -e "${cfg}" ]]; then
        unset cfg
    fi
    fi

    if [ -n "${cfg}" ]; then
    msg.debug "source config from: ${cfg}"
    # shellcheck disable=SC1090
    source "${cfg}"
    else
    msg.debug "config file not found: ${1}"
    fi
}

main.cmd_list() {

    if [ -z "${MAIN_CMD_LIST}" ]; then
    echo -n "commands:"
    # shellcheck disable=SC1083
    MSG_INDENT=1 msg.para "$(declare -F | awk {'print $3'})"
    return 0
    fi

    local grp grp_cmds grp_name cmd
    for grp in "${MAIN_CMD_LIST[@]}"; do
    grp_name=''
    read -r -a grp_cmds <<< "${grp}"
    if [[ ${grp_cmds[0]} == *: ]]; then
        grp_name="${grp_cmds[0]}"
        grp_name="${grp_name%:}"
        unset -v 'grp_cmds[0]'
        echo "${grp_name}.:"
    fi
    for cmd in "${grp_cmds[@]}"; do
        main.cmd.descr "${cmd}" "${grp_name}"
    done
    done
}

main.cmd.descr() {
    # usage: main.cmd.descr foo.bar foo
    local t h
    t="$(type -t "${1}")"
    if [ "${t}" == 'function' ]; then
    h=''
    t="$(type -t "${1}.help")"
        if [ "${t}" == 'function' ]; then
        h="$("${1}.help" | sed -n '1p')"
    fi
    if [[ ${1} == ${2}.* ]]; then
        printf "  %-12s: %s\n" "${1#"${2}".}" "${h}"
    else
        printf "%-14s: %s\n" "$1" "${h}"
    fi
    fi
}

main.usage.options() {
    cat <<EOF
globale options:
  --getenv    : inspect environment variable
  --help      : show this help message
EOF
}

help() {
    # Function help is intended to be overwritten by the script, that sources
    # main.sh
    main.usage
    main.cmd_list
    main.usage.options
}

main() {

    scripts.requires "${_REQUIREMENTS[@]}" || sh.die.err $? "first install missing requirements"
    local _type
    local cmd="$1"; shift

    [ "${V}" -ge 5 ] && set -x

    if [ "$cmd" == "" ]; then
        help
        msg.err "missing command"
        return 42
    fi

    # shellcheck disable=SC2034
    MAIN_CMD="${cmd}"

    case "$cmd" in
        --getenv) var="$1"; echo "${!var}";;
        --help) help;;
        --*)
            help
            msg.err "unknown option $cmd"
            return 42
            ;;
        *)
            _type="$(type -t "$cmd")"
            if [ "$_type" != 'function' ]; then
                msg.err "unknown command: $cmd / use --help"
                return 42
            else
        if [ "${1}" == '--help' ]; then
            "${cmd}.help"
        else
            [ "${V}" -ge 4 ] && set -x
                    "$cmd" "$@"
        fi
            fi
            ;;
    esac
}

scripts.requires() {

    # usage:  main.requires [cmd1 ...]

    local exit_val=0
    while [ -n "${1}" ]; do

        if ! command -v "${1}" &>/dev/null; then
            msg.err "missing command ${1}"
            exit_val=42
        fi
        shift
    done
    return $exit_val
}
