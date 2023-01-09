from __future__ import annotations

from typing import Optional, Union

import pydantic

from ..dtypes import dumps, Short, IntArray, ResourceLocation


class Entity(pydantic.BaseModel, extra=pydantic.Extra.forbid):

    def summon_cmd(self) -> str:
        return f'summon {self.id} ~ ~ ~ {dumps(self)}'

    Air: Optional[float]
    CustomName: Optional[str]
    CustomNameVisible: Optional[bool]
    FallDistance: Optional[float]
    Fire: Optional[Short]
    Glowing: Optional[bool]
    HasVisualFire: Optional[bool]
    id: str
    Invulnerable: Optional[bool]
    Motion: Optional[tuple[float, float, float]]
    NoGravity: Optional[bool]
    OnGround: Optional[bool]
    Passengers: Optional[list[Entity]]
    PortalCooldown: Optional[int]
    Pos: Optional[tuple[float, float, float]]
    Rotation: Optional[tuple[float, float]]
    Silent: Optional[bool]
    Tags: Optional[list[str]]
    UUID: Optional[IntArray]


class _Leash1(pydantic.BaseModel, extra=pydantic.Extra.forbid):
    UUID: IntArray


class _Leash2(pydantic.BaseModel, extra=pydantic.Extra.forbid):
    X: int
    Y: int
    Z: int


class Mob(Entity):
    ActiveEffects: Optional[list['Effect']]
    ArmorDropChances: Optional[tuple[float, float, float, float]]
    ArmorItems: Optional[tuple[ItemStack, ItemStack, ItemStack, ItemStack]]
    Attributes: Optional[list] # TODO: attributes
    Brain: Optional[dict]
    CanPickUpLoot: Optional[bool]
    DeathLootTable: Optional[ResourceLocation] # Todo: resource locations
    DeathLootTableSeed: Optional[int] # long
    DeathTime: Optional[Short]
    FallFlying: Optional[bool]
    Health: Optional[float]
    HurtByTimestamp: Optional[int]
    HurtTime: Optional[int]
    HandDropChances: Optional[tuple[float, float]]
    HandItems: Optional[tuple['ItemStack', 'ItemStack']]
    Leash: Union[_Leash1, _Leash2, None]
    LeftHanded: Optional[bool]
    NoAI: Optional[bool]
    PersistenceRequired: Optional[bool]
    SleepingX: Optional[int]
    SleepingY: Optional[int]
    SleepingZ: Optional[int]
    Team: Optional[int]


from ..item import ItemStack, Effect
Mob.update_forward_refs()
Entity.update_forward_refs()