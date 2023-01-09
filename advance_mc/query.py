from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Literal, Self
from .nbt.entity import Entity
from ._namespacing import ResourceLocation

@dataclass
class EntityQueryMulti:
    
    nbt: Entity|dict|None = None
    
    x: float|str|None = None
    y: float|str|None = None
    z: float|str|None = None
    
    x: float|None = None
    y: float|None = None
    z: float|None = None
    
    distance: float|range|None = None
    scores: dict|None = None
    tag: str|None = None
    
    name: str|None = None
    type: ResourceLocation|str|None = None
    
    predicate: ResourceLocation|str|None = None
    
    x_rotation: float|None = None
    y_rotation: float|None = None
    
    level: int|None = None
    gamemode: str|None = None
    advancements: dict|None = None
    
    limit: int|None = None
    sort: Literal['nearest', 'random']|None = None
    
    def __post_init__(self):
        if self.predicate is not None:
            self.predicate = ResourceLocation.validate(self.predicate)
            
    
    @classmethod
    def validate(cls, target: Entity|EntityQueryMulti|dict) -> Self:
        if isinstance(target, EntityQueryMulti):
            return target
        else:
            return cls(nbt=target)
    

