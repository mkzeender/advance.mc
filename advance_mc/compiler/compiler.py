from __future__ import annotations

from collections import namedtuple
import copy
from dataclasses import dataclass
from dis import Bytecode, Instruction
import inspect
from typing import Generator, Protocol, Any
from abc import ABC
from dis import Positions

from advance_mc.query import EntityQueryMulti

from .._namespacing import ResourceLocation

from ..nbt.entity import Entity
from .mcfunc import McFunc

class Function(Protocol):
    __code__: Any
    __globals__: dict
    
class McIterable(ABC):
    pass

McIterable.register(Entity)

class CompilerError(SyntaxError):
    def __init__(self, message, func: Function, op: Instruction) -> None:
        self.file = file = inspect.getfile(func)
        self.positions: Positions|None = None
        
        # obtain source code to display exception location
        try:
            self.positions = positions = op.positions
            
            with open(file, 'r') as f:
                source_code = f.read().splitlines()[positions.lineno-1]
                
            underlining = ' ' * (positions.col_offset) + '^' * max(1, positions.end_col_offset - positions.col_offset)
            
        except (OSError, AttributeError):
            source_code = '<SOURCE CODE NOT OBTAINABLE>'
            underlining = ''
        
        # create full error message
        long_message = '\n'.join((
            f'Line {positions.lineno}, in file:',
            file,
            '',
            # show source code with underlined error
            source_code,
            underlining,
            '',
            
            message,
            '',
            ''
            
        ))
        
        super().__init__(long_message)


class McQuery(ABC):
    pass
McQuery.register(Entity)

@dataclass
class FunctionBlock:
    offset: int
    mcfunc: McFunc
    
    
    def resolve(self) -> McFunc:
        """Create an McFunc with jump points"""
        mcfunc = copy.deepcopy(self.mcfunc)
        
        if_true = self.jump_if_true is not None
        if_false = self.jump_if_false is not None
        if if_true or if_false:
            #mcfunc.commands.append(f'data modify storage {mcfunc.name} jump prepend value 1b')
            #TODO
            
            if if_true:
                path = "jump[0][{value:1b}]"
                mcfunc.commands.append(f'execute if data storage brandcraft:shit_dude {path} run function {self.jump_if_true.name}')
            if if_false:
                path = "jump[0][{value:1b}]"
            mcfunc.commands.append(f'data remove storage {mcfunc.name} jump[0]')

class Compiler:
    def __init__(self, func: Function, namespace_name:str) -> None:
        self.func = func
        self.name = ResourceLocation(namespace_name, self.func.__name__)
        
        self.code = Bytecode(func)
        self.globals = func.__globals__
        
        self.components = [FunctionBlock(offset=0, mcfunc=McFunc(self.name))]
        self.current_component_i = 0
        
        self.stack = []
        
    # def instructions(self) -> Generator[tuple[bytes, bytes]]:
    #     it = iter(self.code.co_code)
    #     while True:
    #         try:
    #             yield (next(it), next(it))
    #         except StopIteration:
    #             return
    
    @property
    def current_component(self) -> FunctionBlock:
        return self.components[self.current_component_i]
    @current_component.setter
    def current_component(self, val: FunctionBlock):
        for i, block in enumerate(self.components):
            if block.offset == val.offset:
                return i
    
    @property
    def tos(self):
        """Top of stack
        """
        return self.stack[-1]
    
    @tos.setter
    def tos(self, val):
        self.stack[-1] = val
    
    def get_iter(self):
        if isinstance(self.tos, MCIterable):
            ... # TODO
        else:
            self.tos = iter(self.tos)
            
    def error(self, msg: str, op: Instruction):
        raise CompilerError(msg, func=self.func, op=op)
        
    def cmd(self, command):
        """Adds a mcfunction command

        Args:
            command (str)
        """
        self.current_component.mcfunc.commands.append(command)
        
    def func_block_from_jump_offset(self, offset: int):
        for block in self.components:
            if block.offset == offset:
                return block
        
        # add new block if one does not already exist
        new_block = FunctionBlock(
            offset=offset,
            mcfunc=McFunc(
                name=ResourceLocation(
                    self.name.namespace_name,
                    # store it in the mcfunction namespace_name:func_name/offset
                    self.name.namespace_name + '/' + offset
                )
            )
        )
        self.components.append(new_block)
        return new_block
        
        
    def compile(self):
        stack = self.stack
                
        for op in self.code:
            
            # takes care of jump points, beginnings of loops, and recursion
            if op.is_jump_target:
                # create/get the next block
                new_block = self.func_block_from_jump_offset(op.offset)
                # jump to the next block(mcfunction file)
                self.cmd(f'function {new_block.mcfunc.name}')
                # update current block
                self.current_component = new_block
                
                
                
            match op:
                case Instruction(opname='RESUME'):
                    pass
                case Instruction(opname='NOP'):
                    pass
                case Instruction(opname='POP_TOP'):
                    stack.pop()
                case Instruction(opname='COPY', arg=i):
                    stack.append(stack[-i-1])
                case Instruction(opname='SWAP', arg=i):
                    stack[-i-1], stack[-1] = stack[-1], stack[-i-1]
                case Instruction(opname='UNARY_POSITIVE'):
                    stack[-1] = +stack[-1]
                case Instruction(opname='UNARY_NEGATIVE'):
                    stack[-1] = -stack[-1]
                case Instruction(opname='UNARY_NOT'):
                    stack[-1] = not stack[-1]
                # case Instruction(opname='UNARY_INVERT'):
                #     stack[-1] = ~ stack[-1]
                case Instruction(opname='GET_ITER'):
                    self.get_iter()
                case Instruction(opname='GET_YIELD_FROM_ITER'):
                    if not isinstance(stack[-1], Generator):
                        self.get_iter()
                case Instruction(opname='BEFORE_WITH'):
                    # TODO
                    ...
                # case Instruction(opname='GET_LEN') # TODO
                case Instruction(opname='STORE_NAME', arg=i):
                    self.use_storage = True
                    if isinstance(self.tos, EntityQueryMulti):
                        ... # TODO
                    elif isinstance(self.tos, NbtDataType):
                        ... # TODO
                        self.run(f'data modify storage brandcraft:shit_dude frames[0][0].{name} set value {wut}')
                
                case Instruction(opname='RETURN_VALUE'):
                    if self.tos is None:
                        ... # TODO
                case _:
                    self.error(f'The operation "{op.opname}" is not supported by this compiler. Please try different syntax.', op)
        
        if self.use_storage:
            # if the function uses variables, store them in frame objects.
            
            # create the frame at beginning
            v = "[{}]"
            self.components[0].mcfunc.commands.insert(
                0,
                f"data modify storage {self.name} frames prepend value {v}"
            )
            # remove the frame at ending
            self.components[0].mcfunc.commands.append(
                f"data remove storage {self.name} frames[0]"
            )
