# -*- mode: sh; sh-shell: bash -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

tui.init() {
    if [ ! -p /dev/stdout ] && [ ! "${TERM}" = 'dumb' ] && [ ! "${TERM}" = 'unknown' ]; then
    tui.colors
    fi
}

# shellcheck disable=SC2034
tui.colors() {
    # https://en.wikipedia.org/wiki/ANSI_escape_code

    # CSI (Control Sequence Introducer) sequences
    _show_cursor='\e[?25h'
    _hide_cursor='\e[?25l'

    # SGR (Select Graphic Rendition) parameters
    _creset='\e[0m'  # reset all attributes

    # original specification only had 8 colors
    _colors=8

    _Black='\e[0;30m'
    _White='\e[1;37m'
    _Red='\e[0;31m'
    _Green='\e[0;32m'
    _Yellow='\e[0;33m'
    _Blue='\e[0;94m'
    _Violet='\e[0;35m'
    _Cyan='\e[0;36m'

    _BBlack='\e[1;30m'
    _BWhite='\e[1;37m'
    _BRed='\e[1;31m'
    _BGreen='\e[1;32m'
    _BYellow='\e[1;33m'
    _BBlue='\e[1;94m'
    _BPurple='\e[1;35m'
    _BCyan='\e[1;36m'
}

stdin.clean() {
    while read -r -n1 -t 0.1; do : ; done
}

ui.press-key() {

    # usage: ui.press-key [<timeout in sec>]
    #
    # In batch processes without user interaction, the timeout is overwritten by
    # ${FORCE_TIMEOUT}.  The default prompt message is overwritten by ${MSG}.

    stdin.clean
    local _t=$1
    local msg="${MSG}"
    [[ -z "$msg" ]] && msg="${_Green}** press any [${_BCyan}KEY${_Green}] to continue **${_creset}"

    [[ -n $FORCE_TIMEOUT ]] && _t=$FORCE_TIMEOUT
    [[ -n $_t ]] && _t="-t $_t"
    echo -e -n "$msg"
    # shellcheck disable=SC2229
    # shellcheck disable=SC2086
    read -r -s -n1 $_t || true
    echo
    stdin.clean
}

ui.yes-no() {

    # usage: ask_yn <prompt-text> [Ny|Yn] [<timeout in sec>]
    #
    # - Ny: default is NO
    # - Yn: default is YES
    #
    # If the timeout is exceeded, the default is selected.  In batch processes
    # without user interaction, the timeout can be overwritte by
    # ${FORCE_TIMEOUT} environment.

    local EXIT_YES=0 # exit status 0 --> successful
    local EXIT_NO=1  # exit status 1 --> error code

    local _t=${3}
    [[ -n ${FORCE_TIMEOUT} ]] && _t=${FORCE_TIMEOUT}
    [[ -n ${_t} ]] && _t="-t ${_t}"

    case "${FORCE_SELECTION:-${2}}" in
        Y) return ${EXIT_YES} ;;
        N) return ${EXIT_NO} ;;
        Yn)
            local exit_val=${EXIT_YES}
            local choice="[${_BGreen}YES${_creset}/no]"
            local default="Yes"
            ;;
        *)
            local exit_val=${EXIT_NO}
            local choice="[${_BGreen}NO${_creset}/yes]"
            local default="No"
            ;;
    esac
    echo
    while true; do
    stdin.clean
        printf "%s ${choice} " "${1}"
        # shellcheck disable=SC2086,SC2229
        read -r -n1 $_t
        if [[ -z ${REPLY} ]]; then
            echo "${default}"; break
        elif [[ ${REPLY} =~ ^[Yy]$ ]]; then
            exit_val=${EXIT_YES}
            echo
            break
        elif [[ ${REPLY} =~ ^[Nn]$ ]]; then
            exit_val=${EXIT_NO}
            echo
            break
        fi
        _t=""
        msg.err "invalid choice"
    done
    stdin.clean
    return $exit_val
}
