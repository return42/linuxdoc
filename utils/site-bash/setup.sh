#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh -*-
# ----------------------------------------------------------------------------
# Purpose:     common environment customization
# ----------------------------------------------------------------------------

if [[ -z "${REPO_ROOT}" ]]; then
    REPO_ROOT="$(dirname ${BASH_SOURCE[0]})"
    while([ -h "${REPO_ROOT}" ]); do
        REPO_ROOT=`readlink "${REPO_ROOT}"`
    done
    REPO_ROOT=$(cd ${REPO_ROOT}/.. && pwd -P )
fi


_color_Off='\e[0m'  # Text Reset
BYellow='\e[1;33m'

cfg_msg() {
    echo -e "${BYellow}CFG:${_color_Off} $*" >&2
}

if [[ ! -e "${REPO_ROOT}/.config" ]]; then
    cfg_msg "installing ${REPO_ROOT}/.config"
    cp "$(dirname ${BASH_SOURCE[0]})/setup_dot_config" "${REPO_ROOT}/.config"
    chown ${SUDO_USER}:${SUDO_USER} "${REPO_ROOT}/.config"
fi
source ${REPO_ROOT}/.config

# setup's pre hook
if declare -F hook_load_setup_pre >/dev/null
then
    hook_load_setup_pre
fi

# source
source ${REPO_ROOT}/utils/site-bash/common.sh

# setup's post hook
if declare -F hook_load_setup_post >/dev/null
then
    hook_load_setup_post
fi

checkEnviroment

# ----------------------------------------------------------------------------
setupInfo () {
# ----------------------------------------------------------------------------
    rstHeading "setup info"
    echo "
CONFIG        : ${CONFIG}
ORGANIZATION  : ${ORGANIZATION}

REPO_ROOT     : ${REPO_ROOT}
SCRIPT_FOLDER : ${SCRIPT_FOLDER}
TEMPLATES     : ${TEMPLATES}
CACHE         : ${CACHE}
WWW_USER      : ${WWW_USER}
WWW_FOLDER    : ${WWW_FOLDER}
DEB_ARCH      : ${DEB_ARCH}

Services & Apps:

  APACHE_SETUP           : ${APACHE_SETUP}
  SAMBA_SERVER           : ${SAMBA_SERVER}
  FFOX_GLOBAL_EXTENSIONS : ${FFOX_GLOBAL_EXTENSIONS}
  GNOME_APPL_FOLDER      : ${GNOME_APPL_FOLDER}

Open LDAP:

  LDAP_SERVER   : ${LDAP_SERVER}
  LDAP_SSL_PORT : ${LDAP_SSL_PORT}
  OPENLDAP_USER : ${OPENLDAP_USER}
  SLAPD_CONF    : ${SLAPD_CONF}
  SLAPD_DBDIR   : ${SLAPD_DBDIR}

ldapscripts DIT (defaults):

  LDAP_AUTH_BaseDN  : ${LDAP_AUTH_BaseDN}
  LDAP_AUTH_DC      : ${LDAP_AUTH_DC}

LSB (Linux Standard Base) and Distribution information.

  DISTRIB_ID          : ${DISTRIB_ID}
  DISTRIB_RELEASE     : ${DISTRIB_RELEASE}
  DISTRIB_CODENAME    : ${DISTRIB_CODENAME}
  DISTRIB_DESCRIPTION : ${DISTRIB_DESCRIPTION}

CWD : $(pwd -P)"
}


