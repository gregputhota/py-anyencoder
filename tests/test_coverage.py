"""
Some day, this package will have high-quality unit tests with full
coverage.

But today is not that day.
"""


import unittest


from anyencoder.plugins.base import AbstractEncoder, proxy_attrs
from anyencoder.plugins.json import JSONEncoder
from anyencoder.plugins.pickle import PickleEncoder
from anyencoder.encoder import DynamicEncoder, encode, decode
from anyencoder.registry import EncoderTag, TypeTag
from anyencoder import encode_with


class Equality:
    value = None

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.value == other.value)


class MyClass1(Equality):
    value = 'foo'

    @staticmethod
    def _encoder_id():
        return 'dill'


class MyClass2(Equality):
    value = b'greetings'
    _encoder_id = 'pickle'


@encode_with('cloudpickle')
class MyClass3(Equality):
    value = 10


class TestEncodeDecode(unittest.TestCase):

    @proxy_attrs
    class CustomEncoder(AbstractEncoder):
        encoder_id = 10

        def encode(self, value):
            return value

        def decode(self, value):
            return value

    def encode_decode(self, data, encoder_id=None):
        encoded = encode(data, encoder=encoder_id)
        decoded = decode(encoded, encoder=encoder_id)
        self.assertEqual(decoded, data)


class TestEncoderPlugins(TestEncodeDecode):

    data = {'foo': 'bar'}

    def test_default_encoder(self):
        self.encode_decode(self.data)

    def test_encoder_plugin_bson(self):
        encoder_id = 'bson'
        self.encode_decode(self.data, encoder_id)

    def test_encoder_plugin_bzip2(self):
        encoder_id = 'bzip2'
        self.encode_decode(b'something', encoder_id)

    def test_encoder_plugin_gzip(self):
        encoder_id = 'gzip'
        self.encode_decode(b'something', encoder_id)

    def test_encoder_plugin_zlib(self):
        encoder_id = 'zlib'
        self.encode_decode(b'something', encoder_id)

    def test_encoder_plugin_cloudpickle(self):
        encoder_id = 'cloudpickle'
        self.encode_decode(self.data, encoder_id)

    def test_encoder_plugin_dill(self):
        encoder_id = 'dill'
        self.encode_decode(self.data, encoder_id)

    def test_encoder_plugin_json(self):
        encoder_id = 'json'
        self.encode_decode(self.data, encoder_id)

    def test_encoder_plugin_orjson(self):
        encoder_id = 'orjson'
        self.encode_decode(self.data, encoder_id)

    def test_encoder_plugin_ujson(self):
        encoder_id = 'ujson'
        self.encode_decode(self.data, encoder_id)

    def test_encoder_plugin_msgpack(self):
        encoder_id = 'msgpack'
        self.encode_decode(self.data, encoder_id)

    def test_encoder_plugin_pickle(self):
        encoder_id = 'pickle'
        self.encode_decode(self.data, encoder_id)

    def test_encoder_plugin_strbyte(self):
        encoder_id = 'strbyte'
        data = 'foo'
        encoded = encode(data, encoder_id)
        decoded = decode(encoded, encoder_id)
        self.assertEqual(decoded, data)


class TestTypeHints(TestEncodeDecode):

    def test_callable_hint(self):
        obj = MyClass1()
        self.encode_decode(obj)

    def test_attribute_hint(self):
        obj = MyClass2()
        self.encode_decode(obj)

    def test_decorator_hint(self):
        obj = MyClass3()
        self.encode_decode(obj)


class TestProxy(TestEncodeDecode):

    def test_proxy_encoder(self):
        json_encoder = JSONEncoder()
        encoder = self.CustomEncoder(proxy_to=json_encoder)
        enc_tag1 = EncoderTag(
            name='custom-encoder',
            encoder=encoder,
        )
        enc_tag2 = EncoderTag(
            name='json',
            encoder=json_encoder,
        )

        type_tag1 = TypeTag(
            type_=list,
            evaluator=lambda _: 'custom-encoder',

        )
        encoder = DynamicEncoder()
        encoder.register([enc_tag1, enc_tag2])
        encoder.register(type_tag1)
        data = [1, 2, 3]

        encoded = encoder.encode(data)
        decoded = encoder.decode(encoded)
        self.assertEqual(decoded, data)


class TestEncapsulation(TestEncodeDecode):

    def test_invalid_maker_data(self):
        data = [1, 2, 3]
        custom = self.CustomEncoder()
        enc_tag1 = EncoderTag(
            name='custom-encoder',
            encoder=custom,
        )
        type_tag1 = TypeTag(
            type_=list,
            evaluator=lambda _: 'custom-encoder',

        )
        encoder = DynamicEncoder()
        encoder.register([enc_tag1, type_tag1])
        with self.assertRaises(TypeError):
            encoder.encode(data)

    def test_invalid_reader_data(self):

        data = [1, 2, 3]
        type_tag = TypeTag(
            type_=list,
            evaluator=lambda _: 'msgpack',

        )
        with DynamicEncoder() as encoder:
            encoder.register(type_tag)
            encoded = encoder.encode(data)
            with self.assertRaises(ValueError):
                encoder.decode(encoded, encoder='json')


class TestRegistry(unittest.TestCase):

    def test_tags(self):
        type_tag1 = TypeTag(
            type_=dict,
            evaluator=lambda _: 'json',

        )
        type_tag2 = TypeTag(
            type_=dict,
            evaluator=lambda _: 'json',

        )
        type_tag3 = TypeTag(
            type_=int,
            evaluator=lambda _: 'msgpack',

        )
        enc_tag1 = EncoderTag(
            name='json',
            encoder=JSONEncoder(),
        )
        enc_tag2 = EncoderTag(
            name='json',
            encoder=JSONEncoder(),
        )
        enc_tag3 = EncoderTag(
            name='pickle',
            encoder=PickleEncoder(),
        )

        self.assertEqual(type_tag1, type_tag2)
        self.assertNotEqual(type_tag2, type_tag3)
        self.assertEqual(enc_tag1, enc_tag2)
        self.assertNotEqual(enc_tag2, enc_tag3)

    def test_registry_methods(self):
        type_tag1 = TypeTag(
            type_=list,
            evaluator=lambda _: 'msgpack',

        )
        encoder = DynamicEncoder()
        with self.assertRaises(ValueError):
            encoder.registry.remove(type_tag1)

        encoder.register(type_tag1)

        self.assertEqual(encoder.registry.get(list), type_tag1)
        self.assertTrue(encoder.registry.contains(type_tag1))

        with self.assertRaises(ValueError):
            encoder.register(type_tag1)

        encoder.registry.remove(type_tag1)
        self.assertEqual(encoder.registry.get(list), None)
        encoder.registry.dump()
        encoder.registry.clear()


class TestMisc(unittest.TestCase):
    pass
