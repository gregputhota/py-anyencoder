"""
* :class:`DillEncoder`

``pip install dill`` to enable this plugin.
"""


# noinspection PyPackageRequirements
import dill

from anyencoder.plugins.base import (
    AbstractEncoder,
    ConcreteEncoder,
    encodings,
)
from anyencoder.registry import EncoderTag


encode_kwargs = dict(protocol=dill.HIGHEST_PROTOCOL)
decode_kwargs = dict()
concrete = ConcreteEncoder(
    encode=dill.dumps,
    decode=dill.loads,
    encode_kwargs=encode_kwargs,
    decode_kwargs=decode_kwargs,
)


# noinspection PyAbstractClass
class DillEncoder(AbstractEncoder, concrete_encoder=concrete):

    encoder_id = encodings.DILL


tag = EncoderTag(
    name='dill',
    encoder=DillEncoder(),
)
