from binaryninja import load
from z3 import *
import struct

def solve_bytes(rol_value1,add_value1,add_value2,rol_value2,cmp_value):
    solver = Solver()
    r6 = BitVec('r6', 32) 
    
    r6_after_rol1 = RotateLeft(r6, rol_value1 & 0x1F)  
    r6_after_add1 = r6_after_rol1 + add_value1
    r6_after_add2 = r6_after_add1 + add_value2
    r6_after_rol2 = RotateLeft(r6_after_add2, rol_value2 & 0x1F)

    solver.add(r6_after_rol2 == cmp_value)

    if solver.check() == sat:

        model = solver.model()
        r6_value = model[r6].as_long()
        return r6_value
    else:
        print("No solution found")
        exit()


flag_png_bytes = b""
total_len=0x61a80
bv = load("power/code.power.bndb")

def apply_operation(r6, operation, operand):
    if operation == "ROL":
        return RotateLeft(r6, operand & 0x1F)
    elif operation == "ADD":
        return r6 + operand
    elif operation == "CMP":
        return r6 == operand
    elif operation == "MUL":
        return r6*operand
    elif operation == "SUB":
        return r6-operand
    elif operation == "XOR":
        return r6^operand
    elif operation == "ROR":
        return RotateRight(r6, operand & 0x1F)
    else:
        raise ValueError(f"Unsupported operation: {operation}")


def solve_block(addr):
    bb = bv.get_basic_blocks_at(addr)[0]
    solver = Solver()
    r6_value = None
    r6 = BitVec('r6', 32)
    for x in range(-6,-1,1):
        
        operation = str(bb.disassembly_text[x].tokens[1]).strip()
        operand = bb.disassembly_text[x].tokens[-1].value
        # print(operation,hex(operand))
        if operation == "CMP":
            solver.add(apply_operation(r6, operation, operand))
        else:
            r6 = apply_operation(r6, operation, operand)
    
    if solver.check() == sat:
        model = solver.model()
        # __import__("IPython").embed()
        r6_value =int(str(model)[6:-1])
    else:
        print("No solution found")

    next_addr = bb.outgoing_edges[0].target.start
    return next_addr,r6_value

addr = 0x342

while len(flag_png_bytes)<total_len:
    try:
        addr,val = solve_block(addr)
        flag_png_bytes += struct.pack(">I",val)
        # print(len(flag_png_bytes))
    except:
        __import__("IPython").embed()
    # print(flag_png_bytes)
__import__("IPython").embed()