"""
Objects provided by this module:
    * :class:`Label`
    * :func:`_label_cls`
"""


from dataclasses import dataclass
from functools import wraps

from typing import Any, AnyStr

from anyencoder.util import simple_str


@simple_str
@dataclass
class Label:
    """
    This is a dataclass which contains encapsulated data and
    related meta-data. This Label is passed around within this
    package when describing an object and its associated encoding
    scheme.
    """

    __slots__ = (
        'encoder_id',
        'labeled_data',
        'raw_data',
        'version_major',
        'version_micro',
        'version_minor',
    )

    encoder_id: int
    version_major: int
    version_minor: int
    version_micro: int
    labeled_data: AnyStr
    raw_data: Any

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'encoder_id={self.encoder_id!r},'
                f'version_major={self.version_major!r},'
                f'version_minor={self.version_minor!r},'
                f'version_micro={self.version_micro!r},'
                f'labeled_data={self.labeled_data!r},'
                f'raw_data={self.raw_data!r})')


def _label_cls(label_cls: any):
    """
    This is a simple class decorator which adds a method wrapper
    named in order to wrap calls to an underlying callable. This
    is a Mix-In object.
    """
    def decorator(cls: any):

        @wraps(cls)
        def wrapper(label_cls):

            def _label_cls(**kwargs) -> cls:
                return label_cls(**kwargs)

            _label_cls = staticmethod(_label_cls)
            cls._label_cls = _label_cls
            return cls

        return wrapper(label_cls)

    return decorator
