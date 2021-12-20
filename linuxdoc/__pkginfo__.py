# -*- coding: utf-8; mode: python; mode: flycheck -*-
# SPDX-License-Identifier: GPL-2.0
# pylint: disable=invalid-name,redefined-builtin
"""
python package meta informations
"""

from setuptools import find_packages

package = 'linuxdoc'
version = '20211220'
license   = 'GPLv2'
description  = (
    'Sphinx-doc extensions & tools to extract documentation'
    ' from C/C++ source file comments.'
)
copyright = '2021 Markus Heiser'

author = 'Markus Heiser'
author_email = 'markus.heiser@darmarIT.de'

maintainer = 'Markus Heiser'
maintainer_email = 'markus.heiser@darmarIT.de'

url = 'https://github.com/return42/linuxdoc'
docs = 'https://return42.github.io/linuxdoc'
issues = url + '/issues'

authors      = [author, ]

emails       = [author_email, ]
keywords     = 'sphinx extension doc source code comments kernel-doc linux'

maintainers = [maintainer, ]

project_urls = {
    'Documentation'    : docs,
    'Code'             : url,
    'Issue tracker'    : issues,
}

packages = find_packages(exclude=['docs', 'tests'])

# https://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files
package_data = {
#     'xxxx' : [
#         'config.ini',
#         'log.ini',
#         'mime.types',
#     ]
}

# https://docs.python.org/distutils/setupscript.html#installing-additional-files
# https://setuptools.readthedocs.io/en/latest/setuptools.html?highlight=options.data_files#configuring-setup-using-setup-cfg-files
# https://www.scivision.dev/newer-setuptools-needed/
# https://setuptools.readthedocs.io/en/latest/history.html#v40-5-0
data_files = [
#     ('/etc/xxxx', [
#         'xxxx/config.ini',
#         'xxxx/log.ini',
#     ])
#     , ('/usr/share/doc/xxxx', [
#         'README.rst',
#         'LICENSE.txt',
#     ])
]

# https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
python_requires ='>=3.7'

# https://packaging.python.org/guides/distributing-packages-using-setuptools/#py-modules
py_modules = []

# Since pip v18.1 [PEP508-URL] is supported!
#
# Don't use depricated [dependency_links] any more.  See [git+] for using repos
# as packages.  E.g. 'xxxx's master from github with *all extras* is added to
# the requirements by::
#
#        xxxx @ git+https://github.com/return42/xxxx[devel,test]
#
#  The setup.py 'extra_requires' addressed with [PEP-508 extras], here in the
#  example 'devel' and 'test' requirements also installed.
#
# [PEP-508 URL]      https://www.python.org/dev/peps/pep-0508/
# [PEP-508 extras]   https://www.python.org/dev/peps/pep-0508/#extras
# [git+] https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support
# [requirements.txt] https://pip.pypa.io/en/stable/user_guide/#requirements-files
# [dependency_links] https://python-packaging.readthedocs.io/en/latest/dependencies.html

install_requires = [
    'fspath',
    'setuptools',
]

install_requires_txt = "\n".join(install_requires)

test_requires = [
    'pylint'
    ]

test_requires_txt = "\n".join(test_requires)

develop_requires = [
    'twine',
    # 'wheel'
    'Sphinx',
    'pallets-sphinx-themes',
    'sphinx-autobuild',
    'sphinx-issues',
    'sphinx-jinja',
    'sphinx-tabs',
    'sphinxcontrib-programoutput',
    # slide-shows with revaljs
    # 'sphinxjp.themes.revealjs @ git+https://github.com/return42/sphinxjp.themes.revealjs',
    # https://jedi.readthedocs.io/
    # 'jedi',
    # epc required by emacs: https://tkf.github.io/emacs-jedi
    # 'epc @ git+https://github.com/tkf/python-epc',
    ]


develop_requires_txt = "\n".join(develop_requires)

def get_entry_points():
    """get entry points of the python package"""
    return {
        'console_scripts': [
            'kernel-doc = linuxdoc.kernel_doc:main',
            'kernel-autodoc = linuxdoc.autodoc:main',
            'kernel-lintdoc = linuxdoc.lint:main',
            'kernel-grepdoc = linuxdoc.grep_doc:main',
        ]
    }

# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = [
    "Development Status :: 5 - Production/Stable",
     "Intended Audience :: Developers",
     "Intended Audience :: Other Audience",
     "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
     "Operating System :: OS Independent",
     "Programming Language :: Python",
     "Programming Language :: Python :: 3",
     "Topic :: Utilities",
     "Topic :: Software Development :: Documentation",
     "Topic :: Software Development :: Libraries",
     "Topic :: Text Processing",
]

docstring = """\
.. sidebar::  Info

   - %(package)s v%(version)s
   - %(copyright)s / %(license)s
   - %(url)s

The LinuxDoc library contains Sphinx-doc extensions and command line tools to
extract documentation from C/C++ source file comments.  Even if this project
started in context of the Linux-Kernel documentation, you can use these
extensions in common Sphinx-doc projects.

Documentation is available at ./docs or jump to:

- %(docs)s

The LinuxDoc repository is hosted at:

- %(url)s

Issue tracker:

- %(url)s/issues

For installation read file ./docs/install.rst or jump to:

- %(docs)s/install.html
""" % globals()

README = """\
========
LinuxDoc
========

%(docstring)s
""" % globals()

requirements_txt = """# -*- coding: utf-8; mode: conf -*-

# requirements of package %(package)s
# --------------------------------

%(install_requires_txt)s

# test requires
# -------------

%(test_requires_txt)s

# develop
# -------

%(develop_requires_txt)s
""" % globals()
