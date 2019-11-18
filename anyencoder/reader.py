"""
Objects provided by this module:
    * :class:`LabelReader`
    * :class:`BinaryLabelReader`
    * :class:`JSONLabelReader`
"""


import json
import struct

from abc import ABC, abstractmethod
from typing import AnyStr


from anyencoder.config import TEXT_LABEL_DELIM, TITLE
from anyencoder.label import Label, _label_cls
from anyencoder.util import simple_str


@simple_str
class LabelReader(ABC):
    """
    This is an abstract class factory which inspects the labeled data
    and returns its concrete subclasses.

    Public Methods:
      * :func:`LabelReader.scan`

    Usage:

    >>> data = b'something'
    >>> reader_factory = lambda _: LabelReader
    >>> reader = reader_factory(data)
    >>> label = reader.scan()
    >>> assert isinstance(label, Label)
    """

    __slots__ = ()

    def __new__(cls, data: AnyStr):
        """
        Create a new LabelReader object and return it from the factory.

        :param data: The labeled data stream.
        :return: A new LabelReader object.
        """
        if issubclass(type(data), bytes):
            new = object.__new__(BinaryLabelReader)

        elif issubclass(type(data), str):
            new = object.__new__(JSONLabelReader)

        else:
            raise TypeError('No LabelReader for data type')

        new.data = data

        return new

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'data={self.data!r})')

    @abstractmethod
    def scan(self) -> Label:
        """
        Scan the encoded data and return a :class:`Label` object.

        :return: A Label object for the encoded data.
        """
        raise NotImplementedError


@_label_cls(Label)
class BinaryLabelReader(LabelReader):
    """
    This is a concrete instance of :class:`LabelMaker` intended for
    reading binary data labels.
    """

    __slots__ = ('_label_cls', 'data')

    def scan(self) -> Label:
        # The label is 5 bytes in length, as follows:
        # label_len|encoder_id|version_major|version_minor|version_micro
        labeled_data = self.data

        header_size = labeled_data[0]
        assert isinstance(header_size, int)
        assert len(labeled_data) >= header_size

        header = labeled_data[:header_size]
        assert header

        raw_data = labeled_data[header_size:]
        assert raw_data

        s = struct.Struct('B' * header_size)
        try:
            _, encoder_id, major, minor, micro = s.unpack(header)
        except struct.error:
            raise ValueError('Invalid Label')

        return self._label_cls(
            encoder_id=encoder_id,
            raw_data=raw_data,
            labeled_data=labeled_data,
            version_major=major,
            version_minor=minor,
            version_micro=micro,
        )


@_label_cls(Label)
class JSONLabelReader(LabelReader):
    """
    This is a concrete instance of :class:`LabelMaker` intended for
    reading text data labels.
    """

    __slots__ = ('_label_cls', 'data')

    def scan(self) -> Label:
        labeled_data = self.data

        try:
            label, raw_data = labeled_data.split(TEXT_LABEL_DELIM, 2)
            decoded_label = json.loads(label)
        except ValueError:
            raise ValueError('Invalid Label')

        # label format:
        #
        #    __title__: {
        #        'version':    {
        #            'major': version.MAJOR,
        #            'minor': version.MINOR,
        #            'micro': version.MICRO,
        #        },
        #        'encoder_id': self.encoder_id,
        #    },

        assert TITLE in decoded_label
        label_root = decoded_label[TITLE]

        assert 'encoder_id' in label_root
        encoder_id = label_root['encoder_id']

        assert 'version' in label_root
        version = label_root['version']

        assert 'major' in version
        major = version['major']

        assert 'minor' in version
        minor = version['minor']

        assert 'micro' in version
        micro = version['micro']

        return self._label_cls(
            encoder_id=encoder_id,
            raw_data=raw_data,
            labeled_data=labeled_data,
            version_major=major,
            version_minor=minor,
            version_micro=micro,
        )
