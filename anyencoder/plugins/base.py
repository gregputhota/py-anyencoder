"""
Objects provided by this module:
    * :class:`Encodings`
    * :func:`proxy_attrs`
    * :class:`Proxy`
    * :class:`ConcreteEncoder`
    * :class:`BaseEncoder`
    * :class:`AbstractEncoder`
"""


from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import Any, AnyStr, Callable, Optional


@dataclass
class Encodings:
    """
    This dataclass provides integer constants for the pre-baked
    encoder definitions.
    """

    PICKLE: int = 0x80
    CLOUDPICKLE: int = 0x81
    DILL: int = 0x82
    MSGPACK: int = 0x83
    JSON: int = 0x84
    ORJSON: int = 0x85
    UJSON: int = 0x86
    BSON: int = 0x87
    BZIP2: int = 0x88
    GZIP: int = 0x89
    ZLIB: int = 0x8A
    STRBYTE: int = 0x8B


encodings = Encodings()


def proxy_attrs(arg='_proxy_to'):
    """
    This decorator adds hooks to a class which proxy lookup attempts
    for non-existent attributes to the next class in the proxy
    'stack'.
    """
    def decorator(cls):
        if hasattr(cls, '__getattr__'):
            raise TypeError(cls)

        @wraps(cls)
        def wrapper(target_cls):
            def __getattr__(_, item):
                try:
                    return getattr(target_cls, item)
                except AttributeError as e:
                    raise AttributeError from e

            cls.__getattr__ = __getattr__
            return cls
        return wrapper(target_cls)

    if isinstance(arg, str):
        # called as @decorator(arg)
        target_cls = arg
    else:
        # called as @decorator
        target_cls = '_proxy_to'
        decorator = decorator(arg)
    return decorator


@dataclass
class ConcreteEncoder:
    """
    This dataclass encapsulates a conrete encoder callable definition,
    mapping callable references to their concrete counterparts.
    """

    encode: Callable
    decode: Callable
    encode_kwargs: dict
    decode_kwargs: dict

    def __str__(self):
        return self.__class__.__name__


class Proxy:
    """
    This class implements a proxy pattern. It has a constructor which
    stores the next object in the proxy stack and methods to build
    outer callables.
    """

    _proxy_to = None

    def __init__(self, proxy_to: Any):
        """ :param proxy_to: The next item in the proxy stack. """
        self._proxy_to = proxy_to

    @staticmethod
    def _proxied_callable(inner: Callable, outer: Callable) -> Callable:
        """
        This is a closure which builds a proxy from two methods and
        returns a new callable object, to be used in place of the original
        methods.

        :param inner: The 'inner' method, which will be wrapped.
        :param outer: The 'outer' method, which will wrap the 'local'
          method.
        :return: The new callable object.
        """
        assert callable(inner) and callable(outer)

        @wraps(inner)
        def wrapper(value):
            return outer(inner(value))
        return wrapper

    def _proxy_method(self, method: Callable, invert: bool = False) -> None:
        """
        Given a method reference, set up a proxy association. The next
        item in the proxy stack must have a method of the same name.
        The method is modified to include proxying through the next
        item in the stack.

        If invert=True, the proxying behavior is reversed.

        :param method: The method to proxy.
        :param invert: If True, invert the proxy association.
        """
        name = method.__name__
        inner = getattr(self, name)
        outer = getattr(self._proxy_to, name)

        if invert is True:
            inner, outer = outer, inner

        new = self._proxied_callable(inner, outer)
        setattr(self, name, new)


class BaseEncoder(ABC):
    """
    This class is an abstract base for object encoder definitions.
    This class together with :class:`ConcreteEncoder` serve as an
    adapter between higher level code and the concrete encoder.

    Rather than subclassing this object, you probably want to subclass
    :class:`AbstractEncoder`, which inherits from this class.

    Abstract methods:
        * :func:`BaseEncoder.decode`
        * :func:`BaseEncoder.encode`
    """
    @classmethod
    def __init_subclass__(cls, **kwargs):
        """
        An encoder can either provide its own encode / decode methods
        or it can provide a ConcreteEncoder instance as a class
        argument.
        """
        try:
            # If a ConcreteEncoder is passed in, we use it to build the
            # encode/decode methods. This is an alternative to defining
            # encode/decode directly in the derived class.
            concrete_encoder: ConcreteEncoder = kwargs.pop('concrete_encoder')

            cls._concrete_encoder = concrete_encoder

            @wraps(cls.encode)
            def _encode(cls, data):
                encode = cls._concrete_encoder.encode
                kwargs = cls._concrete_encoder.encode_kwargs
                return encode(data, **kwargs)
            cls.encode = _encode

            @wraps(cls.decode)
            def _decode(cls, data):
                decode = cls._concrete_encoder.decode
                kwargs = cls._concrete_encoder.decode_kwargs
                return decode(data, **kwargs)
            cls.decode = _decode

        except KeyError:
            pass

    def __str__(self):
        return self.__class__.__name__

    def encode(self, obj: Any) -> AnyStr:
        """
        Encode value

        :param obj: Object to be encoded
        :return: Encoded data.
        """
        # This is an abstract method and needs to be
        # overriden or replaced (see __init_subclass__)
        raise NotImplementedError

    def decode(self, data: AnyStr) -> Any:
        """
        Decode value

        :param data: Data to be decoded
        :return: Decoded object.
        """
        # See previous comment
        raise NotImplementedError

    @property
    @abstractmethod
    def encoder_id(self):
        """Unique integer ID for this encoder."""
        # This doesn't need to be a property but needs to be set.
        raise NotImplementedError


class AbstractEncoder(BaseEncoder, Proxy, ABC):
    """
    This is an abstract base, to be subclassed for the creation of
    custom encoder definitions.
    """

    def __init__(
            self,
            *,
            encoder_id: Optional[int] = None,
            proxy_to: Optional[BaseEncoder] = None,
    ):
        """
        Construct a new :class:`AbstractEncoder` instance.

        :param encoder_id: Set the encoder_id attribute. This enables
          easy overriding of the value when re-purposing this class
          for use in a proxy stack.
        :param proxy_to: A reference to an existing AbstractEncoder
          instance. This object will wrap its own data encoding with
          the encoder referenced by 'proxy_to'.
        """
        if encoder_id is not None:
            self.encoder_id = encoder_id

        if proxy_to is not None:
            # Proxying is accomplished by replacing encode/decode with
            # calls which wrap the next object in the proxy stack.
            if not isinstance(proxy_to, AbstractEncoder):
                raise TypeError('bad proxy target')
            Proxy.__init__(self, proxy_to)

            # Wrap self.encode around proxy_to.encode
            self._proxy_method(self.encode)

            # Wrap proxy_to.decode around self.decode
            self._proxy_method(self.decode, invert=True)

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'encoder_id={self.encoder_id!r},'
                f'proxy_to={self._proxy_to!r})')

    @property
    @abstractmethod
    def encoder_id(self):
        return self._encoder_id

    @encoder_id.setter
    def encoder_id(self, value):
        self._encoder_id = value
