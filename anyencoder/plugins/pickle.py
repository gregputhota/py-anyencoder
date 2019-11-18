"""
* :class:`PickleEncoder`
"""


import pickle

from anyencoder.plugins.base import (
    AbstractEncoder,
    ConcreteEncoder,
    encodings,
)
from anyencoder.registry import EncoderTag


encode_kwargs = dict(protocol=pickle.HIGHEST_PROTOCOL)
decode_kwargs = dict()
concrete = ConcreteEncoder(
    encode=pickle.dumps,
    decode=pickle.loads,
    encode_kwargs=encode_kwargs,
    decode_kwargs=decode_kwargs,
)


# noinspection PyAbstractClass
class PickleEncoder(AbstractEncoder, concrete_encoder=concrete):

    encoder_id = encodings.PICKLE


tag = EncoderTag(
    name='pickle',
    encoder=PickleEncoder(),
)
