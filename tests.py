import dis
from advance_mc.compiler.compiler import Compiler, CompilerError


def u_add():
    for i in range(10):
        
        print(i)
    
    
dis.dis(u_add)

c = u_add.__code__
print(c.co_consts, c.co_firstlineno, c.co_name, c.co_names, c.co_cellvars, c.co_freevars, c.co_varnames)

th = Compiler(u_add, 'th')
th.compile()

print(th)
