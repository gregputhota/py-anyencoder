"""
* :class:`StrByteEncoder`
"""


from anyencoder.plugins.base import encodings
from anyencoder.plugins import AbstractEncoder
from anyencoder.registry import EncoderTag


class StrByteEncoder(AbstractEncoder):

    encoder_id = encodings.STRBYTE
    encode_kwargs = dict(encoding='utf-8')
    decode_kwargs = dict(encoding='utf-8')

    def encode(self, value: str) -> bytes:
        return value.encode(**self.encode_kwargs)

    def decode(self, value: bytes) -> str:
        return value.decode(**self.decode_kwargs)


tag = EncoderTag(
    name='strbyte',
    encoder=StrByteEncoder(),
)
