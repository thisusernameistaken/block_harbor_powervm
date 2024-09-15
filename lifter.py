from binaryninja import (
    LowLevelILFunction,
    LowLevelILLabel
)
class PowerVMLifter:
    
    def __init__(self,disassembler):
        self.disassembler = disassembler
        self.instructions = {
            0x0 : ['INC',self.inc],
            0x1 : ['DEC',self.dec],
            0x2 : ['IDK',self.unimpl],
            0x3 : ['STORE',self.unimpl],
            0x4 : ['STRLEN',self.strlen],
            0x5 : ['ADD',self.add],
            0x6 : ['ADD.b',self.add_b],
            0x7 : ['SUB',self.sub],
            0x8 : ['SUB.b',self.sub_b],
            0x9 : ['MUL',self.mul],
            0xa : ['XOR',self.xor],
            0xb : ['XOR.b',self.xor_b],
            0xc : ['LSH',self.lsh],
            0xd : ['RSH',self.rsh],
            0xe : ['ROL',self.rol],
            0xf : ['ROR',self.ror],
            0x10 : ['AND',self._and],
            0x11 : ['STORE.b',self.store_b],
            0x12 : ['MOVE',self.move],
            0x13 : ['LOAD',self.load],
            0x14: ['SYSCALL',self.syscall],
            0x15 : ['CALL',self.unimpl],
            0x16 : ['EXIT',self.exit],
            0x17 : ['CMP',self.cmp],
            0x18 : ['JE',self.je],
            0x19 : ['JNE',self.jne],
            0x1a : ["JMP",self.jmp],
        }

    def lift(self,data,addr,il):
        instr,b_info = self.disassembler.disasm(data,addr)
        mnem,func = self.instructions[instr.opcode]
        func(instr,addr,il,b_info)
        return instr.length
    
    def unimpl(self,instr,addr,il,b_info):
        il.append(il.unimplemented())

    def inc(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        inc_expr = il.add(4,dest_reg,il.const(4,1))
        il.append(il.set_reg(4,instr.reg1,inc_expr))

    def dec(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        dec_expr = il.sub(4,dest_reg,il.const(4,1))
        il.append(il.set_reg(4,instr.reg1,dec_expr))

    def move(self,instr,addr,il: LowLevelILFunction,b_info):
        if instr.arg2_type == 3:
            src = il.const(4,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        il.append(il.set_reg(4,instr.reg1,src))

    def xor(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        if instr.arg2_type == 3:
            src = il.const(4,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        xor_expr = il.xor_expr(4,dest_reg,src)
        il.append(il.set_reg(4,instr.reg1,xor_expr))

    def xor_b(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        if instr.arg2_type == 3:
            src = il.const(4,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        xor_expr = il.xor_expr(1,dest_reg,src)
        il.append(il.set_reg(4,instr.reg1,xor_expr))
    
    def add(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        if instr.arg2_type == 3:
            src = il.const(4,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        add_expr = il.add(4,dest_reg,src)
        il.append(il.set_reg(4,instr.reg1,add_expr))

    def rol(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        if instr.arg2_type == 3:
            src = il.const(4,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        add_expr = il.rotate_left(4,dest_reg,src)
        il.append(il.set_reg(4,instr.reg1,add_expr))

    def ror(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        if instr.arg2_type == 3:
            src = il.const(4,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        add_expr = il.rotate_right(4,dest_reg,src)
        il.append(il.set_reg(4,instr.reg1,add_expr))

    def _and(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        if instr.arg2_type == 3:
            src = il.const(4,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        add_expr = il.and_expr(4,dest_reg,src)
        il.append(il.set_reg(4,instr.reg1,add_expr))

    def mul(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        if instr.arg2_type == 3:
            src = il.const(4,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        add_expr = il.mult(4,dest_reg,src)
        il.append(il.set_reg(4,instr.reg1,add_expr))

    def add_b(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        if instr.arg2_type == 3:
            src = il.const(1,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        add_expr = il.add(1,dest_reg,src)
        il.append(il.set_reg(4,instr.reg1,add_expr))

    def sub(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        if instr.arg2_type == 3:
            src = il.const(4,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        sub_expr = il.sub(4,dest_reg,src)
        il.append(il.set_reg(4,instr.reg1,sub_expr))

    def sub_b(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        if instr.arg2_type == 3:
            src = il.const(1,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        sub_expr = il.sub(1,dest_reg,src)
        il.append(il.set_reg(4,instr.reg1,sub_expr))

    def store_b(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        index_reg = il.reg(4,instr.reg2)
        add_expr = il.add(4,dest_reg,index_reg)
        if instr.arg2_type == 3:
            src = il.const(1,instr.arg2)
        else:
            src = il.reg(1,instr.reg3)
        il.append(il.store(1,add_expr,src))

    def syscall(self,instr,addr,il: LowLevelILFunction,b_info):
        # il.append(il.system_call())
        if instr.arg1 == 5:
            il.append(il.intrinsic(["r1"],'open',[il.reg(4,"r1"),il.reg(4,"r2")]))
            # il.append(il.set_reg(4,'r1',il.reg(4,'r0')))
        elif instr.arg1 == 0x8d:
            il.append(il.intrinsic(["r1"],'getdents',[il.reg(4,"r1"),il.reg(4,"r2"),il.reg(4,"r3")]))
        elif instr.arg1 == 4:
            il.append(il.intrinsic(["r1"],'write',[il.reg(4,"r1"),il.reg(4,"r2"),il.reg(4,"r3")]))
        else:
            il.append(il.system_call())

    def load(self,instr,addr,il: LowLevelILFunction,b_info):
        src_reg = il.reg(4,instr.reg3)
        index_reg = il.reg(4,instr.reg4)
        add_expr = il.add(4,src_reg,index_reg)
        load_expr = il.load(4,add_expr)
        il.append(il.set_reg(4,instr.reg1,load_expr))

    def lsh(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        if instr.arg2_type == 3:
            src = il.const(4,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        add_expr = il.shift_left(4,dest_reg,src)
        il.append(il.set_reg(4,instr.reg1,add_expr))

    def rsh(self,instr,addr,il: LowLevelILFunction,b_info):
        dest_reg = il.reg(4,instr.reg1)
        if instr.arg2_type == 3:
            src = il.const(4,instr.arg2)
        else:
            src = il.reg(4,instr.reg3)
        add_expr = il.logical_shift_right(4,dest_reg,src)
        il.append(il.set_reg(4,instr.reg1,add_expr))

    def strlen(self,instr,addr,il: LowLevelILFunction,b_info):
        il.append(il.intrinsic(["r1"],'strlen',[il.reg(4,"r1")]))

    def cmp(self,instr,addr,il: LowLevelILFunction,b_info):
        reg = il.reg(4,instr.reg1)
        val = il.const(4,instr.arg2)
        il.append(il.set_reg(4,"r12",il.compare_equal(4,reg,val)))

    def je(self,instr,addr,il: LowLevelILFunction,b_info):
        target = il.const(4,b_info.true_dest)
        t = LowLevelILLabel()
        f = LowLevelILLabel()
        il.append(il.if_expr(il.reg(4,'r12'),t,f))
        il.mark_label(t)
        il.append(il.jump(target))
        il.mark_label(f)

    def jne(self,instr,addr,il: LowLevelILFunction,b_info):
        target = il.const(4,b_info.false_dest)
        t = LowLevelILLabel()
        f = LowLevelILLabel()
        il.append(il.if_expr(il.reg(4,'r12'),f,t))
        il.mark_label(t)
        il.append(il.jump(target))
        il.mark_label(f)

    def jmp(self,instr,addr,il: LowLevelILFunction,b_info):
        target = il.const(4,b_info.uncon_dest)
        il.append(il.jump(target))

    def exit(self,instr,addr,il: LowLevelILFunction,b_info):
        il.append(il.intrinsic([],"exit",[]))
        il.append(il.no_ret())