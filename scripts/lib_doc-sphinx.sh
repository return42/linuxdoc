# -*- mode: sh; sh-shell: bash -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

# Sphinx doc
# ----------

GH_PAGES="build/gh-pages"

# FIXME: what is with this path names, when we are in a LXC instance?
DOC_SRC="${DOC_SRC:-./doc}"
DOC_DIST="${DOC_DIST:=dist/doc}"
DOC_BUILD="${DOC_BUILD:=build/doc}"

[ "${V}" -ge 1 ] && SPHINX_VERBOSE="-v"

doc.html.help() {
    cat <<EOF
build HTML documentation

  source:  ${DOC_SRC}
  build:   ${DOC_BUILD}
  dest:    ${DOC_DIST}

usage:
  ${MAIN} ${MAIN_CMD}
EOF
}

doc.html() {
    msg.build SPHINX "HTML ${DOC_SRC} --> file://$(readlink -e "$(pwd)/${DOC_DIST}")"
    (   set -e
    doc.prebuild
    # shellcheck disable=SC2086
    sphinx-build \
        ${SPHINX_VERBOSE} ${SPHINX_OPTS} \
        -b html -c "${DOC_SRC}" -d "${DOC_BUILD}/.doctrees" "${DOC_SRC}" "${DOC_DIST}"
    )
    sh.prompt-err $?
}

doc.live.help() {
    cat <<EOF
autobuild HTML documentation while editing

  source:  ${DOC_SRC}
  build:   ${DOC_BUILD}
  dest:    ${DOC_DIST}

usage:
  ${MAIN} ${MAIN_CMD}
EOF
}

doc.live() {
    msg.build SPHINX "autobuild ${DOC_SRC} --> file://$(readlink -e "$(pwd)/${DOC_DIST}")"
    (   set -e
    doc.prebuild
    # shellcheck disable=SC2086
    sphinx-autobuild \
        ${SPHINX_VERBOSE} ${SPHINX_OPTS} \
        --open-browser --host 0.0.0.0 \
        -b html -c "${DOC_SRC}" -d "${DOC_BUILD}/.doctrees" "${DOC_SRC}" "${DOC_DIST}"
    )
    sh.prompt-err $?
}

doc.clean.help() {
    $FMT <<EOF
clean documentation build
EOF
}

doc.clean() {
    msg.build CLEAN "docs -- ${DOC_BUILD} ${DOC_DIST}"
    rm -rf "${GH_PAGES}" "${DOC_BUILD}" "${DOC_DIST}"
    sh.prompt-err $?
}

doc.prebuild() {
    # Dummy function to run some actions before sphinx-doc build gets started.
    # This finction needs to be overwritten by the application script.
    true
    sh.prompt-err $?
}


doc.gh-pages.help() {
    $FMT <<EOF
deploy on gh-pages branch
EOF
}

doc.gh-pages() {

    msg.build GH-PAGES "HTML ${DOC_SRC}"

    local head
    local branch
    local remote
    local remote_url

    # The commit history in the gh-pages branch makes no sense, the history only
    # inflates the repository unnecessarily.  Therefore a *new orphan* branch
    # is created each time we deploy on the gh-pages branch.

    doc.clean
    doc.prebuild
    doc.html

    [ "${V}" -ge 2 ] && set -x
    head="$(git rev-parse HEAD)"
    branch="$(git name-rev --name-only HEAD)"
    remote="$(git config branch."${branch}".remote)"
    remote_url="$(git config remote."${remote}".url)"

    msg.build GH-PAGES "prepare folder: ${GH_PAGES}"
    msg.build GH-PAGES "remote of the gh-pages branch: ${remote} / ${remote_url}"
    msg.build GH-PAGES "current branch: ${branch}"

    # prepare the *orphan* gh-pages working tree
    (
        git worktree remove -f "${GH_PAGES}"
        git branch -D gh-pages
    ) &> /dev/null  || true
    git worktree add --no-checkout "${GH_PAGES}" "${remote}/master"

    pushd "${GH_PAGES}" &> /dev/null || return 42
    git checkout --orphan gh-pages
    git rm -rfq .
    popd &> /dev/null || return 42

    cp -r "${DOC_DIST}"/* "${GH_PAGES}"/
    touch "${GH_PAGES}/.nojekyll"
    cat > "${GH_PAGES}/404.html" <<EOF
<html><head><META http-equiv='refresh' content='0;URL=index.html'></head></html>
EOF
    pushd "${GH_PAGES}" &> /dev/null  || return 42
    git add --all .
    git commit -q -m "gh-pages build from: ${branch}@${head} (${remote_url})"
    git push -f "${remote}" gh-pages
    popd &> /dev/null  || return 42

    [ "${V}" -ge 2 ] && set +x
    msg.build GH-PAGES "deployed"
}
