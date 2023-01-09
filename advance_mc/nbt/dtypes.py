import pydantic
from typing import Protocol, runtime_checkable, Optional, TypeVar, Sequence
from enum import Enum

T = TypeVar('T')
V = TypeVar('V')


class NbtDataType:

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls: T, v) -> T:
        # always true
        return cls(v)

    def to_nbt(self) -> str:
        pass


class Byte(int, NbtDataType):
    def __init__(self, num: int, **kwargs):
        if not -128 <= num <= 127:
            raise ValueError(f'{num} cannot be made a byte')

    def to_nbt(self) -> str:
        return repr(self) + 'b'


class Short(int, NbtDataType):
    def __init__(self, num: int, **kwargs):
        if not -32768 < num < 32768:
            raise ValueError(f'{num} cannot be made a short')

    def to_nbt(self) -> str:
        return repr(self) + 's'


class BaseTypeArray(list, NbtDataType):
    dtype: type
    dtypename: str

    def __init__(self, seq: Sequence):
        super(BaseTypeArray, self).__init__(seq)
        self[:] = (self.dtype(v) for v in self)

    def to_nbt(self) -> str:
        return f'[{self.dtypename};{", ".join(dumps(x) for x in self)}]'


class IntArray(BaseTypeArray):
    dtype = int
    dtypename = 'I'


class NamespacedId(str, NbtDataType):

    @classmethod
    def validate(cls: T, val: str) -> T:
        from .._namespacing import Namespace

        val = val.lower()
        if val.count(':') == 0:
            val = 'minecraft:' + val

        chars = 'abcdefghijklmnopqrstuvwxyz0123456789_-./'
        if not all(x in chars for x in val) or val.count(':') > 1 or val == 'minecraft:':
            raise ValueError(f'"{val}" is not a valid resource location.')

        namespace, target = val.split(':')
        if namespace not in Namespace.instances:
            print(f'"{val}" is an unresolved resource location. Ignoring.')

        return super(NamespacedId, cls).validate(val)


class ResourceLocation(NamespacedId):
    def __new__(cls, namespaced_id: NamespacedId):
        super(ResourceLocation, cls).__init__(namespaced_id)

    def resolve(self):
        ...


def dumps(data) -> str:
    """
    Formats a tree of data into s-nbt format
    :param data:
    :return: (str) s-nbt
    """
    if isinstance(data, pydantic.BaseModel):
        return dumps(data.dict())

    if isinstance(data, NbtDataType):
        return data.to_nbt()

    if isinstance(data, Enum):
        return data.value

    if isinstance(data, bool):
        return Byte(data).to_nbt()

    if isinstance(data, (list, tuple)):
        return '[' + str.join(', ', (dumps(x) for x in data if x is not None)) + ']'

    if isinstance(data, dict):
        return '{' + str.join(', ', (f'{k}:{dumps(v)}' for k, v in data.items() if v is not None)) + '}'

    if isinstance(data, int):
        if -2147483648 < data < 2147483647:
            return repr(data)
        raise ValueError(f'{data} out of allowed int range')

    if isinstance(data, (str, float)):
        # escapes strings
        return repr(data)

    raise TypeError(f'{type(data)} object could not be interpreted as nbt')


