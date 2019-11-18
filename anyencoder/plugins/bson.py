"""
* :class:`BSONEncoder`

``pip install bson`` to enable this plugin.
"""


# noinspection PyPackageRequirements
import bson

from anyencoder.plugins.base import (
    AbstractEncoder,
    ConcreteEncoder,
    encodings,
)
from anyencoder.registry import EncoderTag


encode_kwargs = dict()
decode_kwargs = dict()
concrete = ConcreteEncoder(
    encode=bson.dumps,
    decode=bson.loads,
    encode_kwargs=encode_kwargs,
    decode_kwargs=decode_kwargs,
)


# noinspection PyAbstractClass
class BSONEncoder(AbstractEncoder, concrete_encoder=concrete):

    encoder_id = encodings.BSON


tag = EncoderTag(
    name='bson',
    encoder=BSONEncoder(),
)
