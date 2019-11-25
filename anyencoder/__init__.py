"""
``anyencoder`` simplifies dynamic dispatch of various object
encoding schemes. See the README.
"""

# TODO
#  - improve / increase memoization (with explicit cache busting)
#  - file io / streaming interface
#  - multi-key-dict replacement
#  - benchmarking


from anyencoder.encoder import (
    DynamicEncoder,
    SimpleEncoder,
    decode,
    dumps,
    encode,
    loads,
    encode_with,
)

from anyencoder.plugins import (
    BaseEncoder,
    AbstractEncoder,
    ConcreteEncoder,
    proxy_attrs,
)
from anyencoder.registry import EncoderTag, TypeTag
from anyencoder.config import STR_VER, TITLE

__title__ = TITLE
__version__ = STR_VER

__all__ = [
    '__title__',
    '__version__',
    'AbstractEncoder',
    'BaseEncoder',
    'ConcreteEncoder',
    'DynamicEncoder',
    'EncoderTag',
    'SimpleEncoder',
    'TypeTag',
    'decode',
    'dumps',
    'encode',
    'encode_with',
    'loads',
    'proxy_attrs',
]
