"""
* :class:`UJsonEncoder`

``pip install ujson`` to enable this plugin.
"""


# noinspection PyPackageRequirements
import ujson

from anyencoder.plugins.base import AbstractEncoder, ConcreteEncoder, encodings
from anyencoder.registry import EncoderTag


encode_kwargs = dict()
decode_kwargs = dict()
concrete = ConcreteEncoder(
    encode=ujson.dumps,
    decode=ujson.loads,
    encode_kwargs=encode_kwargs,
    decode_kwargs=decode_kwargs,
)


# noinspection PyAbstractClass
class UJsonEncoder(AbstractEncoder, concrete_encoder=concrete):

    encoder_id = encodings.UJSON


tag = EncoderTag(
    name='ujson',
    encoder=UJsonEncoder(),
)
