from anyencoder import (
    AbstractEncoder,
    DynamicEncoder,
    TypeTag,
    EncoderTag,
    encode_with,
)
from anyencoder.plugins.strbyte import StrByteEncoder
from anyencoder.plugins.ujson import UJsonEncoder
from anyencoder.plugins.zlib import ZlibEncoder


def usage1():
    # Encode something
    letters = ['a', 'b', 'c']

    with DynamicEncoder() as encoder:
        encoded = encoder.encode(letters)
        decoded = encoder.decode(encoded)
        assert decoded == letters


def usage2():
    # Register a type
    type_tag = TypeTag(
        type_=list,
        evaluator=lambda _: 'msgpack',
    )
    letters = ['a', 'b', 'c']

    with DynamicEncoder() as encoder:
        encoder.register(type_tag)
        encoded = encoder.encode(letters)
        decoded = encoder.decode(encoded)
        assert decoded == letters


def usage3():
    # Type evaluators

    def i_care_about_keys(obj):
        if all(map(lambda x: isinstance(x, str), obj.keys())):
            return 'msgpack'
        else:
            return 'bson'

    dict_tag = TypeTag(
        type_=dict,
        evaluator=i_care_about_keys,
    )

    list_tag = TypeTag(
        type_=list,
        evaluator=lambda x: 'msgpack' if len(x) > 1000 else 'json',
    )

    small_list = [1, 2, 3]
    big_list = [*range(0, 5000)]

    str_dict = dict(a=1, b=2, c=3)
    int_dict = {1: 'a', 2: 'b', 3: 'c'}

    with DynamicEncoder() as encoder:
        encoder.register(list_tag)
        encoder.register(dict_tag)
        print(encoder.encode(small_list))
        print(encoder.encode(big_list))
        print(encoder.encode(str_dict))
        print(encoder.encode(int_dict))


def usage4():
    # object._encoder_id

    class MyClass:

        z = False

        def _encoder_id(self):
            # This doesn't need to be a method; an attribute will work.
            if self.z:
                return 'cloudpickle'
            else:
                return 'dill'

    my_cls = MyClass()
    with DynamicEncoder() as encoder:
        print(encoder.encode(my_cls))
        my_cls.z = True
        print(encoder.encode(my_cls))


def usage5():
    # Decorator

    @encode_with('dill')
    class MyClass:
        pass

    my_cls = MyClass()
    with DynamicEncoder() as encoder:
        encoded = encoder.encode(my_cls)
        print(encoded)


def usage6():
    # Registering custom types

    def evaluate_class(obj):
        return 'cloudpickle' if obj.z else 'dill'

    class MyClass:

        def __init__(self):
            self.z = False

    type_tag = TypeTag(
        type_=MyClass,
        evaluator=evaluate_class,
    )

    my_cls = MyClass()

    with DynamicEncoder() as encoder:
        encoder.register(type_tag)
        print(encoder.encode(my_cls))
        my_cls.z = True
        print(encoder.encode(my_cls))


def usage7():

    # Custom Encoder example
    class StrToUtf16(AbstractEncoder):

        encoder_id = 0  # Each encoder has a unique integer ID

        def encode(self, obj):
            return obj.encode('utf-16')

        def decode(self, data):
            return data.decode('utf-16')

    my_encoder = StrToUtf16()
    encoder_tag = EncoderTag(
        name='string-to-utf16',
        encoder=my_encoder,
    )
    type_tag = TypeTag(
        type_=str,
        evaluator=lambda _: 'string-to-utf16',
    )

    encoder = DynamicEncoder()
    encoder.register(encoder_tag)
    encoder.register(type_tag)
    to_16 = encoder.encode('hello world')
    print(to_16)


def usage8():
    # Proxy JSON/text through byte encoding and then through bzip2
    zlib = ZlibEncoder()
    strbyte = StrByteEncoder(proxy_to=zlib)
    json_zlib = UJsonEncoder(encoder_id=1, proxy_to=strbyte)

    encoder_tag = EncoderTag(
        name='json-zlib',
        encoder=json_zlib,
    )
    type_tag = TypeTag(
        type_=dict,
        evaluator=lambda _: 'json-zlib',
    )

    data = dict(a=1, b=2, c=3)

    with DynamicEncoder() as encoder:
        # Pro-tip: You can register an iterable of tags
        encoder.register([encoder_tag, type_tag])
        encoder.encode(data)


if __name__ == '__main__':
    usage1()
    usage2()
    usage3()
    usage4()
    usage5()
    usage6()
    usage7()
    usage8()
