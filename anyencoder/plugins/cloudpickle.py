"""
* :class:`CloudPickleEncoder`

``pip install cloudpickle`` to enable this plugin.
"""


# noinspection PyPackageRequirements
import cloudpickle

from anyencoder.plugins.base import (
    AbstractEncoder,
    ConcreteEncoder,
    encodings,
)
from anyencoder.registry import EncoderTag


encode_kwargs = dict()
decode_kwargs = dict()
concrete = ConcreteEncoder(
    encode=cloudpickle.dumps,
    decode=cloudpickle.loads,
    encode_kwargs=encode_kwargs,
    decode_kwargs=decode_kwargs,
)


# noinspection PyAbstractClass
class CloudPickleEncoder(AbstractEncoder, concrete_encoder=concrete):

    encoder_id = encodings.CLOUDPICKLE


tag = EncoderTag(
    name='cloudpickle',
    encoder=CloudPickleEncoder(),
)
