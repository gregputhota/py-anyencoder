"""
Objects provided by this module:
    * :class:`EncoderTag`
    * :class:`TypeTag`
    * :class:`Registry`
    * :func:`iter_plugins`
"""


from dataclasses import dataclass, field
from importlib import import_module
from pkgutil import iter_modules
from typing import Any, Callable, Iterable, List, Union, Tuple

from multi_key_dict import multi_key_dict

from anyencoder.config import ENCODER_ID_MAX_SIZE
from anyencoder.plugins.base import BaseEncoder
from anyencoder.util import simple_str


@simple_str
@dataclass
class EncoderTag:
    """
    This dataclass encapsulates an instance of a data encoder for use
    within the :class:`Registry` instance.
    """

    # __slots__ = ('encoder', 'name')

    name: str
    encoder: BaseEncoder
    id: int = field(init=False)

    def __post_init__(self):
        """ Field validation. """
        # Ensure it quacks right and do some coercion.
        if not hasattr(self.name, '__str__'):
            raise TypeError('invalid encoder name')
        self.name = str(self.name)

        # Validate the encoder
        attrs = ('encoder_id', 'encode', 'decode')
        if not all(map(lambda a: hasattr(self.encoder, a), attrs)):
            raise TypeError(f'{type(self.encoder)}')

        # Validate the encoder_id
        _id = self.encoder.encoder_id
        if not hasattr(_id, '__int__'):
            raise TypeError(f'id must be an integer: {_id}')
        _id = int(_id)
        # The label allocates one byte to encoder_id storage. In the
        # docs I claim that you can only use 0 < 128, but in practice
        # I only enforce that it's < 256.
        if _id > ENCODER_ID_MAX_SIZE:
            raise TypeError(f'id too large: {_id}')

        self.id = _id

    def __int__(self):
        """ Make it possible to sort these on their id. """
        return self.id

    def __eq__(self, other):
        """ Enable comparisons with other instances. """
        return (isinstance(other, self.__class__) and
                self.name == other.name and
                self.encoder.__class__ == other.encoder.__class__ and
                self.id == other.id)


@simple_str
@dataclass
class TypeTag:
    """
    This dataclass encapsulates an instance of a data type for use
    within the :class:`Registry` instance.
    """

    __slots__ = ('type_', 'evaluator')

    type_: type
    evaluator: Callable[[Any], Union[int, str]]

    def __post_init__(self):
        """ Field validation. """
        if not isinstance(self.type_, type):
            raise TypeError(self.type_)

        if not callable(self.evaluator):
            raise TypeError('evaluator must be callable')

    def __eq__(self, other):
        """ Enable comparisons with other instances. """
        return (isinstance(other, self.__class__) and
                self.type_ == other.type_)


# Annotations
RegistryTag = Union[EncoderTag, TypeTag]
RegistryKey = Union[int, str, type]


@simple_str
class Registry:
    """
    This class provides a registry for storing :class:`TypeTag` and
    :class:`EncoderTag` definitions. During object encoding, the
    registry is consulted in order to select the concrete encoder.

    Public methods:
     * :func:`Registry.clear`
     * :func:`Registry.contains`
     * :func:`Registry.get`
     * :func:`Registry.register`
     * :func:`Registry.remove`
    """

    __slots__ = ('encoder_data', 'type_data')

    def __init__(self):
        """ Construct a new Registry instance. """
        self.encoder_data = multi_key_dict()
        self.type_data = dict()

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def _item_key_store(
            self,
            item: Union[RegistryTag, RegistryKey],
    ) -> Tuple[Any, Any]:
        """
        For a given item, derive the appropriate backing store and
        index to use.
        """
        # EncoderTag objects are indexed by both int and str keys
        if isinstance(item, (EncoderTag, int, str)):
            store = self.encoder_data

            # Use a tuple of (int, str) as key when storing EncoderTag
            if isinstance(item, EncoderTag):
                key = (item.id, item.name)
            else:
                key = item

        # TypeTag objects are indexed by the type which they represent
        elif isinstance(item, (TypeTag, type)):
            store = self.type_data

            # Use self-referenced type as key when storing TypeTag
            key = item.type_ if isinstance(item, TypeTag) else item

        # This doesn't quack right
        else:
            raise TypeError('invalid registry item')

        return key, store

    def clear(self) -> None:
        """ Clear all items from the registry. """
        self.type_data.clear()
        self.encoder_data.items_dict.clear()

    def contains(self, item: Union[RegistryTag, RegistryKey]) -> bool:
        """
        Query the registry for the existence of an item.

        :param item: A registry tag or item key.
        :return: A boolean indiciating whether the item exists in the
          registry.
        """
        key, store = self._item_key_store(item)
        return key in store

    def get(self, key: RegistryKey) -> Union[RegistryTag, None]:
        """
        Fetch an item from the registry.

        :param key: A registry item key.
        :return: The item, or None if the item doesn't exist in the
          registry.
        """
        _, store = self._item_key_store(key)

        try:
            return store[key]
        except KeyError:
            return None

    def dump(self) -> Tuple[List[TypeTag], List[EncoderTag]]:
        """
        Dump the contents of the registry, returning all currently
        registered :class:`TypeTag` and :class:`EncoderTag`
        objects as a tuple of lists

        :return: The contents of the registry, as a tuple of lists.
        """
        types = [tag for tag in self.type_data.values()]
        encoders = [tag for tag in self.encoder_data.values()]

        return types, encoders

    def register(
            self,
            item: Union[RegistryTag, Iterable[RegistryTag]],
    ) -> None:
        """
        Add an item to the registry.

        :param item: A registry tag instance.
        """
        # If given an Iterable of tags, iterate and recurse
        if issubclass(type(item), Iterable):
            assert not isinstance(item, str)
            for tag in item:
                self.register(tag)
            return

        # Figure out our key and backing store
        key, store = self._item_key_store(item)

        def _reject_duplicates(item):
            if self.contains(item):
                raise ValueError(f'Duplicate item: {item}')

        # Check a tuple of keys individually
        if isinstance(key, tuple):
            for k in key:
                _reject_duplicates(k)
        else:
            _reject_duplicates(key)

        # Store the item
        try:
            store[key] = item
        except KeyError as e:
            raise ValueError from e

    def remove(self, item: Union[RegistryTag, RegistryKey]) -> None:
        """
        Remove an item from the registry.

        :param item: A registry tag or item key.
        """
        key, store = self._item_key_store(item)

        # multi_key_dict.__delitem__() won't accept a tuple of keys
        if isinstance(key, tuple):
            key, _ = key

        try:
            del store[key]
        except KeyError:
            raise ValueError(f'No such key: {key}')


def iter_plugins(path, prefix) -> Iterable[EncoderTag]:
    """
    Iterate a list of paths, discover plugins which contain
    :class:`EncoderTag` instances, and return those instances
    as a generator.
    """
    # If you're here because you're trying to build your own plugin,
    # the only thing you really need to know is that each plugin
    # module must contain a valid EncoderTag named tag. Beyond that,
    # the implementation is up to the plugin.
    modules = iter_modules(
        path=path,
        prefix=prefix,
    )

    for m in modules:
        try:
            module = import_module(name=m.name)
            tag = module.tag  # Top-level EncoderTag
            if not isinstance(tag, EncoderTag):
                raise TypeError
            yield tag
        except (AttributeError, ImportError, TypeError):
            pass
