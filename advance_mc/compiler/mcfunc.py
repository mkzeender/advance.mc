from ..nbt.dtypes import ResourceLocation



class McFunc:
    def __init__(self, name: ResourceLocation) -> None:
        self.name = name
        self.commands = []
    
    def to_str(self):
        return '\n'.join(self.commands)