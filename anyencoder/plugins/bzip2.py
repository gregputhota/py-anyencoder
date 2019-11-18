"""
* :class:`Bzip2Encoder`
"""


import bz2

from anyencoder.plugins.base import (
    AbstractEncoder,
    ConcreteEncoder,
    encodings,
)
from anyencoder.registry import EncoderTag


encode_kwargs = dict()
decode_kwargs = dict()
concrete = ConcreteEncoder(
    encode=bz2.compress,
    decode=bz2.decompress,
    encode_kwargs=encode_kwargs,
    decode_kwargs=decode_kwargs,
)


# noinspection PyAbstractClass
class Bzip2Encoder(AbstractEncoder, concrete_encoder=concrete):

    encoder_id = encodings.BZIP2


tag = EncoderTag(
    name='bzip2',
    encoder=Bzip2Encoder(),
)
