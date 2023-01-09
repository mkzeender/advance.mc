import enum

from pydantic import BaseModel, validator, Extra
from .nbt.dtypes import NamespacedId
from typing import Optional, Literal

class NbtLikeMeta(type):
    def __call__(cls, *args, **kwargs):
        super(NbtLikeMeta, cls).__call__(*args, **kwargs)
        cls.dtype = BaseModel

    def __getitem__(cls, item: type):
        if not issubclass(item, BaseModel):
            raise TypeError('Data types must be nbt-like')
        new_type = NbtLikeMeta(f'{cls.__name__}[{item.__name__}]', (cls,), {'dtype': item})


class NbtLike(metaclass=NbtLikeMeta):
    def __init__(self, item: str|BaseModel):
        ...


class Conditions(BaseModel, extra=Extra.forbid):
    pass


class Event(BaseModel):
    conditions: Conditions
    trigger: NamespacedId = 'minecraft:impossible'

    @validator('trigger')
    def trigger_setter(cls, v, values, **kwargs):
        return NamespacedId(type(values['conditions']).__name__)


MinAndMax = Literal['min', 'max']
FloatRange = dict[MinAndMax, float] | float
IntRange = dict[MinAndMax, int] | int


class BlockLoc(BaseModel, extra=Extra.forbid):
    blocks: Optional[list[NamespacedId]]
    tag: Optional[NamespacedId]
    nbt: Optional[NbtLike] # TODO: NBTLIKE
    state: Optional[dict]


class FluidLoc(BaseModel, extra=Extra.forbid):
    fluid: Optional[NamespacedId]
    tag: Optional[NamespacedId]
    state: Optional[dict]


class LightLoc(BaseModel, extra=Extra.forbid):
    light: IntRange

class Location(BaseModel, extra=Extra.forbid):
    biome: Optional[NamespacedId]
    block: Optional[BlockLoc]
    dimension: Optional[NamespacedId]
    fluid: Optional[FluidLoc]