# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=line-too-long, invalid-name, consider-using-f-string
"""Python package meta informations used by setup.py and other project files.
"""

from setuptools import find_packages

package = 'linuxdoc'
version = '20231020'

copyright = '2023 Markus Heiser'  # pylint: disable=redefined-builtin
description = (
    'Sphinx-doc extensions & tools to extract documentation'
    ' from C/C++ source file comments.'
)
license   = 'AGPLv3+'  # pylint: disable=redefined-builtin
keywords = 'sphinx extension doc source code comments kernel-doc linux'

author = 'Markus Heiser'
author_email = 'markus.heiser@darmarIT.de'
authors = [author, ]
emails = [author_email, ]

maintainer = 'Markus Heiser'
maintainer_email = 'markus.heiser@darmarIT.de'
maintainers = [maintainer, ]


url = 'https://github.com/return42/linuxdoc'
docs = 'https://return42.github.io/linuxdoc'
issues = url + '/issues'

project_urls = {
    'Documentation'    : docs,
    'Code'             : url,
    'Issue tracker'    : issues,
    'Changelog'        : url + '/blob/master/CHANGELOG',
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
    'docutils',
    'sphinx',
]

install_requires_txt = "\n".join(install_requires)

test_requires = [
    'pylint'
    ]
test_requires.sort()
test_requires_txt = "\n".join(test_requires)

develop_requires = [
    'argparse-manpage',
    'pallets-sphinx-themes',
    'sphinx-autobuild',
    'sphinx-issues',
    'sphinx-jinja',
    'sphinx-tabs',
    'sphinxcontrib-programoutput',
    'tox',
    'twine',
    ]
develop_requires_txt = "\n".join(develop_requires)

def get_entry_points():
    """get entry points of the python package"""
    return {
        'console_scripts': [

            'linuxdoc.rest = linuxdoc.rest:main',
            'linuxdoc.autodoc = linuxdoc.autodoc:main',
            'linuxdoc.lintdoc = linuxdoc.lint:main',
            'linuxdoc.grepdoc = linuxdoc.grepdoc:main',

            # compatibility / deprecated

            'kernel-doc = linuxdoc.deprecated:cmd_kernel_doc',
            'kernel-autodoc = linuxdoc.deprecated:cmd_kernel_autodoc',
            'kernel-lintdoc = linuxdoc.deprecated:cmd_kernel_lintdoc',
            'kernel-grepdoc = linuxdoc.deprecated:cmd_kernel_grepdoc',

        ]
    }

requirements_txt = """\
%(install_requires_txt)s
""" % globals()

requirements_dev_txt = """\
%(test_requires_txt)s
%(develop_requires_txt)s
""" % globals()

docstring = """\
The LinuxDoc library contains Sphinx-doc extensions and command line tools to
extract documentation from C/C++ source file comments.  Even if this project
started in context of the Linux-Kernel documentation, you can use these
extensions in common Sphinx-doc projects.
"""

README = """\
========
LinuxDoc
========

%(docstring)s

Install
=======

`Install LinuxDoc <%(docs)s/install.html>`__ using `pip
<https://pip.pypa.io/en/stable/getting-started/>`__:

.. code-block:: text

   pip install --user -U linuxdoc


Links
=====

- Documentation:   %(docs)s
- Releases:        https://pypi.org/project/linuxdoc/
- Code:            %(url)s
- Issue tracker:   %(url)s/issues


============ ===============================================
package:     %(package)s (%(version)s)
copyright:   %(copyright)s
e-mail:      %(maintainer_email)s
license:     %(license)s
============ ===============================================
""" % globals()



# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Other Audience",
    "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Utilities",
    "Topic :: Software Development :: Documentation",
    "Topic :: Software Development :: Libraries",
    "Topic :: Text Processing",
]
