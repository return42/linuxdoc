# -*- coding: utf-8; mode: python -*-
# pylint: disable=invalid-name, missing-docstring
u"""compat
    ~~~~~~

    Implementation of a compatibility layer for sphinx related modules.

    :copyright:  Copyright (C) 2018 Markus Heiser
    :license:    GPL Version 2, June 1991 see Linux/COPYING for details.

    Downward compatibility is unfortunately no strength of sphinx-doc and patch
    levels not really exists or if so they are not shipped within LTS
    distributions.  Therefor a minimal compatibility *layer* is needed.

"""

import sphinx

# Get Sphinx version
major, minor, patch = sphinx.version_info[:3]  # pylint: disable=invalid-name

if major == 1 and minor > 5:
    # new logging format started with sphinx 1.6
    from sphinx.util import logging
    getLogger = logging.getLogger

else:
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
