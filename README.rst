==============
``anyencoder``
==============
Here's a little library that makes it easy to juggle multiple object
serializers and dynamically select the serialization scheme to
employ.

.. image:: https://api.travis-ci.org/andrewschenck/py-anyencoder.svg?branch=master
   :target: https://www.github.com/andrewschenck/py-anyencoder


--------
Overview
--------

Features
--------
* Developed on Python 3.7 (and requires 3.7+, sorry not sorry)
* Tested-ish
* You can create and as many custom encoders as you want (as long as
  the number you want is 128 or less.)
* Types are associated with encoders via a registry or direct object
  inspection.

Getting Started
---------------
Encode a list:

.. code-block:: python

    >>> import anyencoder
    >>> letters = ['a', 'b', 'c']
    >>> anyencoder.encode(letters)
    b'\x05\x80\x00\x00\x01\x80\x04\x95\x11\x00\x00\x00\x00\x00\x00\x00]\x94(\x8c\x01a\x94\x8c\x01b\x94\x8c\x01c\x94e.'

Absent other parameters or method calls, the default encoder is used
-- probably ``pickle``. I realize this isn't terribly useful. Let's dig
deeper.


-----
Types
-----

Builtin Types
-------------
Instantiate ``AnyEncoder`` and register a ``TypeTag`` specifying that
list should be serialized using ``msgpack``:

.. code-block:: python

    >>> from anyencoder import AnyEncoder, TypeTag
    >>> type_tag = TypeTag(type_=list, evaluator=lambda _: 'msgpack')
    >>> letters = ['a', 'b', 'c']
    >>> encoder = AnyEncoder()
    >>> encoder.load_encoder_plugins()
    >>> encoder.register(type_tag)
    >>> encoder.encode(letters)
    b'\x05\x83\x00\x00\x01\x93\xa1a\xa1b\xa1c'


Types are associated with an evaluator. The evaluator is called
against the object being serialized. This can be used to inspect
the object and choose the encoding scheme dynamically:

.. code-block:: python

    >>> from anyencoder import AnyEncoder, TypeTag
    >>> def i_care_about_keys(obj):
    ...     """
    ...     If all the keys in the dictionary are strings, I want
    ...     to store the dictionary as msgpack. Otherwise, I want to
    ...     store it as bson. For some reason.
    ...     """
    ...     if all(map(lambda x: isinstance(x, str), obj.keys())):
    ...         return 'msgpack'
    ...     else:
    ...         return 'bson'
    ...
    >>> dict_tag = TypeTag(dict, i_care_about_keys)
    >>> str_dict = dict(a=1, b=2, c=3)
    >>> int_dict = {1: 'a', 2: 'b', 3: 'c'}
    >>> encoder = AnyEncoder()
    >>> encoder.load_encoder_plugins()
    >>> encoder.register(dict_tag)
    >>> encoder.encode(str_dict)
    b'\x05\x83\x00\x00\x01\x83\xa1a\x01\xa1b\x02\xa1c\x03'
    >>> encoder.encode(int_dict)
    b'\x05\x88\x00\x00\x01 \x00\x00\x00\x021\x00\x02\x00\x00\x00a\x00\x022\x00\x02\x00\x00\x00b\x00\x023\x00\x02\x00\x00\x00c\x00\x00'


Custom Types
------------
Classes can implement a method to specify how they should be
serialized. The method should return the name of the desired encoder:

.. code-block:: python

    >>> from anyencoder import AnyEncoder
    >>> class MyClass:
    ...     z = False
    ...
    ...     def _encoder_id(self):
    ...         if self.z:
    ...             return 'cloudpickle'
    ...         else:
    ...             return 'dill'
    >>> my_cls = MyClass()
    ... with AnyEncoder() as encoder:
    ...     with_z_false = encoder.encode(my_cls)
    ...     my_cls.z = True
    ...     with_z_true = encoder.encode(my_cls)
    ...
    >>> with_z_false
    b'\x05\x81\x00\x00\x01\x80\x04\x95\xa8\x00\x00\x00\x00\x00\x00\x00\x8c\ndill._dill\x94\x8c\x0c_create_type\x94\x93\x94(h\x00\x8c\n_load_type\x94\x93\x94\x8c\tClassType\x94\x85\x94R\x94\x8c\x07MyClass\x94h\x04\x8c\x06object\x94\x85\x94R\x94\x85\x94}\x94(\x8c\n__module__\x94\x8c\x08__main__\x94\x8c\x01z\x94\x89\x8c\x07__doc__\x94N\x8c\r__slotnames__\x94]\x94ut\x94R\x94)\x81\x94}\x94h\x10\x89sb.'
    >>> with_z_true
    b'\x05\x82\x00\x00\x01\x80\x04\x95\xb8\x00\x00\x00\x00\x00\x00\x00\x8c\x17cloudpickle.cloudpickle\x94\x8c\x19_rehydrate_skeleton_class\x94\x93\x94(\x8c\x08builtins\x94\x8c\x04type\x94\x93\x94\x8c\x07MyClass\x94h\x03\x8c\x06object\x94\x93\x94\x85\x94}\x94\x8c\x07__doc__\x94Ns\x87\x94R\x94}\x94(\x8c\n__module__\x94\x8c\x08__main__\x94\x8c\x01z\x94\x89\x8c\r__slotnames__\x94]\x94utR)\x81\x94}\x94h\x11\x88sb.'

This doesn't have to be a method; an attribute named ``encoder_id`` will
also work.


If that sounds like too much work for you, try the ``encode_with``
decorator:

.. code-block:: python

    >>> from anyencoder import AnyEncoder, encode_with
    >>> @encode_with('dill')
    ... class MyClass:
    ...     pass
    ...
    ... my_cls = MyClass()
    ... with AnyEncoder() as encoder:
    ...     encoded = encoder.encode(my_cls)
    ...
    >>> encoded
    b'\x05\x81\x00\x00\x01\x80\x04\x95\xb1\x00\x00\x00\x00\x00\x00\x00\x8c\ndill._dill\x94\x8c\x0c_create_type\x94\x93\x94(h\x00\x8c\n_load_type\x94\x93\x94\x8c\tClassType\x94\x85\x94R\x94\x8c\x07MyClass\x94h\x04\x8c\x06object\x94\x85\x94R\x94\x85\x94}\x94(\x8c\n__module__\x94\x8c\x08__main__\x94\x8c\x07__doc__\x94N\x8c\x0b_encoder_id\x94\x8c\x04dill\x94\x8c\r__slotnames__\x94]\x94ut\x94R\x94)\x81\x94.'



Rather than implementing methods, classes can be registered like any
other type:

.. code-block:: python

    >>> from anyencoder import AnyEncoder, TypeTag
    >>> def evaluate_class(obj):
    ...     return 'cloudpickle' if obj.z else 'dill'
    ...
    >>> class MyClass:
    ...     z = False
    ...
    >>> type_tag = TypeTag(MyClass, evaluate_class)
    >>> my_cls = MyClass()
    >>> encoder = AnyEncoder()
    >>> encoder.load_encoder_plugins()
    >>> encoder.register(type_tag)
    >>> encoder.encode(my_cls)
    b'\x05\x81\x00\x00\x01\x80\x04\x95\xa8\x00\x00\x00\x00\x00\x00\x00\x8c\ndill._dill < SNIP >
    >>> my_cls.z = True
    >>> encoder.encode(my_cls)
    b'\x05\x82\x00\x00\x01\x80\x04\x95\xb8\x00\x00\x00\x00\x00\x00\x00\x8c\x17cloudpickle.cloudpickle < SNIP >


--------
Encoders
--------


Builtin Encoders
----------------

Several pre-built encoders are included:

* bson
* bzip2
* cloudpickle
* dill
* gzip
* json
* msgpack
* orjson
* pickle
* strbyte
* ujson
* zlib

Custom Encoders
---------------
Custom encoders can be defined and registered for use. To create
a custom encoder, subclass ``AbstractEncoder``:

.. code-block:: python


    >>> from anyencoder import AnyEncoder, TypeTag, AbstractEncoder, EncoderTag
    >>> class StrToUtf16(AbstractEncoder):
    ...     encoder_id = 10
    ...
    ...     def encode(self, obj):
    ...         return obj.encode('utf-16')
    ...
    ...     def decode(self, data):
    ...         return data.decode('utf-16')
    ...
    >>> my_encoder = StrToUtf16()
    >>> encoder_tag = EncoderTag('str-to-utf-16', my_encoder)
    >>> encoder.register(encoder_tag)
    >>> encoder.register(type_tag)
    >>> encoder.encode('hello world')
    b'\x05\n\x00\x00\x01\xff\xfeh\x00e\x00l\x00l\x00o\x00 \x00w\x00o\x00r\x00l\x00d\x00'


Note
****
By now you may have noticed that there's some extra data included
in these outputs. More on that later.

Considerations for Custom Encoders
**********************************
* They must subclass ``AbstractEncoder`` and override
  ``AbstractEncoder.encode`` and ``AbstractEncoder.decode``.
* The ``encode`` method must return a ``str`` or ``bytes`` object.
* Encoders must have a unique ``encoder_id``. This should be
  an integer ``0 <= encoder_id <= 127``. If you find you need more
  than 128 custom encoders, well, that's just crazy talk.
* Encoders must be added to the registry and named by being
  wrapped in a ``EncoderTag`` object.


Proxying Encoders
-----------------
The ``AbstractEncoder`` class has a built-in proxy pattern which can
be utilized to build a proxy 'stack' of encoders in order to perform
logging, inspection, and multi-step object manipulation:

.. code-block:: python

    >>> from anyencoder import AnyEncoder, EncoderTag, TypeTag
    >>> from anyencoder.plugins.zlib import ZlibEncoder
    >>> from anyencoder.plugins.strbyte import StrByteEncoder
    >>> from anyencoder.plugins.ujson import UJsonEncoder
    >>> zlib = ZlibEncoder()
    >>> strbyte = StrByteEncoder(proxy_to=zlib)
    >>> json_zlib = UJsonEncoder(encoder_id=1, proxy_to=strbyte)
    >>> encoder_tag = EncoderTag('json-zlib', json_zlib)
    >>> type_tag = TypeTag(dict, lambda _: 'json-zlib')
    >>> data = dict(a=1, b=2, c=3)
    >>> with AnyEncoder() as encoder:
    ...     encoder.register([encoder_tag, type_tag])
    ...     result = encoder.encode(data)
    ...
    >>> result
    b'\x05\x01\x00\x00\x01x\x9c\xabVJT\xb22\xd4QJR\xb22\xd2QJV\xb22\xae\x05\x00-=\x04\x87'


Considerations for Proxying Encoders
************************************
* When building a proxy stack, the ``encoder_id`` is only relevant for
  the bottom (first) encoder in the stack. The proxy stack counts as
  a single encoder, and the first encoder in the stack needs a unique
  ``encoder_id``. The ``encoder_id`` can be passed as an argument to
  facilitate easily re-using existing classes in proxy stacks.

* A proxy 'stack' is itself registered as a unique encoder with a
  unique ``encoder_id`` As with other encoders, a proxy stack's
  ``encode`` method must return either ``bytes`` or ``str`` data.
  However, individual 'encoders' in the stack can perform other
  actions, as long as the stacks's ``encode`` method provides
  data and ``decode`` method can do something with that data.
  This allows you to do other things with indivudal 'encoders'
  in the stack, such as implement callbacks, logging, heuristics,
  object inspection, etc...


Encoder Plugin Loading
----------------------
Several pre-baked encoder plugins are included, and are loaded
by the ``load_encoder_plugins`` method. This method is called
automatically when ``AnyEncoder``'s context manager is invoked:

.. code-block:: python

    >>> from pprint import pprint
    >>> from anyencoder import AnyEncoder
    >>> with AnyEncoder() as encoder:
    ...     types, encoders = encoder.registry.dump()
    ...
    >>> pprint(encoders)
    [EncoderTag(name='bson',encoder=BSONEncoder(encode_kwargs={},decode_kwargs={},    encoder_id=136,proxy_to=None)),
     EncoderTag(name='bzip2',encoder=Bzip2Encoder(encode_kwargs={},decode_kwargs={},    encoder_id=137,proxy_to=None)),
     EncoderTag(name='cloudpickle',encoder=CloudPickleEncoder(encode_kwargs={},    decode_kwargs={},encoder_id=130,proxy_to=None)),
     EncoderTag(name='dill',encoder=DillEncoder(encode_kwargs={'protocol': 4},    decode_kwargs={},encoder_id=129,proxy_to=None)),
     EncoderTag(name='gzip',encoder=GzipEncoder(encode_kwargs={},decode_kwargs={},    encoder_id=144,proxy_to=None)),
     EncoderTag(name='json',encoder=JSONEncoder(encode_kwargs={},decode_kwargs={},    encoder_id=133,proxy_to=None)),
     EncoderTag(name='msgpack',encoder=MessagePackEncoder(encode_kwargs={'use_bin_type': True},decode_kwargs={'raw': False},encoder_id=131,proxy_to=None)),
     EncoderTag(name='orjson',encoder=OrJsonEncoder(encode_kwargs={},decode_kwargs={},encoder_id=134,proxy_to=None)),
     EncoderTag(name='pickle',encoder=PickleEncoder(encode_kwargs={'protocol': 4},decode_kwargs={},encoder_id=128,proxy_to=None)),
     EncoderTag(name='strbyte',encoder=StrByteEncoder(encode_kwargs={},decode_kwargs={},encoder_id=132,proxy_to=None)),
     EncoderTag(name='ujson',encoder=UJsonEncoder(encode_kwargs={},decode_kwargs={},encoder_id=135,proxy_to=None)),
     EncoderTag(name='zlib',encoder=ZlibEncoder(encode_kwargs={},decode_kwargs={},encoder_id=145,proxy_to=None))]


Note
****
Several of the plugins require third-party libraries in order to be
loaded and registered.


------------
How It Works
------------

Labels
------
After object encoding, ``anyencoder`` prepends a label to the data.
At decode time, the label is removed and read in order to determine
how to decode the data.

For binary data, the label is 5 bytes in length:
``label_len|encoder_id|version_major|version_minor|version_micro``

For text data, the label is a small JSON dictionary.

Warning
*******
Because the data is modified to include the label, it must be decoded
with ``anyencoder`` in order to extract the label. Serializing an
object with ``anyencoder`` and then trying to decode the result with
the concrete serializer is *guaranteed* to fail.


Encoder IDs
-----------
Because ``encoder_id`` is limited to a single byte, it must be a
value between ``0`` and ``255``. Values ``128`` through ``255`` are
reserved for the library, and therefore you should choose a ``value``
where ``0 <= value <= 127`` when choosing the ``encoder_id`` for a
custom encoder.


