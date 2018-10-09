#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh -*-
# ----------------------------------------------------------------------------
# Purpose:  common shell functions
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# usefull defaults
# ----------------------------------------------------------------------------

if [[ -z "${ORGANIZATION}" ]]; then
    ORGANIZATION="myorg"
fi

if [[ -z "${REPO_ROOT}" ]]; then
    REPO_ROOT="$(dirname ${BASH_SOURCE[0]})"
    while([ -h "${REPO_ROOT}" ]) do REPO_ROOT=`readlink "${REPO_ROOT}"`; done
    REPO_ROOT=$(cd ${REPO_ROOT}/../.. && pwd -P )
fi

if [[ -z "${SCRIPT_FOLDER}" ]]; then
    SCRIPT_FOLDER="${REPO_ROOT}/scripts"
fi

if [[ -z ${TEMPLATES} ]]; then
    TEMPLATES="${REPO_ROOT}/templates"
fi

if [[ -z "$CACHE" ]]; then
    CACHE="${REPO_ROOT}/cache"
fi

if [[ -z ${CONFIG} ]]; then
    CONFIG="${REPO_ROOT}/hostSetup/$(hostname -s)"
fi

if [[ -z "${WWW_FOLDER}" ]]; then
    WWW_FOLDER=/var/www
fi

if [[ -z ${WWW_USER} ]]; then
    WWW_USER=www-data
fi

if [[ -z ${DEB_ARCH} ]]; then
    if [[ $(uname -m) != "x86_64" ]]; then  # 32Bit Version ...
	DEB_ARCH="i386"
    else                                    # 64bit Version ...
	DEB_ARCH="amd64"
    fi
fi

if [[ -e /etc/lsb-release ]]; then
    # Release Informationen in Umgebungsvariablen wie
    # "DISTRIB_ID=ubuntu
    # https://wiki.ubuntu.com/DerivativeDistroHowto#File_.2BAC8-etc.2BAC8-lsb-release
    source /etc/lsb-release
fi

# ----------------------------------------------------------------------------
# toolchain
# ----------------------------------------------------------------------------

if [[ -z ${MERGE_CMD} ]]; then
    # $MERGE_CMD {file_a} {file_b} {merged}
    MERGE_CMD=merge2FilesWithEmacs
fi

if [[ -z ${THREE_WAY_MERGE_CMD} ]]; then
    # $THREE_WAY_MERGE_CMD {mine} {yours} {ancestor} {merged}
    THREE_WAY_MERGE_CMD=merge3FilesWithEmacs
fi

if [[ -z ${DIFF_CMD} ]]; then
    DIFF_CMD=diff
    if [[ $(which colordiff) ]]; then
        DIFF_CMD=colordiff
    fi
fi

export LESS="$LESS -r"

# ----------------------------------------------------------------------------
checkEnviroment() {
# ----------------------------------------------------------------------------

    # Überprüft ob das Environment aussreichend ist um alle Funktionen in dieser
    # Datei nutzen zu können.

    if [[ -z ${CONFIG} ]]; then
        err_msg "environment \${CONFIG} is not defined"
        exit
    fi
    if [[ -z ${TEMPLATES} ]]; then
        err_msg "environment \${TEMPLATES} is not defined"
        exit
    fi

    LDAP_AUTH_BaseDN="dc=`echo $LDAP_SERVER | sed 's/^\.//; s/\.$//; s/\./,dc=/g'`"
    LDAP_AUTH_DC="`echo $LDAP_SERVER | sed 's/^\.//; s/\..*$//'`"

}

# ----------------------------------------------------------------------------
timestamp() {
# ----------------------------------------------------------------------------
    date +"%Y%m%d_%H%M%S"
}

# ----------------------------------------------------------------------------
cleanStdIn() {
# ----------------------------------------------------------------------------
    if [[ $(uname -s) != 'Darwin' ]]; then
        while $(read -n1 -t 0.1); do : ; done
    fi
}

# ----------------------------------------------------------------------------
getIPfromHostname(){
# ----------------------------------------------------------------------------
    ping -q -c 1 -t 1 "$1" | grep PING | sed -e "s/).*//" | sed -e "s/.*(//"
}

# ----------------------------------------------------------------------------
rstHeading() {
# ----------------------------------------------------------------------------

    # usage: rstHeading <header-text> [part|chapter|section]

    case ${2-chapter} in
        part)     printf "\n${BGreen}${1//?/=}\n$1\n${1//?/=}${_color_Off}\n";;
        chapter)  printf "\n${BGreen}${1}\n${1//?/=}${_color_Off}\n";;
        section)  printf "\n${BGreen}${1}\n${1//?/-}${_color_Off}\n";;
        part-nc)     printf "\n${1//?/=}\n$1\n${1//?/=}\n";;
        chapter-nc)  printf "\n${1}\n${1//?/=}\n";;
        section-nc)  printf "\n${1}\n${1//?/-}\n";;
        *)
            err_msg "invalid argument '${2}' in line $(caller)"
            return 42
            ;;
    esac
}

# ----------------------------------------------------------------------------
rstBlock() {
# ----------------------------------------------------------------------------

    echo -en "\n$*\n" | fmt
}

# ----------------------------------------------------------------------------
rstBlock_stdin() {
# ----------------------------------------------------------------------------

    echo ""
    case "${1}" in
        raw)
	    (while read line; do
		echo -e "$line"
		done)
	    ;;
        *)
	    (while read line; do
		echo -e "$line"
		done) | fmt
            ;;
    esac
}

# ----------------------------------------------------------------------------
rstPkgList() {
# ----------------------------------------------------------------------------

    echo -en "\npackage::\n\n  $*\n" | fmt
}

# ----------------------------------------------------------------------------
waitKEY(){
# ----------------------------------------------------------------------------

    # usage: waitKEY [<timeout in sec>]

    local _t=$1
    [[ ! -z $FORCE_TIMEOUT ]] && _t=$FORCE_TIMEOUT
    [[ ! -z $_t ]] && _t="-t $_t"
    shift
    cleanStdIn
    if [[ ! $TERM == "dumb" ]] ; then
        tput sc
        printf "${Green}** press any [${Orange}KEY${Green}] to continue **${_color_Off}"
        read -n1 $_t
        [[ $REPLY == p ]] && read -s -n1
        tput rc
        printf "\e[K"
    else
        read -n1 $_t -p "** press any [KEY] to continue **"
        printf "\n"
    fi
    cleanStdIn
}

# ----------------------------------------------------------------------------
# colorize
# ----------------------------------------------------------------------------

# http://linuxcommand.org/lc3_resources.php
# http://misc.flogisoft.com/bash/tip_colors_and_formatting
# http://ethanschoonover.com/solarized
# siehe: man terminfo, man tput

_colors=0
if tput setaf 1 &> /dev/null; then

    BOLD=$(tput bold)
    _color_Off=$(tput sgr0)

    Black=$(tput setaf 0)
    White=$(tput setaf 7)
    BBlack=$(tput setaf 0)$(tput bold)
    BWhite=$(tput setaf 7)$(tput bold)

    if [[ $(tput colors) -ge 256 ]] 2>/dev/null; then
        _colors=256

        Red=$(tput setaf 160)
        Green=$(tput setaf 64)
        Yellow=$(tput setaf 136)
        Blue=$(tput setaf 33)
        Cyan=$(tput setaf 37)
        Violet=$(tput setaf 61)

        BRed=$(tput setaf 160)$(tput bold)
        BGreen=$(tput setaf 64)$(tput bold)
        BYellow=$(tput setaf 136)$(tput bold)
        BBlue=$(tput setaf 33)$(tput bold)
        BCyan=$(tput setaf 37)$(tput bold)
        BViolet=$(tput setaf 61)$(tput bold)

        Orange=$(tput setaf 166)
        Magenta=$(tput setaf 125)

        BASE03=$(tput setaf 234)
        BASE02=$(tput setaf 235)
        BASE01=$(tput setaf 240)
        BASE00=$(tput setaf 241)
        BASE0=$(tput setaf 244)
        BASE1=$(tput setaf 245)
        BASE2=$(tput setaf 254)
        BASE3=$(tput setaf 230)

    else
        _colors=16

        Red=$(tput setaf 1)
        Green=$(tput setaf 2)
        Yellow=$(tput setaf 3)
        Blue=$(tput setaf 4)
        Violet=$(tput setaf 13)
        Cyan=$(tput setaf 6)

        BRed=$(tput setaf 1)$(tput bold)
        BGreen=$(tput setaf 2)$(tput bold)
        BYellow=$(tput setaf 3)$(tput bold)
        BBlue=$(tput setaf 4)$(tput bold)
        BViolet=$(tput setaf 13)$(tput bold)
        BCyan=$(tput setaf 6)$(tput bold)

        Orange=$(tput setaf 9)
        Magenta=$(tput setaf 5)

        BASE03=$(tput setaf 8)
        BASE02=$(tput setaf 0)
        BASE01=$(tput setaf 10)
        BASE00=$(tput setaf 11)
        BASE0=$(tput setaf 12)
        BASE1=$(tput setaf 14)
        BASE2=$(tput setaf 7)
        BASE3=$(tput setaf 15)
    fi
else
    _colors=8
    _color_Off='\e[0m'  # Text Reset

    Black='\e[0;30m'
    White='\e[1;37m'
    Red='\e[0;31m'
    Green='\e[0;32m'
    Yellow='\e[0;33m'
    Blue='\e[0;34m'
    Violet='\e[0;35m'
    Cyan='\e[0;36m'

    # Bold
    BBlack='\e[1;30m'
    BWhite='\e[1;37m'
    BRed='\e[1;31m'
    BGreen='\e[1;32m'
    BYellow='\e[1;33m'
    BBlue='\e[1;34m'
    BPurple='\e[1;35m'
    BCyan='\e[1;36m'

fi

# ----------------------------------------------------------------------------
err_msg() {
# ----------------------------------------------------------------------------
    echo -e "${BRed}ERROR:${_color_Off} $*" >&2
}
# ----------------------------------------------------------------------------
info_msg() {
# ----------------------------------------------------------------------------
    echo -e "${BYellow}INFO:${_color_Off} $*"
}

# ----------------------------------------------------------------------------
ask(){
# ----------------------------------------------------------------------------

    # usage: ask <env-name> <prompt-text> <default>

    local REPLY
    local env_name=$1
    local prompt_text="$2"
    local default="$3"

    local choice=""
    if [[ ! -z $3 ]] ; then choice="[${Orange}${default}${_color_Off}]"; fi

    printf "\n"
    while true; do
        cleanStdIn
        [[ ! $TERM == "dumb" ]] && tput sc
        printf "${_color_Off}${prompt_text} ${choice} "
        read $_t
        if [[ -z $REPLY ]]; then
            if [[ ! -z $default ]]; then
                #printf "$default\n"
                REPLY="$default"
                break
            else
                _t="" # Wenn die erste Eingabe ungültig ist wird der Timer abgeschaltet
                if [[ $TERM == "dumb" ]] ; then
                    err_msg "invalid choice"
                else
                    printf "  ${BRed}ERROR:${_color_Off} invalid choice"
                    sleep 1
                    tput rc
                    printf "\e[K"
                fi
            fi
        else
            break
        fi
    done
    cleanStdIn
    eval "$env_name='${REPLY}'"
}

# ----------------------------------------------------------------------------
askYesNo(){
# ----------------------------------------------------------------------------

    # usage: askYesNO <prompt-text> [Yn|Ny] <timeout in sec>

    EXIT_YES=0 # exit status 0 --> successful
    EXIT_NO=1  # exit status 1 --> error code
    local _t=$3
    [[ ! -z $FORCE_TIMEOUT ]] && _t=$FORCE_TIMEOUT
    [[ ! -z $_t ]] && _t="-t $_t"

    # ESC-Sequenzen: http://ascii-table.com/ansi-escape-sequences.php

    case "${2}" in
        Yn)
            local exitValue=${EXIT_YES}
            local choice="[${Orange}Yes${_color_Off}/no]"
            local default="Yes"
            ;;
        Ny)
            local exitValue=${EXIT_NO}
            local choice="[${Orange}No${_color_Off}/yes]"
            local default="No"
            ;;
        *)  err_msg "invalid argument '${2}' in line $(caller)"
            return 42
            ;;
    esac

    printf "\n"
    while true; do
        cleanStdIn
        [[ ! $TERM == "dumb" ]] && tput sc
        printf "${_color_Off}$1 ${choice} "
        read -n1 $_t
        if [[ -z $REPLY ]]; then
            printf "$default\n"
            break
        elif [[ $REPLY =~ ^[Yy]$ ]]; then
            exitValue=${EXIT_YES}
            printf "\n"
            break
        elif [[ $REPLY =~ ^[Nn]$ ]]; then
            exitValue=${EXIT_NO}
            printf "\n"
            break
        fi
        _t="" # Wenn die erste Eingabe ungültig ist wird der Timer abgeschaltet
        if [[ $TERM == "dumb" ]] ; then
            err_msg "invalid choice"
        else
            printf "  ${BRed}ERROR:${_color_Off} invalid choice"
            sleep 1
            tput rc
            printf "\e[K"
        fi
    done
    cleanStdIn
    return $exitValue
}

# ----------------------------------------------------------------------------
askNy(){
# ----------------------------------------------------------------------------

    # usage: askNy <prompt-text> <timeout in sec>
    askYesNo "${1}" Ny "${2}"
}

# ----------------------------------------------------------------------------
askYn(){
# ----------------------------------------------------------------------------

    # usage: askYn <prompt-text> <timeout in sec>
    askYesNo "${1}" Yn "${2}"
}

# ----------------------------------------------------------------------------
chooseOneMenu() {
# ----------------------------------------------------------------------------

    # Print a menu from arguments ($2-$n) and promt selection with ($1)
    #
    # usage:
    #   chooseOneMenu <name>  "your selection?" "Coffee" "Coffee with milk"

    local default=${DEFAULT_SELECT-1}
    local REPLY
    local env_name=$1 && shift
    local choice=$1;
    local max="${#@}"
    local _t
    [[ ! -z $FORCE_TIMEOUT ]] && _t=$FORCE_TIMEOUT
    [[ ! -z $_t ]] && _t="-t $_t"

    list=("$@")
    echo -e "${BGreen}Menu::${_color_Off}"
    for ((i=1; i<= $(($max -1)); i++)); do
        if [[ $i == $default ]]; then
            echo -e "  ${Orange}$i.)${_color_Off} ${list[$i]}"
        else
            echo -e "  ${BGreen}$i.)${_color_Off} ${list[$i]}"
        fi
    done
    while true; do
        cleanStdIn
        [[ ! $TERM == "dumb" ]] && tput sc
        printf "$1 [${Orange}$default${_color_Off}] "

        if (( 10 > $max )); then
            read -n1 $_t
        else
            read $_t
        fi
        # selection fits
        [[ $REPLY =~ ^-?[0-9]+$ ]] && (( $REPLY > 0 )) && (( $REPLY < $max )) && break

        # take default
        [[ -z $REPLY ]] && REPLY=$default && break

        _t="" # Wenn die erste Eingabe ungültig ist wird der Timer abgeschaltet

        if [[ $TERM == "dumb" ]] ; then
            err_msg "invalid choice"
        else
            printf "  ${BRed}ERROR:${_color_Off} invalid choice"
            sleep 1
            tput rc
            printf "\e[K"
        fi
    done
    echo
    cleanStdIn
    eval $env_name='${list[${REPLY}]}'
}

# ----------------------------------------------------------------------------
askPassphrase(){
# ----------------------------------------------------------------------------

    # Fragt den Anwender nach einer Passphrase und legt sie in dem globalen
    # Namen ``passphrase`` ab.
    local prompt="$1"
    if [[ -z ${prompt} ]]; then
        prompt="Passphrase"
    fi

    passphrase=""
    local passphrase_check="--"
    while [[ ${passphrase} != ${passphrase_check} ]] ; do
        read -s -p "$prompt: " passphrase
        echo
        read -s -p "$prompt (again): " passphrase_check
        echo
        if [[  ${passphrase} != ${passphrase_check} ]] ; then
            err_msg "typo, please repeat"
            passphrase=""
            passphrase_check="--"
        fi
    done
}

# ----------------------------------------------------------------------------
ask_rm(){
# ----------------------------------------------------------------------------

    # Ask to remove files by glob pattern from (base) folder.  Without pattern,
    # remove the entire folder.
    #
    # usage:
    #
    #    ask_rm [Yn|Ny] <base-folder> [<files to remove>, ...]
    #
    # e.g.: ask_rm /var/lib/samba '*.tdb' '*.dat' 'private'
    #
    local ask_default=$1
    shift
    local folder=$1
    shift

    if [[ ! -d "$folder" ]]; then
        info_msg "Ordner $folder existiert nicht (Löschen nicht erforderlich)"
        return 42
    fi

    if [[ $# -eq 0 ]]; then
        if askYesNo "Soll der Ordner '${folder}' gelöscht werden?" ${ask_default}; then
            rm -rf "$folder"
        fi
        return $?
    fi
    TEE_stderr <<EOF | bash 2>&1 | prefix_stdout
cd ${folder}; ls -la "$@"; exit $?
EOF
    if askYesNo "Sollen die Dateien (${folder}) gelöscht werden?" ${ask_default}; then
        for pattern in "$@"; do
            rm -rf ${folder}/${pattern}
        done
    fi
}


# ----------------------------------------------------------------------------
TEE_stderr () {
# ----------------------------------------------------------------------------

    # Es wird Zeile für Zeile von stdin gelesen und auf stdout ausgegeben. Auf
    # stderr erfolgt die gleiche Ausgabe (ggf. coloriert). Vor der Ausgabe der
    # Zeile wird n-Sekunden gewartet (erstes Argument). Diese Funktion eignet
    # sich um eine Reihe von Kommandos (Zeilen) sequentiell an einen Interpreter
    # oder ähnliches weiter zu geben.

    # Beispiel::
    #
    #     TEE_stderr 3 <<EOF | python -i 2>&1 | prefix_stdout "OUT: "
    #     a=5+2
    #     b=a+3
    #     print "hello"
    #     print b
    #     EOF

    local _t="0";
    if [[ ! -z $1 ]] ; then _t="$1"; fi

    (while read line; do
        sleep $_t
        echo -e "${BRed}$line${_color_Off}" >&2
        echo "$line"
    done)
}

# ----------------------------------------------------------------------------
prefix_stdout () {
# ----------------------------------------------------------------------------

    # Fügt jeder Zeile aus dem Stream aus stdin ein Prefix hinzu und gibt diese
    # Zeile auf stdout wieder aus. Kann man verwenden um Ausgaben eines Tools
    # optisch (farblich) besonders hervorzuheben.

    # usage:
    #
    #     <cmd> | prefix_stdout [prefix [color]]
    #
    #     ls -la | prefix_stdout "-->|" "${Yellow}"

    local prefix="-->| "
    local color_on="${Yellow}"
    local color_off="${_color_Off}"

    if [[ ! -z $1 ]] ; then prefix="$1"; fi
    if [[ ! -z $2 ]] ; then color_on="$2"; fi
    if [[ -z $color_on ]] ; then color_off=""; fi

    (while IFS= read line; do
        echo -e "${prefix}${color_on}$line${color_off}"
    done)

}

# ----------------------------------------------------------------------------
sudoOrExit() {
# ----------------------------------------------------------------------------
    if [ ! $(id -u) -eq 0 ];  then
        echo "this command requires root (sudo) privilege!"
        exit 42
    fi
}

# ----------------------------------------------------------------------------
exitOnSudo() {
# ----------------------------------------------------------------------------
    if [ $(id -u) -eq 0 ];  then
        echo "this command should not executed with root (sudo) privilege!"
        exit 42
    fi
}

# ----------------------------------------------------------------------------
askReboot() {
# ----------------------------------------------------------------------------

    # usage: askReboot [Ny|Yn] [<timeout in sec>]

    rstHeading "== Es wird ein Reboot des Hosts $HOSTNAME empfohlen ==" part
    if askYesNo "Soll **$HOSTNAME** neu gebootet werden?" ${1:-Ny} $2; then
        sudo reboot
    fi
}

# ----------------------------------------------------------------------------
cacheDownload() {
# ----------------------------------------------------------------------------

    # usage: cacheDownload <url> <local-filename> [askYn|askNy]

    local exitValue=0

    if [[ ! -z ${SUDO_USER} ]]; then
        sudo -u ${SUDO_USER} mkdir -p ${CACHE}
    else
        mkdir -p ${CACHE}
    fi

    if [[ -f "${CACHE}/$2" ]] ; then
        info_msg "${Green}already cached:${_color_Off} $1"
        info_msg "  -->${Green} ${CACHE}/$2 ${_color_Off}"

        case "$3" in
            askYn|askNy)
                if ( ! $3 "should $2 from cache be used?"); then
                    rm "${CACHE}/$2"
                fi
                ;;
        esac
    fi

    if [[ ! -f "${CACHE}/$2" ]]; then
        info_msg "${Green}caching:${_color_Off} $1"
        info_msg "  -->${Green} ${CACHE}/$2 ${_color_Off}"
        if [[ ! -z ${SUDO_USER} ]]; then
            sudo -u ${SUDO_USER} wget --progress=bar -O "${CACHE}/$2" $1 ; exitValue=$?
        else
            wget --progress=bar -O "${CACHE}/$2" $1 ; exitValue=$?
        fi
        if (( $exitValue )) ; then
            err_msg "failed to download: $1"
        fi
    fi
}

# ----------------------------------------------------------------------------
cloneGitRepository() {
# ----------------------------------------------------------------------------

    # cloneGitRepository https://github.com/radarhere/Sane.git python-sane

    local target_folder="${CACHE}/$2"
    if [[  "${2:0:1}" = "/" ]]; then
        target_folder="$2"
    fi

    if [[ ! -z ${SUDO_USER} ]]; then
        sudo -u ${SUDO_USER} mkdir -p ${CACHE}
    else
        mkdir -p ${CACHE}
    fi

    if [[ -d "${target_folder}" ]] ; then
	info_msg "${Green}already cloned:${_color_Off} $1"
        info_msg "  -->${Green} ${target_folder} ${_color_Off}"
	pushd "${target_folder}" > /dev/null
        if [[ ! -z ${SUDO_USER} ]]; then
            sudo -u ${SUDO_USER} git pull --all
        else
            git pull --all
        fi
	popd > /dev/null
    else
	info_msg "${Green}clone:${_color_Off} $1"
        info_msg "  -->${Green} ${target_folder} ${_color_Off}"
	pushd "$(dirname ${target_folder})" > /dev/null
        if [[ ! -z ${SUDO_USER} ]]; then
            sudo -u ${SUDO_USER} git clone "$1" "$2"
        else
            git clone "$1" "$2"
        fi
	popd > /dev/null
    fi
}

# ----------------------------------------------------------------------------
merge3FilesWithEmacs(){
# ----------------------------------------------------------------------------

    # usage:
    #
    #    merge3FilesWithEmacs file-A file-B file-ancestor merge-buffer-file

    emacs -nw --no-desktop --eval "\
(progn \
  (setq ediff-quit-hook 'kill-emacs)   \
  (ediff-merge-files-with-ancestor \"$1\" \"$2\" \"$3\" nil \"$4\"))"
}

# ----------------------------------------------------------------------------
merge2FilesWithEmacs(){
# ----------------------------------------------------------------------------

    # usage:
    #
    #    merge2FilesWithEmacs file-A file-B merge-buffer-file

    emacs -nw --no-desktop --eval "\
(progn \
  (setq ediff-quit-hook 'kill-emacs)   \
  (ediff-merge-files \"$1\" \"$2\" nil \"$3\"))"
}

# ----------------------------------------------------------------------------
merge3FilesWithMeld(){
# ----------------------------------------------------------------------------

    # usage:
    #
    #    merge3FilesWithMeld {mine} {yours} {ancestor} {merged}

    # meld "$LOCAL" "$BASE" "$REMOTE" --output "$MERGED"
    meld "$1" "$3" "$2" --output "$4"

}

# ----------------------------------------------------------------------------
merge2FilesWithMeld(){
# ----------------------------------------------------------------------------

    # usage:
    #
    #    merge2FilesWithMeld {my-file} {your-file} {merged-file}

    meld "$1" "$2" --output "$3"
}


# ----------------------------------------------------------------------------
cmp3Files() {
# ----------------------------------------------------------------------------

    # Vergleichen von drei Dateien
    #
    # cmp3Files <name> {my-file} {your-file} {common-ancestor-file}
    #
    # In der Array-Variablen <name> werden die ungleichen Dateien gesetzt.
    #
    # <name> {my-file} {your-file} {common-ancestor-file} :: Sind alle drei
    #     Datein unterschiedlich werden sie in der gleichen Reihenfolge gesetzt,
    #     wie sie als Argumente übergeben wurden.
    #
    # <name> ({my-file} {your-file or common-ancestor-file}) :: Sind nur zwei
    #     Dateien unterschiedlich, steht am ersten Platz des Arrays wieder die
    #     Datei, die schon der Funktion als erstes Argument übergeben wurde.
    #
    # <name> () :: Sind alle drei Dateien gleich, wird ein leeres Array gesetzt
    #
    local env_name=$1
    local file_a=$(realpath "$2")
    local file_b=$(realpath "$3")
    local file_c=$(realpath "$4")
    local f
    local retVal=("${file_a}")

    for f in "${file_a}" "${file_b}" "${file_c}" ; do
        if [[ ! -f "${f}" ]] ; then
            err_msg "file ${f} does not exists"
	    waitKEY
            return 1
        fi
    done

    if ! cmp --silent "${file_a}" "${file_b}"; then
        retVal=("${retVal[@]}" "${file_b}")
    fi
    if ! cmp --silent "${file_a}" "${file_c}"; then
        if ! cmp --silent "${file_b}" "${file_c}"; then
            retVal=("${retVal[@]}" "${file_c}")
        fi
    fi

    if [[ ${#retVal[@]} == 1 ]]; then
        eval $env_name='()'
    else
        eval $env_name='("${retVal[@]}")'
    fi
    return 0
}

# ----------------------------------------------------------------------------
merge2Files() {
# ----------------------------------------------------------------------------

    # Vergleichen / Mergen von zwei Dateien.
    #
    # Es werden zwei Dateien miteinander verglichen. Wenn es Differenzen gibt,
    # kann ein Merge durchgeführt werden. Die beiden zu vergleichenden Dateien
    # werden als Argumente übergeben. Das dritte Argument ist ein Name für die
    # Datei mit dem Merge.
    #
    # Die Funktion kann allgemein genutzt werden, um zwei Dateien zu mergen.
    # Lässt man das dritte Argument, den Dateinamen für den Merge weg, dann
    # schaltet die Funktion in einen Modus um, der auf die Ordnerstruktur der
    # handsOn Skripte optimiert ist. In diesem Modus wird die erste Datei durch
    # den Merge ersetzt. Etwas anschaulicher erklärt:
    #
    #  1. Argument  ${CONFIG}/etc/apache2/apache2.conf    <-- merge backup-file
    #  2. Argument  ${TEMPLATES}/etc/apache2/apache2.conf
    #
    # oder aber
    #
    #  1. Argument  /etc/apache2/apache2.conf          <-- merge im dst file
    #  2. Argument  ${TEMPLATES}/etc/apache2/apache2.conf
    #
    # usage:
    #
    #     merge2Files {my-file}     {your-file}     {merged-file}
    #     merge2Files {sys-file|backup-file} {template-file}
    #
    # exit-codes: ACHTUNG, beim Merge ist der Exit-Code ungleich Null!
    #
    #     0: Keine Merge erfolgt, entweder weil alle gleich oder Benutzer Merge
    #        abgelehnt hat.
    #     1: Es ist ein Fehler aufgetreten
    #     2: Es wurde ein Merge der zwei Dateien durchgeführt
    #    16: Die Datei aus dem erste Argument wurde übernommen
    #    32: Die Datei aus dem zweiten Argument wurde übernommen

    local file_a=$(realpath "$1")
    local file_b=$(realpath "$2")
    local merged=$(realpath ${3-$1.merged})
    local retCode=1  # im default wird der Fehlerfall angenommen

    local mode="normal"
    if [[ -z "$3" ]]; then
        mode="handsOn"
    fi
    #echo ":: mode --> $mode"

    for f in "${file_a}" "${file_b}"; do
        if [[ ! -f "${f}" ]] ; then
            err_msg "file ${f} does not exists"
	    waitKEY
            return $retCode
        fi
    done

    # *all equal*
    # ----------------

    if cmp --silent "${file_a}" "${file_b}"; then
        info_msg "These files are *equal* (no need to merge)"
        info_msg "    ${file_a}"
        info_msg "    ${file_b}"
        retCode=0
        ## Job done: EXIT !!!
        return $retCode
    fi

    # Auswahlliste aufbauen:
    local choices=("take over file ${file_b}")
    if [[ $mode == "normal"  ]]; then
        local choices=("${choices[@]}" "take over file ${file_a}")
    else
        local choices=("${choices[@]}" "keep file ${file_a} untouched")
    fi
    choices=("${choices[@]}" "merge files")

    local c
    chooseOneMenu c "your selection?" "${choices[@]}"

    case "$c" in

        "keep file ${file_a} untouched")
            if [[ $mode == "handsOn" ]]; then
                retCode=0
            fi
            ;;

        "take over file ${file_a}")
            if [[ $mode == "normal" ]]; then
                cp -f "${file_a}" "${merged}"
                retCode=16
            fi
            ;;

        "take over file ${file_b}")
            if [[ $mode == "normal" ]]; then
                info_msg "cp ${file_b} --> ${merged}"
                cp -f "${file_b}" "${merged}"
                retCode=32
            elif [[ $mode == "handsOn" ]]; then
                info_msg "cp ${file_b} --> ${file_a}"
                cp -f "${file_b}" "${file_a}"
                retCode=32
            fi
            ;;

        "merge files")

            rm -f "$merged"
            $MERGE_CMD "${file_a}" "${file_b}" "$merged"

            if [[ -f "$merged" ]]; then
                retCode=2
                if [[ $mode == "handsOn" ]]; then
                    info_msg "save merged file --> ${file_a}"
                    cp -f "${merged}" "${file_a}"
                    rm  "$merged"
                fi
            else
                # Wenn keine Merge-Datei erzeugt wurde, wird dies als Fehler bewertet
                err_msg "missing merged file"
                retCode=1
            fi
            ;;
        *)
            # FIXME: Ich hab teilweise Probleme mit dem *select*, wenn das mit
            # TMOUT läuft.
            err_msg "FIXME: Es trat ein *Ausnahmefehler* bei der Auswahl auf"
            retCode=1
            ;;
    esac
    ## Job done: EXIT !!!
    [[ $retCode == 1 ]] && err_msg "merge failed with errors!"
    return $retCode
}

# ----------------------------------------------------------------------------
merge3Files() {
# ----------------------------------------------------------------------------

    # Vergleichen / Mergen von drei Dateien.
    #
    # Es werden drei Dateien miteinander verglichen, wenn es Differenzen gibt,
    # kann ein Merge durchgeführt werden. Die drei zu vergleichenden Dateien
    # werden als Argumente übergeben. Das vierte Argument ist ein Name für die
    # Datei mit dem Merge.
    #
    # Die Funktion kann allgemein genutzt werden, um drei Dateien zu mergen.
    # Lässt man das vierte Argument, den Dateinamen für den Merge weg, dann
    # schaltet die Funktion in einen Modus um, der auf die Ordnerstruktur der
    # handsOn Skripte optimiert ist. In diesem Modus werden die erste und dritte
    # Datei durch den Merge ersetzt. Etwas anschaulicher erklärt:
    #
    #  1. Argument  /etc/apache2/apache2.conf             <-- merge
    #  2. Argument  ${TEMPLATES}/etc/apache2/apache2.conf
    #  3. Argument  ${CONFIG}/etc/apache2/apache2.conf    <-- merge
    #
    #  Wird ein vierter Dateiname für den Merge angegeben, so darf diese
    #  Merge-Datei noch nicht existieren, bzw. sie wird vor dem Merge gelöscht.
    #
    # usage:
    #
    #     merge3Files {my-file}   {your-file}  {common-ancestor-file} {merged-file}
    #     merge3Files {sys-file}  {templ-file} {backup-file}
    #
    # exit-codes: ACHTUNG, beim Merge ist der Exit-Code ungleich Null!
    #
    #     0: Keine Merge erfolgt, entweder weil alle gleich oder Benutzer Merge
    #        abgelehnt hat.
    #     1: Es ist ein Fehler aufgetreten
    #     2: Es wurde ein Merge von zwei Dateien durchgeführt
    #     4: Es wurde ein drei-Wege-Merge durchgeführt.
    #    16: Die Datei aus dem ersten Argument wurde übernommen
    #    32: Die Datei aus dem zweiten Argument wurde übernommen
    #    64: die Datei aus dem dritten Argument wurde übernommen

    local file_a=$(realpath "$1")
    local file_b=$(realpath "$2")
    local file_c=$(realpath "$3")
    local merged=$(realpath ${4-$1.merged})
    local files2merge=
    local retCode=1  # im default wird der Fehlerfall angenommen

    local mode="normal"
    if [[ -z "$4" ]]; then
        mode="handsOn"
    fi

    # compare three files and EXIT on error
    cmp3Files files2merge "${file_a}" "${file_b}" "${file_c}" || return $retCode

    # *all equal*
    # ----------------

    if [[ ${#files2merge[@]} < 2 ]]; then
        info_msg "These files are *equal* (no need to merge)"
        info_msg "    ${file_a}"
        info_msg "    ${file_b}"
        info_msg "    ${file_c}"
        ## Job done: EXIT !!!
        retCode=0
        return $retCode
    elif cmp --silent "${file_a}" "${file_c}"; then
        info_msg "These files are *equal*"
        info_msg "    ${file_a}"
        info_msg "    ${file_c}"
    elif cmp --silent "${file_b}" "${file_c}"; then
        info_msg "These files are *equal*"
        info_msg "    ${file_b}"
        info_msg "    ${file_c}"
    fi

    local choices=()
    if [[ $mode == "normal" ]]; then
        #
        # merge3Files {my-file} {your-file} {common-ancestor-file} {merged-file}
        #
        choices=("${choices[@]}" "keep file ${files2merge[0]} untouched")
        choices=("${choices[@]}" "take over file ${files2merge[1]}")
        [[ ${#files2merge[@]} > 2 ]] && choices=("${choices[@]}" "take over file ${files2merge[2]}" )

    elif [[ $mode == "handsOn" ]]; then
        #
        # merge3Files {sys-file}  {templ-file} {backup-file}
        #
        # Die Reihenfolge im Auswahlmenü versucht das *naheliegenste* oben in
        # der Liste anzuordnen, der manuelle Merge steht immer an letzter Stelle
        # im Menü. Bei der Festlegung der Reihenfolge gehe ich davon aus, dass
        # es eigentlich nur zwei mögliche Gründe für die Veränderung von
        # {sys-file} und {templ-file} geben kann, ohne das diese im
        # {backup-file} gelandet währen.
        #
        # 0.) manuelle Änderungen an {sys-file} wurden auch immer im {backup-file}
        #     gesichert.
        # 1.) Systemupdates ändern u.U. {sys-file}
        #     * {backup-file} ist *getestet*, das Update an der eigenen
        #       Konfiguration aber nicht
        #     * {backup-file} wird über {sys-file} priorisiert
        # 2.) Es gab eine Verbesserung in dem {templ-file}
        #     * Die Verbesserung in {templ-file} ist *ungetestet*, das
        #       {sys-file} ist produktiv
        #     * {sys-file} wird über {templ-file} priorisiert

        [[ ${#files2merge[@]} > 2 ]] && choices=("${choices[@]}" "take over file ${files2merge[2]}" )
        choices=("${choices[@]}" "take over file ${files2merge[1]}" )
        choices=("${choices[@]}" "keep file ${files2merge[0]} untouched")
    fi
    choices=("${choices[@]}" "merge files")

    local c
    chooseOneMenu c "your selection?" "${choices[@]}"

    case "$c" in

        "keep file ${files2merge[0]} untouched")
            if [[ $mode == "handsOn" ]]; then
                retCode=0
            fi
            ;;

        "take over file ${files2merge[1]}")
            if [[ $mode == "normal" ]]; then
                info_msg "cp ${files2merge[1]} --> ${merged}"
                cp -f "${files2merge[1]}" "${merged}"
                retCode=32
            elif [[ $mode == "handsOn" ]]; then
                info_msg "cp ${files2merge[1]} --> ${file_a}"
                cp -f "${files2merge[1]}" "${file_a}"
                # falls ein Backup existiert, wird das jetzt auch gleich
                # mit dem Merge geladen
                if [[ -f "${file_c}" ]]; then
                    if ! cmp --silent "${file_a}" "${file_c}"; then
                        info_msg "cp ${file_a} --> ${file_c}"
                        cp -f "${file_a}" "${file_c}"
                    fi
                fi
                retCode=32
            fi
            ;;

        "take over file ${files2merge[2]}")
            if [[ $mode == "normal" ]]; then
                info_msg "cp ${files2merge[2]} --> ${merged}"
                cp -f "${files2merge[2]}" "${merged}"
                retCode=64
            elif [[ $mode == "handsOn" ]]; then
                info_msg "cp ${files2merge[2]} --> ${file_a}"
                cp -f "${files2merge[2]}" "${file_a}"
                retCode=64
            fi
            ;;

        "merge files")
            rm -f "$merged"
            if [[ ${#files2merge[@]} == 2 ]]; then
                $MERGE_CMD "${files2merge[@]}" "$merged"
                retCode=2
            else
                $THREE_WAY_MERGE_CMD "$file_b" "$file_c" "$file_a" "$merged"
                retCode=4
            fi
            if [[ -f "$merged" ]]; then
                if [[ $mode == "handsOn" ]]; then
                    info_msg "save merged file --> ${file_a}"
                    cp -f "${merged}" "$file_a"
                    rm -f "${merged}"
                    # falls ein Backup existiert, wird das jetzt auch gleich
                    # mit dem Merge geladen
                    if ! cmp --silent "${file_a}" "${file_c}"; then
                        info_msg "cp ${file_a} --> ${file_c}"
                        cp -f "${file_a}" "${file_c}"
                    fi
                fi
            else
                # Wenn keine Merge-Datei erzeugt wurde, wird dies als Fehler bewertet
                err_msg "missing merged file"
                retCode=1
            fi
            ;;
        *)
            # FIXME: Ich hab teilweise Probleme mit dem *select*, wenn das mit
            # TMOUT läuft.
            err_msg "FIXME: Es trat ein *Ausnahmefehler* bei der Auswahl auf"
            retCode=1
            ;;
    esac
    ## Job done: EXIT !!!
    [[ $retCode == 1 ]] && err_msg "merge failed with errors!"
    return $retCode
}


# ----------------------------------------------------------------------------
aptInstallPackages(){
# ----------------------------------------------------------------------------

    rstHeading "${TITLE:-installation of deb-packages}" section
    rstPkgList "$@"
    if askYn "should packages be installed?" 30; then
        apt-get install -y "$@"
    fi
    waitKEY 30
}

# ----------------------------------------------------------------------------
aptPurgePackages(){
# ----------------------------------------------------------------------------

    rstHeading "${TITLE:-remove deb-packages}" section
    rstPkgList "$@"
    if askYn "should packages be de-installed (purged)?" 30; then
        apt-get purge --autoremove --ignore-missing -y "$@"
    fi
    waitKEY 30
}

# ----------------------------------------------------------------------------
aptPackageInstalled() {
# ----------------------------------------------------------------------------
    # if ! aptPackageInstalled virtualenv ; then
    #     echo "Please install virtualenv!"
    # fi
    dpkg -l "$1" &> /dev/null
    return
}

# ----------------------------------------------------------------------------
aptRepositoryExist() {
# ----------------------------------------------------------------------------

    # Prüft, ob die APT-Datenquelle bereits eingerichtet ist.

    # usage:
    #
    #     aptRepositoryExist '<deb[-src] URI Suite>' [apt-src-name]
    #
    #     aptRepositoryExist 'deb http://download.virtualbox.org/virtualbox/debian wily' oracle-vbox

    local APT_SRC_ENTRY="${1}"
    local APT_SOURCE_NAME="${2}"
    local regexp="^\s*${APT_SRC_ENTRY}"

    if [[ -f "/etc/apt/sources.list.d/${APT_SOURCE_NAME}.list" ]] ; then
        info_msg "/etc/apt/sources.list.d/${APT_SOURCE_NAME}.list exists."
    fi
    grep --color=auto -n "$regexp" /etc/apt/sources.list /etc/apt/sources.list.d/*.list 2> /dev/null
    local retCode=$?
    return $retCode
}

# ----------------------------------------------------------------------------
aptAddRepositoryURL(){
# ----------------------------------------------------------------------------

    # Dem add-apt-repository fehlt (immernoch) die Option --sources-list-file,
    # mit dem man den Eintrag in eine separate Datei in sources.list.d eintragen
    # könnte (so wie bei ppa's). Deswegen mache ich das hier manuell. Typischer
    # Weise verwendet man die drei aptXYZ-Funktionen zum anlegen löschen eines
    # Repository gemeinsam::
    #
    #   APT_SOURCE_NAME="nodesource"
    #   APT_SOURCE_URL="https://deb.nodesource.com/node_4.x"
    #   APT_SOURCE_KEY_URL="https://deb.nodesource.com/gpgkey/nodesource.gpg.key"
    #
    # Hinzufügen des APT-Repository *nodesource* (suite=main)::
    #
    #   aptAddRepositoryURL "$APT_SOURCE_URL" "$APT_SOURCE_NAME" main
    #
    # Hinzufügen der APT-Datenquelle (suite=nodesource, compnent=src)::
    #
    #   aptAddRepositoryURL "$APT_SOURCE_URL" "$APT_SOURCE_NAME" main src
    #
    # Hinzufügen des Public-Keys des APT-Repository *nodesource*::
    #
    #   aptAddPkeyFromURL "$APT_SOURCE_KEY_URL" "$APT_SOURCE_NAME"
    #
    # Löschen des APT-Repository *nodesource* (suites & components) und des
    # public-keys::
    #
    #   aptRemoveRepository "$APT_SOURCE_NAME"
    #
    # usage:
    #
    #     addAptRepositoryURL <apt-reposetory-url> [apt-reposetory-name [comp [src]]]

    local URL="${1}"
    local FNAME="$(stripHostnameFromUrl ${1})".list
    local APT_SOURCE_NAME="${FNAME}"

    if [[ ! -z $2 ]] ; then
        FNAME="${2}".list
        APT_SOURCE_NAME="${2}"
    fi

    FNAME="/etc/apt/sources.list.d/${FNAME}"

    local DEB="deb ${1} $(lsb_release -sc)"
    if [[ ! -z "$4" ]] ; then
        DEB="deb-$4 ${1} $(lsb_release -sc)"
    fi
    if aptRepositoryExist "${DEB}" "${APT_SOURCE_NAME}"; then
        rstBlock "APT-Source: '${DEB}' allready exist"
        if ! askNy "should it be added once more?"; then
            return
        fi
    fi
    if [[ ! -z "$3" ]] ; then
        DEB="$DEB $3"
    else
        DEB="$DEB contrib"
    fi

    echo -e "add: ${Yellow}${DEB}${_color_Off}"
    echo -e "to:  ${Yellow}${FNAME}${_color_Off}"
    echo "" >> "${FNAME}"
    echo "# added $(date)" >> "${FNAME}"
    echo "${DEB}" >> "${FNAME}"
}

# ----------------------------------------------------------------------------
aptAddPkeyFromURL(){
# ----------------------------------------------------------------------------

    # usage: aptAddPkeyFromURL KEY-URL [REPOSETORY-NAME]

    # aptAddPkeyFromURL
    #      https://www.virtualbox.org/download/oracle_vbox.asc

    local URL="${1}"
    local FNAME="$(stripFilenameFromUrl ${1})".gpg

    if [[ ! -z $2 ]] ; then
        FNAME="${2}".gpg
    fi

    FNAME="/etc/apt/trusted.gpg.d/${FNAME}"
    echo -e "add key from: ${Yellow}${URL}${_color_Off}"
    echo -e "to:  ${Yellow}${FNAME}${_color_Off}"

    TEE_stderr <<EOF | bash | prefix_stdout
    wget -q "$URL" -O- | sudo apt-key --keyring "$FNAME" add -
EOF
}

# ----------------------------------------------------------------------------
aptRemoveRepository() {
# ----------------------------------------------------------------------------

    # usage: aptRemoveRepository REPOSETORY-NAME
    if [[ -z $1 ]] ; then
	err_msg "missing REPOSETORY-NAME in line $(caller)"
	exit
    fi
    local SRCL_FNAME="/etc/apt/sources.list.d/${1}.list"
    local PKEY_FNAME="/etc/apt/trusted.gpg.d/${1}.gpg"

    if [[ -e "${PKEY_FNAME}" ]]; then
	echo -e "remove: ${Yellow}${PKEY_FNAME}${_color_Off}"
	rm -f "${PKEY_FNAME}"
    else
	info_msg "${PKEY_FNAME} does not exists."
    fi
    if [[ -e "${SRCL_FNAME}" ]]; then
	echo -e "remove: ${Yellow}${SRCL_FNAME}${_color_Off}"
	rm -f "${SRCL_FNAME}"
    else
	err_msg "REPOSETORY $SRCL_FNAME does not exist!"
    fi
}

# ----------------------------------------------------------------------------
installDebFromURL () {
# ----------------------------------------------------------------------------

    # Installiert ein debian-Paket direkt aus einer URL. Sofern das Paket
    # bereits im ${CACHE} ist, wird es nicht extra ein zweites mal
    # *runtergeladen*. Als zweites Argument kann der Dateiname im ${CACHE}
    # angegeben werden, falls dieser sich nicht *sauber* aus der URL ermitteln
    # lässt.
    #
    # usage:
    #
    #    installDebFromURL <url> [<local-filename>]
    #
    #    installDebFromURL "http://www.teamviewer.com/download/teamviewer_i386.deb"

    local URL="${1}"
    local FNAME="$(stripFilenameFromUrl ${1})"

    if [[ ! -z $2 ]] ; then
        FNAME="${2}"
    fi
    echo
    info_msg "${Green}install deb package: '$FNAME'${_color_Off}"
    cacheDownload "${URL}" "${FNAME}"
    echo ""
    dpkg -i "${CACHE}/${FNAME}"
    apt-get install -fy
    waitKEY
}

# ----------------------------------------------------------------------------
TEMPLATES_installFolder() {
# ----------------------------------------------------------------------------

    # Installiert den angegebenen Ordner aus den ``${TEMPLATES}``
    # Ordner. Existiert bereits eine Sicherung im Ordner der Konfiguration
    # (``${CONFIG}``), wird diese anstatt des Templates verwendet.
    #
    # usage:
    #
    #     TEMPLATES_installFolder {folder} [{owner} [{group} ]]
    #

    if [[ -d "${CONFIG}${1}" ]] ; then
	installFolder "${CONFIG}${1}" "$1" "$2" "$3"
    else
	installFolder "${TEMPLATES}${1}" "$1" "$2" "$3"
    fi
}

# ----------------------------------------------------------------------------
installFolder() {
# ----------------------------------------------------------------------------

    # Installiert den angegebenen Ordner, sofern dieser am Zielort nicht bereits
    # existiert. Existiert der Ordner wird eine Anfrage gestellt ob dieser
    # Ordner ersetzt werden soll.
    #
    # usage:
    #
    #     installFolder {src-folder} {dst-name} [{owner} [{group} ]]
    #
    # ACHTUNG: der dst-name ist der Name des src-folder im Ziel!!!
    #
    #   installFolder /SRC /DST
    #
    # ersetz den Ordner /DST durch den Ordner SRC. Es wird nicht der Ordner SRC
    # in den Ordner /DST kopiert, so wie das "cp -r" machen würde.

    local owner=${3-$(id -un)}
    local group=${4-$(id -gn)}
    local parent_folder=$(dirname "${2}")

    if [[ ! -d "${1}" ]] ; then
        err_msg "folder ${1} does not exists"
	waitKEY

    elif [[ ! -d "${2}" ]] ; then
        info_msg "${2} will be installed"
	mkdir -pv "$parent_folder"
        cp -rv "${1}" "${2}" | prefix_stdout "${BGreen}install${_color_Off}: "
        chown -R $owner:$group "${2}"

    elif askNy "should ${BYellow}'$2'${_color_Off} be replaced by '$1'? (${BRed}WARNING:${_color_Off} no backup copy)"; then
	rm -rf "${2}"
        cp -rv "${1}" "${2}" | prefix_stdout "${BGreen}install${_color_Off}: "
        chown -R $owner:$group "${2}"
    fi
}

# ----------------------------------------------------------------------------
TEMPLATES_InstallOrMerge() {
# ----------------------------------------------------------------------------

    # Installiert die angegebene Datei aus dem ${TEMPLATES} Ordner, sofern diese
    # am Zielort nicht bereits existiert. Im Falle, dass die Datei im Ziel
    # bereits existiert oder es eine Sicherung im ${CONFIG}-Ordner gibt, wird
    # ein Merge durchgeführt. Mit dem Schalter --eval wird die Template Datei
    # vorher noch evaluiert (``echo "$(cat ${TEMPLATES}${dst})"``)
    #
    # usage:
    #
    #     TEMPLATES_InstallOrMerge [--eval] {file} [{owner} [{group} [{chmod}]]]
    #
    #     TEMPLATES_InstallOrMerge /etc/updatedb.conf root root 644

    local do_eval=0
    if [[ "$1" == "--eval" ]]; then
        do_eval=1; shift
    fi
    local dst="${1}"
    local owner=${2-$(id -un)}
    local group=${3-$(id -gn)}
    local chmod=${4-755}

    info_msg "install: ${dst}"

    if [[ ! -f "${CONFIG}${dst}" && ! -f "${TEMPLATES}${dst}" ]] ; then
        err_msg "none of this (source) files exists"
        err_msg "  ${TEMPLATES}${dst}"
        err_msg "  ${CONFIG}${dst}"
        err_msg "... can't install $dst / exit installation with error 42"
        waitKEY
        return 42
    fi

    local template_file="${TEMPLATES}${dst}"
    if [[ "$do_eval" == "1" ]]; then
        info_msg "BUILD template ${BRed}${template_file}${_color_Off}"
        if [[ -f "${TEMPLATES}${dst}" ]] ; then
            template_file="${CACHE}${dst}"
            mkdir -p $(dirname "${template_file}")
            eval "echo \"$(cat ${TEMPLATES}${dst})\"" > "${template_file}"
        else
            err_msg "  FAILED ${template_file}"
            return 42
        fi
    fi

    if [[ -f "${dst}" ]] ; then
        info_msg "file ${dst} allready exists on this host"
    fi
    info_msg "examine <prefix>${dst} file(s)"

    if [[ -f "${dst}" && -f "${CONFIG}${dst}" && -f "${template_file}" ]] ; then

        # Es existieren alle drei Dateien (Ziel, TEMPLATES u. CONFIG).  Es wird
        # ein Merge aller drei Dateien durchgeführt. Als "gemeinsammer Vorfahre"
        # (*ancestor*) wird die CONFIG Datei *angenommen*. Das ist *formal*
        # nicht ganz korrekt, denn eigentlich ist der "gemeinsamme Vorgänger"
        # eine *Vorgängerversion* der Template Datei. Aber den gemeinsammen
        # Vorfahren kennt man nun eh nicht mehr (es können sich ja auch alle
        # drei Dateien gleichzeitig geändert haben).  Die TEMPLATES Datei ist
        # genau genommen der TRUNK. Die Ziel und CONFIG Datei bilden den Branch,
        # der mit der ersten Sicherung in CONFIG entstanden ist.
        #
        # Da es aber die CONFIG Datei ist, die *weiterentwickelt* werden soll,
        # ist diese auch der Vorfahre von der Ziel-Datei.
        #
        #  1. Argument  /etc/apache2/apache2.conf             <-- merge
        #  2. Argument  ${TEMPLATES}/etc/apache2/apache2.conf
        #  3. Argument  ${CONFIG}/etc/apache2/apache2.conf    <-- merge

        while true; do

            merge3Files "${dst}" "${template_file}" "${CONFIG}${dst}"
            exitCode=$?

            if [[ $exitCode == 0 ]]; then
                break
            elif [[ $exitCode == 1 ]]; then
                if ! askYn "merge failed, repeat merge?"; then
                    err_msg "... exit installation with error 42"
                    exit 42
                fi
            elif [[ $exitCode > 1 ]]; then
                # Es wurde die Zieldatei verändert, jetzt müssen noch Benutzer, Gruppe &
                # Rechte angepasst werden.
                chown "${owner}":"${group}" ${dst}
                chmod "${chmod}" "${dst}"
                break
            fi
        done

    elif [[ -f "${dst}" && -f "${template_file}" ]] ; then

        # Die Zieldatei existiert, es gibt ein TEMPLATE aber es gibt keine
        # Sicherung
        #
        #  1. Argument  /etc/apache2/apache2.conf          <-- merge im dst file
        #  2. Argument  ${TEMPLATES}/etc/apache2/apache2.conf

        while true; do

            merge2Files "${dst}" "${template_file}"
            exitCode=$?

            if [[ $exitCode == 0 ]]; then
                break
            elif [[ $exitCode == 1 ]]; then
                if ! askYn "merge failed, repeat merge?"; then
                    err_msg "... exit installation with error 42"
                    exit 42
                fi
            elif [[ $exitCode > 1 ]]; then
                # Es wurde die Zieldatei verändert, jetzt müssen noch Benutzer,
                # Gruppe & Rechte angepasst werden.
                chown "${owner}":"${group}" ${dst}
                chmod "${chmod}" "${dst}"
                break
            fi
        done

    elif [[ -f "${dst}" && -f "${CONFIG}${dst}" ]] ; then

        # Die Zieldatei existiert, es gibt KEIN TEMPLATE aber es gibt EINE
        # Sicherung
        #
        #  1. Argument  /etc/apache2/apache2.conf          <-- merge im dst file
        #  2. Argument  ${CONFIG}/etc/apache2/apache2.conf

        while true; do

            merge2Files "${dst}" "${CONFIG}${dst}"
            exitCode=$?

            if [[ $exitCode == 0 ]]; then
                break
            elif [[ $exitCode == 1 ]]; then
                if ! askYn "merge failed, repeat merge?"; then
                    err_msg "... exit installation with error 42"
                    exit 42
                fi
            elif [[ $exitCode > 1 ]]; then
                # Es wurde die Zieldatei verändert, jetzt müssen noch Benutzer,
                # Gruppe & Rechte angepasst werden.
                chown "${owner}":"${group}" ${dst}
                chmod "${chmod}" "${dst}"
                break
            fi
        done

    elif [[ ! -f "${dst}" && -f "${CONFIG}${dst}" && -f "${template_file}"  ]] ; then

        # Die Zieldatei existiert NICHT, aber es gibt eine CONFIG-Sicherung und
        # die TEMPLATES Datei. Es wird ein Merge von TEMPLATES nach CONFIG
        # durchgeführt und dann wird CONFIG installiert.

        #  1. Argument  ${CONFIG}/etc/apache2/apache2.conf    <-- merge backup-file
        #  2. Argument  ${TEMPLATES}/etc/apache2/apache2.conf

        while true; do

            merge2Files "${template_file}" "${CONFIG}${dst}" "${dst}"
            exitCode=$?

            if [[ $exitCode == 0 ]]; then
                break
            elif [[ $exitCode == 1 ]]; then
                if ! askYn "merge failed, repeat merge?"; then
                    err_msg "... exit installation with error 42"
                    exit 42
                fi
            elif [[ $exitCode > 1 ]]; then
                break
            fi

        done
        sudo install -v -o "${owner}" -g "${group}" -m "${chmod}" "${CONFIG}${dst}" "${dst}"


    elif [[ ! -f "${dst}" && -f "${template_file}" ]] ; then
        # Die Zieldatei existiert NICHT, es gibt ein TEMPLATE aber es gibt KEINE
        # Sicherung
        echo
        sudo install -v -o "${owner}" -g "${group}" -m "${chmod}" "${template_file}" "${dst}"

    elif [[ ! -f "${dst}" && -f "${CONFIG}${dst}" ]] ; then
        # Die Zieldatei existiert NICHT, es gibt KEIN TEMPLATE aber es gibt eine
        # Sicherung
        echo
        sudo install -v -o "${owner}" -g "${group}" -m "${chmod}" "${CONFIG}${dst}" "${dst}"

    else
        err_msg "Dieser Fall ist nicht kausal / nicht implementiert :-o"
    fi
}

# ----------------------------------------------------------------------------
CONFIG_installFolder() {
# ----------------------------------------------------------------------------

    # Installiert den angegebenen Ordner aus den ``${CONFIG}`` Ordner.
    #
    # CONFIG_installFolder {folder} [{owner} [{group} ]]
    #

    installFolder "${CONFIG}${1}" "${1}" $2 $3
}

# ----------------------------------------------------------------------------
CONFIG_showDiff() {
# ----------------------------------------------------------------------------

    # vergleicht die übergebene Datei mit der korrespondierenden Datei im
    # $CONFIG Backup

    if [[ -e "${CONFIG}${1}" ]]; then
        if cmp --silent "${CONFIG}${1}" "${1}"; then
            rstBlock "${BYellow}  ${1} and backup are equal${_color_Off}"
        else
            rstBlock "${BYellow}  ${1} and backup are different\n"
            printf "// diff START ========================================${_color_Off}\n"
            $DIFF_CMD -u "${CONFIG}${1}" "${1}"
            printf "${BYellow}// diff END ==========================================${_color_Off}\n"
        fi
    else
        err_msg "${CONFIG}${1} does not exists"
    fi
}

# ----------------------------------------------------------------------------
CONFIG_Backup() {
# ----------------------------------------------------------------------------

    # legt in dem Ordner ${CONFIG} die Kopien, der als Argumente übergebenen
    # Dateien und Ordner an

    if [[ -z "${CONFIG}" ]]; then
        err_msg "environment \${CONFIG} is not defined"
        exit 42
    fi

    for ITEM in "$@"  ; do
        if [[ ! -e "${ITEM}" ]]; then
            err_msg "path \"${ITEM}\" does not exists / skip backup"
            continue
        fi
        if [[ -d "${ITEM}" ]]
        then
            echo "backup folder : ${ITEM}"
        else
            echo "backup file   : ${ITEM}"
        fi
        local _d=${CONFIG}$(dirname "${ITEM}")
        mkdir -p "$_d"
        cp -ar "${ITEM}" "$_d"
    done
    chown -R ${SUDO_USER}:${SUDO_USER} ${CONFIG}
    chmod -R u+r ${CONFIG}
}

# ----------------------------------------------------------------------------
CONFIG_cryptedBackup(){
# ----------------------------------------------------------------------------

    # legt in dem Ordner ${CONFIG} die verschlüsselten Kopien, der als Argumente
    # übergebenen Dateien und Ordner an

    if [[ -z "${CONFIG}" ]]; then
        err_msg "environment \${CONFIG} is not defined"
        exit 42
    fi

    askPassphrase

    for ITEM in "$@"; do

        if [[ ! -e "${ITEM}" ]]; then
            err_msg "path \"${ITEM}\" does not exists / skip backup"
            continue
        fi

        local _d=${CONFIG}$(dirname "${ITEM}")
        mkdir -p "$_d"
        if [[ -d "${ITEM}" ]]
        then
            echo "backup folder : ${ITEM} --> ${ITEM}.tar.gpg"
            rm -f "${CONFIG}${ITEM}.tar.gpg"
            tar -cf - "${ITEM}" | gpg --batch --no-options --openpgp --passphrase "${passphrase}"  --set-filename "${ITEM}" --symmetric --output "${CONFIG}${ITEM}.tar.gpg"
        else
            echo "backup file : ${ITEM} --> ${ITEM}.gpg"
            rm -f "${CONFIG}${ITEM}.gpg"
            gpg --batch --no-options --passphrase "${passphrase}" --set-filename "${ITEM}" --symmetric --output "${CONFIG}${ITEM}.gpg" "${ITEM}"
        fi
    done

}


# Samba
# =====

if [[ -z "$SAMBA_SERVER" ]]; then
    SAMBA_SERVER=127.0.0.1
fi

# Debian's Apache Setup
# =====================

if [[ -z "$APACHE_SETUP" ]]; then
    APACHE_SETUP="/etc/apache2"
fi

if [[ -z "${APACHE_SITES_AVAILABE}" ]]; then
    APACHE_SITES_AVAILABE="${APACHE_SETUP}/sites-available"
    # APACHE_SITES_ENABLED="${APACHE_SETUP}/sites-enabled"
fi
if [[ -z "${APACHE_MODS_AVAILABE}" ]]; then
    APACHE_MODS_AVAILABE="${APACHE_SETUP}/mods-available"
    # APACHE_MODS_ENABLED="${APACHE_SETUP}/mods-enabled"
fi
if [[ -z "${APACHE_CONF_AVAILABE}" ]]; then
    APACHE_CONF_AVAILABE="${APACHE_SETUP}/conf-available"
    # APACHE_CONF_ENABLED="${APACHE_SETUP}/conf-enabled"
fi

# ----------------------------------------------------------------------------
APACHE_install_site() {
# ----------------------------------------------------------------------------

    # Installiert eine Apache-Site aus den ``${TEMPLATES}`` Ordner. Nach dem
    # Installieren (sites-available) wird die *Site* aktiviert (sites-enabled)
    # und es wird die Konfiguration des Apache Servers neu geladen, so das die
    # Site gleich aktiv ist.
    #
    # usage:
    #
    #   APACHE_install_site [--eval] <apache-sites.conf-filename>
    #
    #   APACHE_install_site phpvirtualbox

    local do_eval=""
    if [[ "$1" == "--eval" ]]; then
        do_eval=$1; shift
    fi

    local CONF
    for CONF in $*; do
        CONF=${CONF%.conf}.conf
        TEMPLATES_InstallOrMerge $do_eval "${APACHE_SITES_AVAILABE}/${CONF}" root root 644
    done
    sudo a2ensite -q "$@"
    APACHE_reload
}

# ----------------------------------------------------------------------------
APACHE_install_conf(){
# ----------------------------------------------------------------------------

    # Installiert eine Apache-Konfiguration aus den ``${TEMPLATES}``
    # Ordner. Nach dem Installieren (conf-available) wird die *Konfiguration*
    # aktiviert (conf-enabled) und es wird die Konfiguration des Apache Servers
    # neu geladen, so das die Site gleich aktiv ist.
    #
    # usage:
    #
    #   APACHE_install_conf <my.conf-filename>
    #
    #   APACHE_install_conf security

    local CONF
    for CONF in $*; do
        CONF=${CONF%.conf}.conf
        TEMPLATES_InstallOrMerge "${APACHE_CONF_AVAILABE}/${CONF}" root root 644
    done
    sudo a2enconf -q "$@"
    APACHE_reload
}

# ----------------------------------------------------------------------------
APACHE_disable_mod_conf(){
# ----------------------------------------------------------------------------

    # FIXME: Wie soll man die conf-Dateien aus dem mods-enable normaler Weise
    # anpassen bzw. wie kann man a2enmod daran hindern diese zu aktivieren? Ich
    # hab keine Antwort in der Doku gefunden, deshalb benenne ich die conf-Datei
    # einfach um
    local CONF
    for CONF in $*; do
        CONF=${CONF%.conf}.conf
        local cfgFile="${APACHE_MODS_AVAILABE}/${CONF}"
        if [[ -f "${cfgFile}" ]]; then

            if [[ -f "${cfgFile}-disabled" ]]; then
                info_msg "allready disabled: ${cfgFile}-disabled"
            else
                info_msg "disabling ${cfgFile}"
                mv "${cfgFile}" "${cfgFile}-disabled"
            fi
            info_msg "create empty ${cfgFile}"
            echo "# This is an empty default configuration of module:" > $cfgFile
            echo "#     ${CONF%.conf}.load"                            >> $cfgFile
            echo "# The origin was saved in file:"                     >> $cfgFile
            echo "#     ${CONF}-disabled"                              >> $cfgFile
            echo "# Dont't edit this file it, will be deleted!!"       >> $cfgFile
            echo "# Instead, create or edit file:"                     >> $cfgFile
            echo "#     ${APACHE_CONF_AVAILABE}/${CONF}"               >> $cfgFile
        else
            info_msg "config file ${cfgFile} does not (yet) exists."
        fi
    done
    APACHE_reload
}

#  ----------------------------------------------------------------------------
APACHE_reload() {
# ----------------------------------------------------------------------------
    rstBlock "${BGreen}Reload der Apache Konfiguration ...${_color_Off}"
    echo
    sudo apachectl configtest
    sudo service apache2 force-reload
}

# ----------------------------------------------------------------------------
APACHE_dissable_site() {
# ----------------------------------------------------------------------------

    # Deaktiviert eine Site (sie bleibt allerdings in den *available* Sites
    # erhalten). Nach der Deaktivierung wird die Konfiguration des Apache
    # Servers neu geladen. Damit sind dann auch alle Apache-Prozesse die an
    # diese Site gebunden waren beendet.
    #
    # usage:
    #
    #   APACHE_dissable_site <site-name>
    #
    #   APACHE_disable_site fxSyncServer

    sudo a2dissite -q "$@"
    sudo service apache2 force-reload
}

# Firefox
# =======

if [[ -z "$FFOX_GLOBAL_EXTENSIONS" ]]; then
    FFOX_GLOBAL_EXTENSIONS=/usr/lib/firefox-addons/extensions
fi

# ----------------------------------------------------------------------------
FFOX_globalAddOn() {
# ----------------------------------------------------------------------------

    # Installiert / Deinstalliert ein *globales* FireFox-AddOn. Diese werden von
    # allen FFox-Sitzungen geladen, die auf diesem Host laufen. Für die
    # Deinstallation wird ebenfalls die ``.xpi`` Datei benötigt, mit der man das
    # AddOn mal installiert hatte, den nur darin steht die ID, unter der dieses
    # AddOn (global unter ``${FFOX_GLOBAL_EXTENSIONS}``) installiert wurde.
    #
    # usage:
    #
    #   FFOX_globalAddOn [install|deinstall] <xpi-filename>
    #
    #   FFOX_globalAddOn install ${CACHE}/firefox_addon-627512-latest.xpi

    # get extension UID from install.rdf

    echo
    UID_ADDON=$(unzip -p $2 manifest.json \
        | python -c  'import json,sys;print json.load(sys.stdin)["applications"]["gecko"]["id"]' 2>/dev/null)
    if [[ -z ${UID_ADDON} ]] ; then
        UID_ADDON=$(unzip -p $2 install.rdf \
                           | grep "<em:id>" \
                           | head -n 1 \
                           | sed 's/^.*>\(.*\)<.*$/\1/g' )
    fi
    if [[ -z ${UID_ADDON} ]] ; then
        # Scheinbar gibt es Plugins bei denen der Namensraum (em) nicht
        # expliziet angegeben ist, diese verwenden dann das <id> Tag.
        UID_ADDON=$(unzip -p $2 install.rdf \
                           | grep "<id>" \
                           | head -n 1 \
                           | sed 's/^.*>\(.*\)<.*$/\1/g' )
    fi
    if [[ -z ${UID_ADDON} ]] ; then
        err_msg "can't read tag '<em:id>' from: $2"
    else
        case $1 in
            install)
                info_msg "installing: ${UID_ADDON}.xpi --> ${FFOX_GLOBAL_EXTENSIONS}"
                sudo cp $2 "${FFOX_GLOBAL_EXTENSIONS}/${UID_ADDON}.xpi"
                ;;
            deinstall)
                if [[ -f "${FFOX_GLOBAL_EXTENSIONS}/${UID_ADDON}.xpi" ]] ; then
                   rstBlock "remove AddOn ${BGreen}${UID_ADDON}.xpi${_color_Off} from ${FFOX_GLOBAL_EXTENSIONS}"
                   sudo rm -v "${FFOX_GLOBAL_EXTENSIONS}/${UID_ADDON}.xpi"
                else
                   rstBlock "AddOn ${BGreen}${UID_ADDON}.xpi${_color_Off} does not exists in ${FFOX_GLOBAL_EXTENSIONS}"
                fi
                ;;
            *)
                err_msg "invalid argument '${2}' in line $(caller)"
                return 42
                ;;
            esac
    fi
}

# GNOME
# =====

if [[ -z "$GNOME_APPL_FOLDER" ]]; then
    GNOME_APPL_FOLDER=/usr/share/applications
fi

# ----------------------------------------------------------------------------
GNOME_SHELL_installLauncher () {
# ----------------------------------------------------------------------------

    # usage:
    #
    #   GNOME_SHELL_installLauncher dmSDK-Emacs.desktop "$launcher_dmSDKEmacs"

    echo
    echo "$1 --> $GNOME_APPL_FOLDER"
    echo "$2" | sudo tee "$GNOME_APPL_FOLDER/$1" > /dev/null
}

# ----------------------------------------------------------------------------
getUrlAfterRedirect() {
# ----------------------------------------------------------------------------

    # Ermittelt die *echte* URL, die sich aus Redirects ergibt.

    # usage: getUrlAfterRedirect <url>

    curl -s -L -I -o /dev/null -w %{url_effective} "$1"
}

# ----------------------------------------------------------------------------
stripFilenameFromUrl() {
# ----------------------------------------------------------------------------

    # usage: stripFilenameFromUrl <url>

    # siehe Parameter-Substitution
    # http://tldp.org/LDP/abs/html/parameter-substitution.html
    local x
    x=${1##*/}
    x=${x%%\?*}
    echo $x
}

# ----------------------------------------------------------------------------
stripHostnameFromUrl() {
# ----------------------------------------------------------------------------

    # usage: stripHostnameFromUrl <url>

    # siehe Parameter-Substitution
    # http://tldp.org/LDP/abs/html/parameter-substitution.htm

    local x
    x=${1#*\/\/}
    x=${x%%\/*}
    echo $x
}

# ----------------------------------------------------------------------------
setValueCfgFile() {
# ----------------------------------------------------------------------------

    # Setzt den Wert einer Variablen in einer (Config-)Datei. Gibt es die
    # Variable nicht, dann wird sie am Ende der Datei hinzugefügt,

    # usage:
    #
    #     setValueCfgFile <cfgFile> <var_name> <var_value> [<assignment_operator> [<comment_char>]]
    #
    #     setValueCfgFile /etc/default/rsync RSYNC_ENABLE true
    #     setValueCfgFile /etc/hosts 127.0.0.1 productsearch.ubuntu.com '\s+' '#'

    local _cfgFile="$1"
    local _name="$2"
    local _value="$3"
    local _operator="${4:-=}"
    local _comment="${5:-#}"
    local retCode=0
    local name_match="^${_name}\s*${_operator}\s*"

    #set -x
    if grep -q "${name_match}" "${_cfgFile}"; then
        local _name=$(echo "$2" | sed 's,/,\\/,g')
        local _value=$(echo "$3" | sed 's,/,\\/,g')
        #set -x
        sed  -i "s/\(${name_match}\)[^${_comment}]*\(${_comment}.*\)*\$/\1${_value} \2/" "${_cfgFile}"
        #set +x
    else
        echo >> "${_cfgFile}"
        echo "${_name}${_operator}${_value}" >> "${_cfgFile}"
        retCode=1
    fi
    #set +x
    return $retCode
}


# Debian's OpenLDAP Setup
# =======================

if [[ -z ${LDAP_SERVER} ]]; then
    LDAP_SERVER="$(hostname 2>/dev/null)"
fi
if [[ -z ${LDAP_SSL_PORT} ]]; then
    LDAP_SSL_PORT=636
fi

if [[ -z ${OPENLDAP_USER} ]]; then
    OPENLDAP_USER=openldap
fi

if [[ -z ${SLAPD_DBDIR} ]]; then
    SLAPD_DBDIR=/var/lib/ldap
fi

if [[ -z ${SLAPD_CONF} ]]; then
    SLAPD_CONF="/etc/ldap/slapd.d"
fi

if [[ -z ${LDAP_AUTH_BaseDN} ]]; then
    LDAP_AUTH_BaseDN="dc=`echo $LDAP_SERVER | sed 's/^\.//; s/\.$//; s/\./,dc=/g'`"
fi

if [[ -z ${LDAP_AUTH_DC} ]]; then
    LDAP_AUTH_DC="`echo $LDAP_SERVER | sed 's/^\.//; s/\..*$//'`"
fi


encode_utf8() {
    # Make the value utf8 encoded. Takes one argument and utf8 encode it.
    # Usage: val=`encode_utf8 <value>`
  perl -e 'use Encode; print encode_utf8($ARGV[0]);' "$1"
}

# ----------------------------------------------------------------------------
LDAP_create_DIT() {
# ----------------------------------------------------------------------------

    # Create a new Directory-Information-Tree.

    # Usage: create_new_DIT <basedn> <dc> <organization> <passphrase>

    # e.g.: create_new_DIT "dc=myhost.local" "myhost" "my-org-name"

    local basedn="$1"  # e.g.: domain really.argh.org --> 'dc=really,dc=argh,dc=org'
    local DC="$2"      # e.g. the hostname --> 'really'
    local ORGANIZATION=$(encode_utf8 "$3")  # Encode to utf8
    local passphrase="$4"
    local SSHA_PASSWORD=$(slappasswd -s "$passphrase") # interactive
    local exit_code

    local ldif_dn ldif_dit _ldapadd

    local SUFFIX="$basedn"
    local BACKEND="mdb"
    local BACKENDOBJECTCLASS="olcMdbConfig"
    local BACKENDOPTIONS="olcDbMaxSize: 1073741824"

    ldif_dn=$(cat <<EOF
# The Organization definition.
dn: ${SUFFIX}
objectClass: top
objectClass: dcObject
objectClass: organization
o: ${ORGANIZATION}
dc: ${DC}

# Organization's admin
dn: cn=admin,${SUFFIX}
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: admin
description: LDAP administrator
userPassword: ${SSHA_PASSWORD}
EOF
)

    ldif_dit=$(cat <<EOF
# The database definition.
dn: olcDatabase=${BACKEND},cn=config
objectClass: olcDatabaseConfig
objectClass: ${BACKENDOBJECTCLASS}
olcDatabase: ${BACKEND}
# Checkpoint the database periodically in case of system
# failure and to speed slapd shutdown.
olcDbCheckpoint: 512 30
${BACKENDOPTIONS}
# Save the time that the entry gets modified, for database #1
olcLastMod: TRUE
# The base of your directory in database #1
olcSuffix: ${SUFFIX}
# Where the database file are physically stored for database #1
olcDbDirectory: ${SLAPD_DBDIR}
# olcRootDN directive for specifying a superuser on the database. This
# is needed for syncrepl.
olcRootDN: cn=admin,${SUFFIX}
olcRootPW: ${SSHA_PASSWORD}
# Indexing options for database #1
olcDbIndex: objectClass eq
olcDbIndex: cn,uid eq
olcDbIndex: uidNumber,gidNumber eq
olcDbIndex: member,memberUid eq
# addittional DB index
olcDbIndex: sn pres,sub,eq
olcDbIndex: displayName pres,sub,eq
olcDbIndex: default sub
olcDbIndex: mail,givenName eq,subinitial
olcDbIndex: dc eq
# The userPassword by default can be changed by the entry owning it if
# they are authenticated. Others should not be able to see it, except
# the admin entry above.
# Allow update of authenticated user's shadowLastChange attribute.
# Updating it on password change is implemented at least by libpam-ldap,
# libpam-ldapd, and the slapo-smbk5pwd overlay.
olcAccess: to attrs=userPassword,shadowLastChange
  by dn.exact=gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth manage
  by dn="cn=admin,${SUFFIX}" write
  by self write
  by anonymous auth
  by * none
# User should be able to set 'loginShell, gecos'
olcAccess: to attrs=loginShell,gecos
  by dn="cn=admin,${SUFFIX}" write
  by self write
  by * read
olcAccess: to dn.base=""
  by * read
# The admin dn (olcRootDN) bypasses ACLs and so has total access,
# everyone else can read everything and a login with the SASL EXTERNAL
# method get 'manage' access.
olcAccess: to *
  by dn="cn=admin,${SUFFIX}" write
  by dn.exact=gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth manage
  by self write
  by * read
EOF
)
    rstHeading "DIT DB with RootDN 'cn=admin,${SUFFIX}'" section
    echo
    _ldapadd="ldapadd -H ldapi:// -Y EXTERNAL -D cn=config"
    echo -e "$ldif_dit" | prefix_stdout "<--|"
    echo -e "${BRed}$_ldapadd${_color_Off}" >&2
    echo -e "$ldif_dit" | $_ldapadd || exit_code=1
    if [ "$exit_code" ]; then
        err_msg "DIT configuration failed"
    fi
    waitKEY

    rstHeading "Organization 'dc=${DC}' with LDAP admin" section
    echo
    _ldapadd="ldapadd -H ldapi:// -D cn=admin,${SUFFIX} -x"
    echo -e "$ldif_dn" | prefix_stdout "<--|"
    echo -e "${BRed}$_ldapadd$ -W${_color_Off}" >&2
    echo -e "$ldif_dn" | $_ldapadd -x -w ${passphrase} || exit_code=1
    if [ "$exit_code" ]; then
        err_msg "DC configuration failed"
    fi
    waitKEY
    return
}


# ----------------------------------------------------------------------------
LDAP_setPasswd() {
# ----------------------------------------------------------------------------

    # usage:
    #
    #   LDAP_setPasswd <username>

    echo "Passwort für Benutzer '$1' eingeben ..."
    # Der Admin (root) muss das Passwort der Benutzer mit ldapsetpasswd ändern,
    # die Benutzer selber können passwd verwenden, wenn sie ihr passwort ändern
    # möchten.
    ldapsetpasswd $1
}

# ----------------------------------------------------------------------------
LDAP_addUserToGroup() {
# ----------------------------------------------------------------------------

    # usage:
    #
    #   LDAP_addUserToGroup <username> <group>

    info_msg "Benutzer '$1' wird in Gruppe '$2' aufgenommen"
    ldapaddusertogroup $1 $2
}

# ----------------------------------------------------------------------------
LDAP_insertUser() {
# ----------------------------------------------------------------------------
    # usage:
    #
    #   LDAP_insertUser <username> <uid>

    if [[ -z $1 ]]; then
        err_msg "Es muss das zu erstellende Benutzerlogin angegeben werden."
        return 42
    fi
    rstHeading "Anlegen des Benutzers $1 (Gruppe $1)" chapter
    echo
    ldapaddgroup $1 $2
    ldapadduser $1 $1 $2

}
