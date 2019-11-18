"""
* :class:`MessagePackEncoder`

``pip install msgpack`` to enable this plugin.
"""


# noinspection PyPackageRequirements
import msgpack

from anyencoder.plugins.base import (
    AbstractEncoder,
    ConcreteEncoder,
    encodings,
)
from anyencoder.registry import EncoderTag


encode_kwargs = dict(use_bin_type=True)
decode_kwargs = dict(raw=False)
concrete = ConcreteEncoder(
    encode=msgpack.packb,
    decode=msgpack.unpackb,
    encode_kwargs=encode_kwargs,
    decode_kwargs=decode_kwargs,
)


# noinspection PyAbstractClass
class MessagePackEncoder(AbstractEncoder, concrete_encoder=concrete):

    encoder_id = encodings.MSGPACK


tag = EncoderTag(
    name='msgpack',
    encoder=MessagePackEncoder(),
)
