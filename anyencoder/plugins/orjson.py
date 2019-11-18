"""
* :class:`OrJsonEncoder`

``pip install orjson`` to enable this plugin.
"""


# noinspection PyPackageRequirements
import orjson

from anyencoder.plugins.base import (
    AbstractEncoder,
    ConcreteEncoder,
    encodings,
)
from anyencoder.registry import EncoderTag


encode_kwargs = dict()
decode_kwargs = dict()
concrete = ConcreteEncoder(
    encode=orjson.dumps,
    decode=orjson.loads,
    encode_kwargs=encode_kwargs,
    decode_kwargs=decode_kwargs,
)


# noinspection PyAbstractClass
class OrJsonEncoder(AbstractEncoder, concrete_encoder=concrete):

    encoder_id = encodings.ORJSON


tag = EncoderTag(
    name='orjson',
    encoder=OrJsonEncoder(),
)
