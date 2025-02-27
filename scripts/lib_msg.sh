# -*- mode: sh; sh-shell: bash -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

# shellcheck source=./lib_tui.sh
. /dev/null

sh.lib.import tui

if command -v fmt >/dev/null; then
    export FMT="fmt -u"
elif command -v fold >/dev/null; then
    export FMT="fold -s"
else
    export FMT="cat"
fi

# The msg.debug, msg.info, msg.warn and msg.err messages are printed to stder.
# The msg.debug is only printed on verbose level $V >= 3

msg.debug() {
    if [ "${V}" -ge 3 ]; then
    echo -e "${_BYellow}DEBUG:${_creset} $*" >&2
    fi
}
msg.info()  { echo -e "${_BYellow}INFO:${_creset}  $*" >&2; }
msg.warn()  { echo -e "${_BBlue}WARN:${_creset}  $*" >&2; }
msg.err()   { echo -e "${_BRed}ERROR:${_creset} $*" >&2; }

msg.build() {

    # usage:  msg.build ENV "lorem ipsum .."
    #
    # Print a build messages stdout.

    local tag="$1        "
    shift
    echo -e "${_Blue}${tag:0:10}${_creset}$*"
}

msg.title() {

    # usage:  msg.title <header-text> [part|chapter|section]
    #
    # Print reST formated title to stdout.

    case ${2-chapter} in
        part)     printf "\n${_BGreen}${1//?/=}${_creset}\n${_BCyan}%s${_creset}\n${_BGreen}${1//?/=}${_creset}\n" "${1}";;
        chapter)  printf "\n${_BCyan}%s${_creset}\n${_BGreen}${1//?/=}${_creset}\n" "${1}";;
        section)  printf "\n${_BCyan}%s${_creset}\n${_BGreen}${1//?/-}${_creset}\n" "${1}";;
        *)
            msg.err "invalid argument '${2}' in line $(caller)"
            return 42
            ;;
    esac
}

msg.para() {

    # usage:  MSG_INDENT=1 rst_para "lorem ipsum ..."
    #
    # Print reST formated paragraph  to stdout.

    local prefix=''
    if [[ -n $MSG_INDENT ]] && [[ $MSG_INDENT -gt 0 ]]; then
        prefix="$(for _ in $(seq 1 "$MSG_INDENT"); do printf "  "; done)"
        echo -en "\n$*\n" | $FMT | msg.prefix "$prefix"
    else
        echo -en "\n$*\n" | $FMT
    fi
}

msg.prefix () {

    # usage:  <cmd> | msg.prefix [prefix]
    #
    # Add a prefix to each line of stdout.

    local prefix="${_BYellow}-->|${_creset}"

    if [[ -n $1 ]] ; then prefix="$1"; fi

    # shellcheck disable=SC2162
    while IFS= read line; do
         echo -e "${prefix}$line"
    done
    # some piped commands hide the cursor, show cursory when the stream ends
    echo -en "$_show_cursor"
}
