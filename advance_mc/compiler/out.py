from zipfile import ZipFile
from os.path import join
import os
import json
from .._namespacing import Namespace


class Datapack:
    def __init__(self, name, pack_format=10, description='Created by PyneCraft'):
        self.meta = {
            'pack': {
                'pack_format': pack_format,
                'description': description
            }
        }
        self.name = name

    def compile(self):
        with ZipFile(self.name, 'w') as z:

            z.writestr('pack.mcmeta', json.dumps(self.meta))

            # create each namespace
            for namespace in Namespace.instances.values():

                # copy any json files and nbt files
                for folder in 'advancements, dimension, dimension_type, functions, loot_tables, predicates, recipes, structures, tags, worldgen':
                    for dirpath, dnames, filenames in os.walk(join(namespace.src_folder, folder)):
                        for file in filenames:
                            file: str
                            if file.lower().endswith(('.json', '.nbt')):
                                z.write(join('data', namespace.name, folder, file))

                # create mcfunction files
                for func in namespace.functions:
                    func_code = '\n'.join(func.commands)
                    z.writestr(f'data/{namespace.name}/functions/{func.path}.mcfunction', func_code)

                # TODO: create events

