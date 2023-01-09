from functools import wraps

from .nbt.dtypes import ResourceLocation, NamespacedId
from typing import Optional, Literal
from .nbt.entity import Entity
from .nbt.dtypes import dumps


Target = str | Entity


def resolve_target(target: Target):
    if isinstance(target, Entity):
        target = f'@e[nbt={dumps(target)}]'
    return target


class Function(ResourceLocation):
    def __init__(self, func_name: str):
        super(Function, self).__init__(func_name)
        # @wraps(func)
        # def wrapper():
        #     func_name = ResourceLocation(func_name)
        #
        #     # m: str = func.__module__
        #     # loc = m.find(namespace)
        #     # if loc == -1:
        #     #     raise ValueError(
        #     #         f'Could not locate the function {repr(func)} in the namespace {namespace}. Try putting it in a file named {namespace}.py')
        #     # m = m[loc].removeprefix(namespace).removeprefix('.').replace('.', '/')
        #     #
        #     # namespaced_id = (f'{namespace}:{m}/{func.__name__}' if m else func.__name__)
        #
        #     f = _Function(func_name)
        #     f.func = func
        #     return f
        self.func = lambda: None
        self.commands = []

    def __call__(self, arg: 'callable | Execute | None' = None) -> 'Function | None':
        if callable(arg) and currently_parsed is self.func is None:
            # enables decorator behavior
            self.func: callable = arg
            return self
        elif currently_parsed is not None:
            (execute if arg is None else arg).run(f'function {self}')
            return

        raise RuntimeError('This Minecraft-function cannot be called in the current context.')

    def append_code(self, code: str):
        for line in code.split('\n'):
            self.commands.append(line.strip())


class Execute:
    def __init__(self, context=None):
        if context is None:
            self.context = []
        else:
            self.context = context[:]

    def _add_context(self, context):
        return Execute(self.context + [context])

    def as_(self, target: Target):

        return self._add_context('as {resolve_target(target)}')

    def at_(self, target: Target):
        return self._add_context('at {resolve_target(target)}')

    def align_(self, axes: str):
        return self._add_context(f'align {axes}')

    def anchored(self, anchor: Literal['eyes', 'feet']):
        return self._add_context(f'anchored {anchor}')

    def facing_pos(self, pos: str):
        return self._add_context(f'facing {pos}')

    def facing_entity(self, target: Target):
        return self._add_context(f'facing entity {resolve_target(target)}')

    def in_(self, dimension: NamespacedId | str):
        if isinstance(dimension, str):
            dimension = NamespacedId(dimension)
        return self._add_context(f'in {dimension.resolve()}')

    def positioned(self, pos: str):
        return self._add_context(f'positioned {pos}')

    def positioned_as(self, target: Target):
        return self._add_context(f'positioned as {resolve_target(target)}')

    def rotated(self, pos: str):
        return self._add_context(f'rotated {pos}')

    def rotated_as(self, target: Target):
        return self._add_context(f'rotated as {resolve_target(target)}')

    def if_(self, args):
        return self._add_context(f'if {args}')

    def unless_(self, args):
        return self._add_context(f'if {args}')

    def if_entity(self, target: Target):
        return self._add_context(f'if entity {resolve_target(target)}')

    def unless_entity(self, target: Target):
        return self._add_context(f'if entity {resolve_target(target)}')

    def run(self, *commands: str | Function):
        """
        Use inside a function to run a minecraft command
        :param commands: Command(s) to run. Commands may be separated by newlines
        """
        if currently_parsed is None:
            raise SyntaxError('run() must be called from inside a function')

        for cmd in commands:
            if self.context:
                cmd = f'execute {" ".join(self.context)} run ' + cmd

            currently_parsed.commands.append(cmd)


execute = Execute()
run = execute.run

currently_parsed: Optional[Function] = None
