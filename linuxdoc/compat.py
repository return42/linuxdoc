# -*- coding: utf-8; mode: python -*-
# pylint: disable=C, unused-import, invalid-name, missing-docstring
u"""
compat
~~~~~~

Implementation of a compatibility layer for sphinx and docutils related modules.

:copyright:  Copyright (C) 2018 Markus Heiser
:license:    GPL Version 2, June 1991 see Linux/COPYING for details.

Downward compatibility is unfortunately no strength of sphinx-doc `[ref]
<https://github.com/sphinx-doc/sphinx/issues/3212#issuecomment-283756374>`__ and
patch levels are not really exists or if so they are not shipped within LTS
distributions.  Therefor a minimal *compatibility layer* is needed.  Even if we
do our best here, there are also a lot of incompatibilities in between sphinx
docutils whose fixing is out of the scope of this linuxdoc project `[ref]
<https://www.kernel.org/doc/html/latest/doc-guide/sphinx.html#sphinx-install>`__.

To get best results (and less warnings) its inevitable to use latest sphinx-doc
version and the RTD in a python3 `virtualenv <https://virtualenv.pypa.io>`__::

  $ virtualenv3 py3
  $ . py3/bin/activate
  $ pip install sphinx sphinx_rtd_theme

The following incompatibilities will be handled by this layer.  More details see
Sphinx-doc’s `CHANGELOG <http://www.sphinx-doc.org/en/master/changes.html>`__
and docutils `RELEASE-NOTES
<http://docutils.sourceforge.net/RELEASE-NOTES.html>`__

Bugfixes:

- Sphinx <= 1.4 (bug in docutils >= 0.13) : HTML Builders crashes with
  docutils-0.13 `[ref] <https://github.com/sphinx-doc/sphinx/pull/3217>`__

Downward compatibility:

- Sphinx >= 1.6: ``Sphinx.warn()``, ``Sphinx.info()`` and other logging methods are
  now deprecated.  Please use ``sphinx.util.logging`` instead.  It will be
  removed in Sphinx-2.0.

- Sphinx >= 1.7: ``sphinx.ext.autodoc.AutodocReporter`` is replaced by
  ``sphinx.util.docutils.  switch_source_input()`` and now deprecated.  It will
  be removed in Sphinx-2.0.

"""

import docutils
import sphinx

# Get Sphinx version
major, minor, patch = sphinx.version_info[:3]  # pylint: disable=invalid-name
docutils_major, docutils_minor, docutils_patch = docutils.__version_info__[:3]


if (major == 1 and minor <= 4) and (docutils_major == 0 and docutils_minor>=13):
    # to fix the docutils bug, we need a ugly hack, extending the code
    # object of sphinx's HTMLTranslator.depart_image method
    from sphinx.writers import html
    _origin_HTMLTranslator_depart_image = html.HTMLTranslator.depart_image
    def _wrap_HTMLTranslator_depart_image(__self, node):
        _origin_HTMLTranslator_depart_image(__self, node)
        if node['uri'].lower().endswith(('svg', 'svgz')):
            __self.context.pop()
    html.HTMLTranslator.depart_image = _wrap_HTMLTranslator_depart_image


if major >= 1 and minor >= 6:
    from sphinx.util import logging
    getLogger = logging.getLogger

else:
    # workaround for Sphinx < 1.6
    import logging
    from collections import defaultdict
    VERBOSE=15
    LEVEL_NAMES = defaultdict(lambda: logging.WARNING)
    LEVEL_NAMES.update({
        'CRITICAL': logging.CRITICAL,
        'SEVERE': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'VERBOSE': VERBOSE,
        'DEBUG': logging.DEBUG,
    })

    VERBOSITY_MAP = defaultdict(lambda: 0)  # type: Dict[int, int]
    VERBOSITY_MAP.update({
        0: logging.INFO,
        1: VERBOSE,
        2: logging.DEBUG,
    })
    class SphinxLoggerAdapter(logging.LoggerAdapter):
        """LoggerAdapter allowing ``type`` and ``subtype`` keywords."""

        def log(self, level, msg, *args, **kwargs):  # type: ignore
            # type: (Union[int, str], unicode, Any, Any) -> None
            if isinstance(level, int):
                super(SphinxLoggerAdapter, self).log(level, msg, *args, **kwargs)
            else:
                levelno = LEVEL_NAMES[level]
                super(SphinxLoggerAdapter, self).log(levelno, msg, *args, **kwargs)

        def verbose(self, msg, *args, **kwargs):
            # type: (unicode, Any, Any) -> None
            self.log(VERBOSE, msg, *args, **kwargs)

        def process(self, msg, kwargs):  # type: ignore
            # type: (unicode, Dict) -> Tuple[unicode, Dict]
            extra = kwargs.setdefault('extra', {})
            if 'type' in kwargs:
                extra['type'] = kwargs.pop('type')
            if 'subtype' in kwargs:
                extra['subtype'] = kwargs.pop('subtype')
            if 'location' in kwargs:
                extra['location'] = kwargs.pop('location')
            if 'nonl' in kwargs:
                extra['nonl'] = kwargs.pop('nonl')
            if 'color' in kwargs:
                extra['color'] = kwargs.pop('color')
            return msg, kwargs

        def handle(self, record):
            # type: (logging.LogRecord) -> None
            self.logger.handle(record) # type: ignore

    def getLogger(name):
        _logger = logging.getLogger('sphinx.' + name)
        _logger.disabled = False
        # wrap logger by SphinxLoggerAdapter
        return SphinxLoggerAdapter(_logger, {})

    logger = logging.getLogger('sphinx')
    logger.setLevel(logging.DEBUG)

if major >= 1 and minor >= 7:
    from sphinx.util.docutils import switch_source_input

else:
    # workaround for Sphinx < 1.7
    from docutils.statemachine import StateMachine
    from contextlib import contextmanager

    @contextmanager
    def switch_source_input(state, content):
        # type: (State, ViewList) -> Generator[None, None, None]
        """Switch current source input of state temporarily."""
        try:
            # remember the original ``get_source_and_line()`` method
            get_source_and_line = state.memo.reporter.get_source_and_line

            # replace it by new one
            state_machine = StateMachine([], None)
            state_machine.input_lines = content
            state.memo.reporter.get_source_and_line = state_machine.get_source_and_line

            yield
        finally:
            # restore the method
            state.memo.reporter.get_source_and_line = get_source_and_line
