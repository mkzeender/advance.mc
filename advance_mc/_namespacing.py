from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Self
from ._function import Function

import importlib as impl
from pathlib import Path

@dataclass
class ResourceLocation:
    namespace_name: str
    path: str
    
    @classmethod
    def validate(cls, value:str|ResourceLocation) -> Self:
        if isinstance(value, ResourceLocation):
            return value
        else:
            if ':' in value:
                n, p = value.lower().split(':', 2)
            else:
                n = 'minecraft'
                p = value.lower()
                
            if not n.isalpha():
                raise ValueError(f'"{value}" is not a valid resource location')
            return cls(n, p)

    def __str__(self):
        return ':'.join(self.namespace_name, self.path)
        
        
@lru_cache
class Namespace:
    instances: dict[str, 'Namespace'] = {}

    def __init__(self, name: str, parent_package=''):
        """
        Creates a namespace from a python package.
        :param name: The name of a python package. It should contain some of the following modules or subpackages:
            functions
            events
            predicates
        These modules will be automatically imported when compiling the datapack.
        """
        self.instances[name] = self
        self.functions: list[Function] = []
        self.name = name
        self.src_folder = Path(impl.import_module(name).__file__).parent

        try:
            mod = impl.import_module(parent_package + '.' + name)
            impl.import_module('.functions', mod.__name__)
        except ImportError:
            pass

    def function(self, func: callable) -> callable:
        func_obj = Function(func)
        self.functions.append(func_obj)
        return func_obj


