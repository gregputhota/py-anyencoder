"""
Objects provided by this module:
    * :class:`LabelMaker`
    * :class:`BinaryLabelMaker`
    * :class:`JSONLabelMaker`
"""


import json
import struct

from abc import abstractmethod
from typing import AnyStr


from anyencoder.config import TEXT_LABEL_DELIM, TITLE, version
from anyencoder.label import _label_cls, Label
from anyencoder.util import memoize_method, simple_str


@simple_str
@_label_cls(Label)
class LabelMaker:
    """
    This is an abstract class factory which inspects the type of data
    being labeled and returns its concrete subclasses.

    Public Methods:
      * :func:`LabelMaker.apply`

    Usage:

    >>> encoded_data = b'something'
    >>> encoder_id = 128
    >>> maker = BinaryLabelMaker()  # A concrete example
    >>> label = maker.apply(encoder_id)
    >>> assert isinstance(label, Label)
    """

    __slots__ = ()

    def __new__(cls, data: AnyStr):
        """
        Create a new LabelMaker object and return it from the factory.

        :param data: The data being labeled.
        :return: A new LabelMaker object.
        """
        if issubclass(type(data), bytes):
            new = object.__new__(BinaryLabelMaker)

        elif issubclass(type(data), str):
            new = object.__new__(JSONLabelMaker)

        else:
            raise TypeError('No LabelMaker for data type')

        new.data = data
        new.version = version

        return new

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'data={self.data!r})')

    @abstractmethod
    def _build_label(self, encoder_id: int) -> AnyStr:
        """
        Build and return the data label.

        :param: encoder_id: The encoder ID.
        :return: The data label.
        """
        raise NotImplementedError

    @abstractmethod
    def _label_data(self, encoder_id: int) -> AnyStr:
        """
        Label the encoded data and return the result.

        :param encoder_id: The encoder ID.
        :return: The data stream with the label prepended.
        """
        raise NotImplementedError

    def apply(self, encoder_id: int) -> Label:
        """
        Return the label from the :class:`LabelMaker`.

        :param encoder_id: The encoder_id.
        :return: The Label object for this LabelMaker.
        """
        return self._label_cls(
            encoder_id=encoder_id,
            version_major=self.version.MAJOR,
            version_minor=self.version.MINOR,
            version_micro=self.version.MICRO,
            labeled_data=self._label_data(encoder_id),
            raw_data=self.data,
        )


class BinaryLabelMaker(LabelMaker):
    """
    This is a concrete instance of :class:`LabelMaker` intended for
    labeling binary data.
    """

    __slots__ = ('data', 'version')

    @memoize_method
    def _build_label(self, encoder_id: int) -> bytes:
        # The label is 5 bytes in length, as follows:
        # label_len|encoder_id|version_major|version_minor|version_micro
        # For this reason, we're limited to 2^8 unique encoder_ids.
        label_values = (
            encoder_id,
            self.version.MAJOR,
            self.version.MINOR,
            self.version.MICRO,
        )
        label_len = len([*label_values]) + 1
        s = struct.Struct('B' * label_len)

        try:
            label = s.pack(*(label_len, *label_values))
        except struct.error as e:
            raise ValueError('invalid label_values') from e

        return label

    def _label_data(self, encoder_id: int) -> bytes:
        label = self._build_label(encoder_id)

        # Prepend the label to the encoded data, with a delimiter.
        try:
            labeled_data = label + self.data
        except TypeError as e:
            raise TypeError('data labeling error') from e

        return labeled_data


class JSONLabelMaker(LabelMaker):
    """
    This is a concrete instance of :class:`LabelMaker` intended for
    labeling text data.
    """

    __slots__ = ('data', 'version')

    @memoize_method
    def _build_label(self, encoder_id: int) -> AnyStr:

        label_values = {
            TITLE: {
                'encoder_id': encoder_id,
                'version':    {
                    'major': self.version.MAJOR,
                    'minor': self.version.MINOR,
                    'micro': self.version.MICRO,
                },
            },
        }
        try:
            label = json.dumps(label_values)
        except TypeError as e:
            raise TypeError('invalid label_values') from e

        return label

    def _label_data(self, encoder_id: int) -> str:
        label = self._build_label(encoder_id)

        # Prepend the label to the encoded data, with a delimiter.
        try:
            labeled_data = f'{label}{TEXT_LABEL_DELIM}{self.data}'
        except TypeError as e:
            raise TypeError('data labeling error') from e

        return labeled_data
