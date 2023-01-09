from .base import Mob, ItemStack

from pydantic import BaseModel, Extra
from typing import Optional


class _Recipe(BaseModel, extra=Extra.forbid):
    buy: ItemStack
    buyB: Optional[ItemStack]
    demand: int = 0
    maxUses: int
    priceMultiplier: Optional[int] = 0
    rewardExp: Optional[bool]
    sell: ItemStack
    specialPrice: Optional[int]
    uses: Optional[int]
    xp: Optional[int]


class _Offers(BaseModel, extra=Extra.forbid):
    Recipes: list[_Recipe]


class _VillagerData(BaseModel, extra=Extra.forbid):
    level: int = 99
    profession: str = 'farmer'
    type: str = 'plains'


class Villager(Mob):
    Gossips: Optional[list[dict]]
    Offers: Optional[_Offers]
    VillagerData: Optional[_VillagerData]
    Xp: Optional[int]
    Inventory: Optional[list[ItemStack]]
    LastRestock: Optional[int]
    LastGossipDecay: Optional[int]
    RestocksToday: Optional[int]
    Willing: Optional[bool]
