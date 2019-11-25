"""
Objects provided by this module:
    * :class:`MakerMixIn`
    * :class:`RegistryMixIn`
    * :class:`ReaderMixIn`
    * :class:`Decode`
    * :class:`Encode`
    * :class:`DynamicEncoder`
    * :class:`SimpleEncoder`
    * :func:`encode_with`
"""


from functools import wraps
from typing import (
    Any,
    AnyStr,
    Callable,
    Optional,
    Union,
)


from anyencoder.config import (
    DEFAULT_ENCODER,
    DEFAULT_PLUGIN_PATH,
    DEFAULT_PLUGIN_PREFIX,
    HINT_ATTR,
)
from anyencoder.maker import LabelMaker
from anyencoder.plugins import AbstractEncoder
from anyencoder.reader import LabelReader
from anyencoder.registry import Registry, iter_plugins
from anyencoder.util import simple_str


# Annotations
EncoderID = Union[int, str]
ReaderFactory = Callable[[AnyStr], LabelReader]
MakerFactory = Callable[[int], LabelMaker]


class MakerMixIn:
    """ MakerFactory MixIn class. """

    def __init__(self, maker_factory: MakerFactory):
        """
        :param maker_factory: A factory which produces
          LabelMaker objects.
        """
        self._maker_factory = maker_factory


class RegistryMixin:
    """ Registry MixIn class. """

    def __init__(self, registry: Registry):
        """ :param registry: A reference to the active Registry. """
        self._registry = registry

    def _encoder_from_encoder_id(
            self,
            encoder_id: EncoderID,
    ) -> AbstractEncoder:
        """ Return the data encoder for a given Encoder ID. """
        # Total failure
        if encoder_id is None:
            raise ValueError(f'invalid encoder_id: {encoder_id}')

        encoder_tag = self._registry.get(encoder_id)
        if encoder_tag:
            encoder = encoder_tag.encoder
        else:
            raise ValueError(f'encoder not found for id: {encoder_id}')

        if not isinstance(encoder, AbstractEncoder):
            raise ValueError(f'invalid encoder: {encoder}')

        return encoder


class ReaderMixIn:
    """ ReaderFactory MixIn class. """

    def __init__(self, reader_factory: ReaderFactory):
        """
        :param reader_factory: A factory which produces
          LabelReader objects.
        """
        self._reader_factory = reader_factory


@simple_str
class Decode(RegistryMixin, ReaderMixIn):
    """
    This class provides the abstract decoding logic.
    A callable interface is provided.
    """

    __slots__ = (
        '_reader_factory',
        '_registry',
    )

    def __init__(
            self,
            *,
            registry: Registry,
            reader_factory: ReaderFactory,
    ):
        """ Construct a new callable :class:`Decode` instance. """
        RegistryMixin.__init__(self, registry)
        ReaderMixIn.__init__(self, reader_factory)

    def __call__(
            self,
            data: AnyStr,
            encoder: Optional[EncoderID] = None,
    ) -> Any:
        """
        Decode data and return the result.

        :param data: AnyStr representation of an encoded object.
        :param encoder: Optionally override Encoder selection.
        :return: The decoded object.
        """
        _encoder_id = None

        # Call the label reader and retrieve the labeled data
        reader = self._reader_factory(data)
        label = reader.scan()

        # If encoder= was passed, it precedes everything
        if _encoder_id is None:
            if encoder is not None:
                _encoder_id = encoder

        # Derive the encoder from the Label
        if _encoder_id is None:
            _encoder_id = label.encoder_id

        encoder = self._encoder_from_encoder_id(_encoder_id)
        try:
            decoded_data = encoder.decode(label.raw_data)
        except (TypeError, ValueError) as e:
            raise ValueError('unable to decode data') from e

        return decoded_data

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'registry={self._registry!r},'
                f'reader_factory={self._reader_factory!r})')


@simple_str
class Encode(RegistryMixin, MakerMixIn):
    """
    This class provides a callable interface which manages the
    abstract encoding logic.
    """

    __slots__ = (
        '_maker_factory',
        '_registry',
    )

    def __init__(
            self,
            *,
            registry: Registry,
            maker_factory: MakerFactory,
    ):
        """ Construct a new callable :class:`Encode` instance. """
        RegistryMixin.__init__(self, registry)
        MakerMixIn.__init__(self, maker_factory)

    def __call__(
            self,
            obj: Any,
            encoder: Optional[EncoderID] = None,
    ) -> AnyStr:
        """
        Encode an object and return the result.

        :param obj: The object to be encoded.
        :param encoder: Optionally override Encoder selection.
        :return: AnyStr representiation of obj.
        """
        # Get the encoder
        _encoder = self._find_encoder(obj, encoder)
        assert _encoder
        # Encode the payload
        encoded_data = _encoder.encode(obj)
        # Get the LabelMaker from the factory
        maker = self._maker_factory(encoded_data)
        # Build the label using the LabelMaker
        label = maker.apply(_encoder.encoder_id)
        # Grab the labeled payload
        labeled_data = label.labeled_data

        return labeled_data

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'registry={self._registry!r},'
                f'maker_factory={self._maker_factory!r})')

    def _find_encoder(
            self, obj: Any,
            encoder_id: EncoderID,
    ) -> AbstractEncoder:
        """
        Inspect an object and select the concrete encoder.

        :param obj: The object to be encoded.
        :param encoder_id: The value of encoder_id, passed in from
          the first-class API. Currently, this will be used to pre-
          empt other encoder selection logic within this function.
        :return: The concrete encoder instance to be used for data encoding.
        """

        _encoder_id = None

        # If encoder= was passed, it precedes everything
        if _encoder_id is None:
            _encoder_id = encoder_id

        # Inspect the object directly
        if _encoder_id is None:
            try:
                hint = getattr(obj, HINT_ATTR)
                _encoder_id = hint() if callable(hint) else hint
            except AttributeError:
                pass

        # Try the type registry
        if _encoder_id is None:
            data_type = type(obj)
            type_tag = self._registry.get(data_type)

            # The TypeTag includes a callable which evaluates the
            # data and dynamically return the desired encoder_id
            if type_tag:
                evaluator = type_tag.evaluator
                _encoder_id = evaluator(obj)

        # Fall back to default
        if _encoder_id is None:
            _encoder_id = DEFAULT_ENCODER

        # Map the encoder_id to an encoder instance
        encoder = self._encoder_from_encoder_id(_encoder_id)

        return encoder


@simple_str
class DynamicEncoder(MakerMixIn, ReaderMixIn):
    """
    This class provides an interface to the underlying encoders.
    Several pre-baked encoder definitions are pre-loaded when this
    class's context manager is called.

    Public methods:
      * :func:`EncoderSession.encode` (:func:`Encode.__call__`)
      * :func:`EncoderSession.decode` (:func:`Decode.__call__`)
      * :func:`EncoderSession.register` (:func:`Registry.register`)
      * :func:`EncoderSession.load_encoder_plugins`


    >>> from anyencoder import DynamicEncoder
    >>> data = [1, 2, 3]
    >>> with DynamicEncoder() as encoder:
    >>>    encoded = encoder.encode(data)
    >>>    decoded = encoder.decode(encoded)
    >>> assert decoded == data
    """

    __slots__ = (
        '_maker_factory',
        '_reader_factory',
        'registry',
        'decode',
        'encode',
        'register',
    )

    def __init__(
            self,
            *,
            maker_factory: Optional[MakerFactory] = None,
            reader_factory: Optional[ReaderFactory] = None,
            registry: Optional[Registry] = None,
    ):
        """
        Construct a new DynamicEncoder object.

        :param maker_factory: Inject an alternate maker factory.
        :param reader_factory: Inject an alternate reader factory.
        :param registry: Inject an alternate registry.
        """
        maker_factory = maker_factory if maker_factory else LabelMaker
        reader_factory = reader_factory if reader_factory else LabelReader
        MakerMixIn.__init__(self, maker_factory)
        ReaderMixIn.__init__(self, reader_factory)

        # Add the Registry through composition
        self.registry = registry if registry else Registry()
        self.register = self.registry.register

        # Add the abstract encoder callables
        self.decode = Decode(
            registry=self.registry,
            reader_factory=self._reader_factory,
        )
        self.encode = Encode(
            registry=self.registry,
            maker_factory=self._maker_factory,
        )

    def __enter__(self):
        """
        This context manager automatically finds and registers several
        pre-baked concrete encoder definitions.
        """
        self.load_encoder_plugins()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'maker_factory={self._maker_factory!r},'
                f'reader_factory={self._reader_factory!r},'
                f'registry={self.registry!r})')

    def load_encoder_plugins(
            self,
            *,
            path: str = DEFAULT_PLUGIN_PATH,
            prefix: str = DEFAULT_PLUGIN_PREFIX,
    ) -> None:
        """
        Specify a path from which pre-baked encoder plugins should
        be discovered and added to the registry. This is an alternate
        way to register a set of plugins and is probably only useful
        under a limited set of circumstances.

        Both arguments are passed to pkgutil.iter_modules

        :param path: A sys.path format list of paths to search.
        :param prefix: A prefix for relative module imports.
        """
        self.register(iter_plugins(path, prefix))


@simple_str
class SimpleEncoder:
    """
    This is a simple wrapper around :class:`DynamicEncoder`. This
    class is mainly useful for testing purposes; for optimal
    performance, instantiate :class:`DynamicEncoder`.

    Public methods:
      * :func:`SimpleEncoder.encode`
      * :func:`SimpleEncoder.decode`
    """

    _encoder = DynamicEncoder

    @classmethod
    def encode(cls, obj: Any, encoder: Optional[EncoderID] = None) -> AnyStr:
        """
        Encode an object and return the result.

        :param obj: Any serializable object.
        :param encoder: Optionally override the encoder selection.
        """
        with cls._encoder() as _encoder:
            return _encoder.encode(obj, encoder=encoder)

    @classmethod
    def decode(cls, data: AnyStr, encoder: Optional[EncoderID] = None) -> Any:
        """
        Decode data and return the result.

        :param data: A byte-or-string representing the encoded object.
        :param encoder: Optionally override the encoder selection.
        """
        with cls._encoder() as _encoder:
            return _encoder.decode(data, encoder=encoder)

    def __repr__(self):
        return f'{self.__class__.__name__}()'


_encoder = SimpleEncoder()
dumps = encode = _encoder.encode
loads = decode = _encoder.decode


def encode_with(encoder: Union[int, str], attr_name=HINT_ATTR):
    """
    This is a decorator which sets an attribute on an object to specify
    an EncoderID to use.

    :param encoder: A string or integer EncoderID.
    :param attr_name: Optionally override the attribute name.
    """
    def decorator(obj):

        @wraps(obj)
        def wrapper(encoder, attr_name):
            if hasattr(obj, attr_name):
                raise TypeError(obj)
            setattr(obj, attr_name, encoder)
            return obj

        return wrapper(encoder, attr_name)

    return decorator
