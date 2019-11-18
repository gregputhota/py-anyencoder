"""
* :class:`ZlibEncoder`
"""


import zlib

from anyencoder.plugins.base import (
    AbstractEncoder,
    ConcreteEncoder,
    encodings,
)
from anyencoder.registry import EncoderTag


encode_kwargs = dict()
decode_kwargs = dict()
concrete = ConcreteEncoder(
    encode=zlib.compress,
    decode=zlib.decompress,
    encode_kwargs=encode_kwargs,
    decode_kwargs=decode_kwargs,
)


# noinspection PyAbstractClass
class ZlibEncoder(AbstractEncoder, concrete_encoder=concrete):

    encoder_id = encodings.ZLIB


tag = EncoderTag(
    name='zlib',
    encoder=ZlibEncoder(),
)
