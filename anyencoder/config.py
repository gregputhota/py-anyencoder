""" Configuration constants and miscellany. """

import os
from dataclasses import dataclass


PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
DEFAULT_ENCODER = os.getenv('PY_ANYENCODER_DEFAULT_ENCODER', 'pickle')
HINT_ATTR = '_encoder_id'
TEXT_LABEL_DELIM = '|'
TITLE = 'anyencoder'
ENCODER_ID_MAX_SIZE = 255
DEFAULT_PLUGIN_PATH = [f'{PACKAGE_ROOT}/plugins']
DEFAULT_PLUGIN_PREFIX = f'{TITLE}.plugins.'


@dataclass
class SemanticVersion:
    """
    This dataclass provides an semantic version representation.
    """

    MAJOR: int = 0
    MINOR: int = 0
    MICRO: int = 3


version = SemanticVersion()
STR_VER = f'{version.MAJOR}.{version.MINOR}.{version.MICRO}'
