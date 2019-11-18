"""
This package contains the pre-built encoder definitions. Some
of these modules require supporting third-party packages to be
installed in order to load.
"""


from anyencoder.config import STR_VER
from anyencoder.plugins.base import (
    BaseEncoder,
    ConcreteEncoder,
    AbstractEncoder,
    proxy_attrs,
)


__version__ = STR_VER

__all__ = [
    'BaseEncoder',
    'ConcreteEncoder',
    'AbstractEncoder',
    'proxy_attrs',
]
