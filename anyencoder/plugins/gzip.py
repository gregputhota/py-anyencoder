"""
* :class:`GzipEncoder`
"""


import gzip

from anyencoder.plugins.base import (
    AbstractEncoder,
    ConcreteEncoder,
    encodings,
)
from anyencoder.registry import EncoderTag


encode_kwargs = dict()
decode_kwargs = dict()
concrete = ConcreteEncoder(
    encode=gzip.compress,
    decode=gzip.decompress,
    encode_kwargs=encode_kwargs,
    decode_kwargs=decode_kwargs,
)


# noinspection PyAbstractClass
class GzipEncoder(AbstractEncoder, concrete_encoder=concrete):

    encoder_id = encodings.GZIP


tag = EncoderTag(
    name='gzip',
    encoder=GzipEncoder(),
)
