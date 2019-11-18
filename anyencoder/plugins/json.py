"""
* :class:`JSONEncoder`
"""


import json

from anyencoder.plugins.base import (
    AbstractEncoder,
    ConcreteEncoder,
    encodings,
)
from anyencoder.registry import EncoderTag


encode_kwargs = dict()
decode_kwargs = dict()
concrete = ConcreteEncoder(
    encode=json.dumps,
    decode=json.loads,
    encode_kwargs=encode_kwargs,
    decode_kwargs=decode_kwargs,
)


# noinspection PyAbstractClass
class JSONEncoder(AbstractEncoder, concrete_encoder=concrete):

    encoder_id = encodings.JSON


tag = EncoderTag(
    name='json',
    encoder=JSONEncoder(),
)
