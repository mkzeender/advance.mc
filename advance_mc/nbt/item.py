from pydantic import BaseModel, Extra
from typing import Optional
from .dtypes import IntArray, Short, Byte
from warnings import warn
from enum import Enum


class InventorySlot(Byte):
    def __init__(self, val):
        super().__init__(val)
        if not 0 <= self <= 35 and self not in (self.offhand, self.feet, self.legs, self.chest, self.head):
            raise ValueError(f'{self} is not an InventorySlot')

    offhand = Byte(-106)
    feet = Byte(100)
    legs = Byte(101)
    chest = Byte(102)
    head = Byte(103)


class AttribModSlot(Enum):
    mainhand = 'mainhand'
    offhand = 'offhand'
    feet = 'feet'
    legs = 'legs'
    chest = 'chest'
    head = 'head'


class AttribModOperation(Enum):
    add = 0
    multiply_base = 1
    multiply = 2


class AttribMod(BaseModel, extra=Extra.forbid):
    AttributeName: str
    Name: str
    Slot: AttribModSlot
    Operation: AttribModOperation = 0
    Amount: float
    UUID: Optional[IntArray]


class _Display(BaseModel, extra=Extra.forbid):
    color: Optional[int] # todo: COLORS
    Name: Optional[str]
    Lore: Optional[list[str]]


class HideFlags(int):
    def __new__(cls, __x=0, enchantments=False, attributemodifiers=False, unbreakable=False, candestroy=False, canplaceon=False, other=False, dyed=False):
        return super().__new__(cls, __x + enchantments + 2 * attributemodifiers + 4*unbreakable + 8*candestroy + 16*canplaceon + 32*other + 64*dyed)


class Enchantment(BaseModel, extra=Extra.forbid):
    id: str
    lvl: Short


class EffectId(Enum):
    absorption = Byte(22)
    bad_omen = Byte(31)
    blindness = Byte(15)
    conduit_power = Byte(29)
    dolphins_grace = Byte(30)
    fire_resistance = Byte(12)
    glowing = Byte(24)
    haste = Byte(3)
    health_boost = Byte(21)
    hero_of_the_village = Byte(32)
    hunger = Byte(17)
    instant_health = Byte(6)
    instant_damage = Byte(7)
    invisibility = Byte(14)
    jump_boost = Byte(8)
    levitation = Byte(25)
    luck = Byte(26)
    mining_fatigue = Byte(4)
    nausea = Byte(9)
    night_vision = Byte(16)
    poison = Byte(19)
    regeneration = Byte(10)
    resistance = Byte(11)
    saturation = Byte(23)
    slow_falling = Byte(28)
    slowness = Byte(2)
    speed = Byte(1)
    strength = Byte(5)
    unluck = Byte(27)
    water_breathing = Byte(13)
    weakness = Byte(18)
    wither = Byte(20)
    darkness = Byte(33)


class Effect(BaseModel, extra=Extra.forbid):
    Id: EffectId
    Amplifier: Byte = Byte(1)
    Duration: Optional[int]
    Ambient: Optional[bool]
    ShowParticles: Optional[bool]
    ShowIcon: Optional[bool]


class ItemTag(BaseModel, extra=Extra.allow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for extra in set(kwargs) - self.__fields_set__:
            warn(f'{extra} is not a known item key')

    Damage: Optional[int]
    Unbreakable: Optional[bool]
    CanDestroy: Optional[list[str]] #TODO: block predicates
    CustomModelData: Optional[int]
    AttributeModifiers: Optional[list[AttribMod]]
    CanPlaceOn: Optional[list[str]] #TODO: block predicates
    BlockEntityTag: Optional[dict] # TODO: block entity tags
    BlockStateTag: Optional[dict] # TODO: block state
    display: Optional[_Display]
    HideFlags: Optional[HideFlags]
    Enchantments: Optional[list[Enchantment]]
    StoredEnchantments: Optional[list[Enchantment]]
    RepairCost: Optional[int]
    CustomPotionEffects: Optional[list[Effect]]
    Potion: Optional[str]
    CustomPotionColor: Optional[int] #TODO: color
    EntityTag: Optional['Entity']
    # TODO: book pages, fireworks, etc


class ItemStack(BaseModel, extra=Extra.forbid):
    Count: Byte = Byte(1)
    id: str
    tag: Optional[ItemTag]
    Slot: Optional[InventorySlot]


from .entity.base import Entity
ItemTag.update_forward_refs()