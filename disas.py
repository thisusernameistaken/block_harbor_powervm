import struct
import ctypes

class PowerInstruction:

    def __init__(self,data):
        self.data = data
        self.length = 1
        self.opcode = data[0]
        self.arg = None
        self.arg1 = None
        self.arg2 = None
        self.reg = None
        self.reg1 = ""
        self.reg2 = ""
        self.reg_off = None
        self.reg1_off = None
        self.reg2_off = None
        self.reg3_off = None
        self.reg4_off = None
        self.arg_type = None
        self.arg1_type = None
        self.arg2_type = None
        self.arg_size = None
        self.arg1_size = None
        self.arg2_size = None
        self.arg_count = None
        self.mnem = "UNKNOWN"
        
    def __str__(self):
        s = f'{self.mnem} '
        if self.arg1_type == 3:
            s += f"{hex(self.arg1)}"
        elif self.arg1_type == 2:
            s += self.reg1 
        else:
            s += self.reg1 + ", " + self.reg2 

        if self.arg_count == 2:
            if self.arg2_type == 3:
                s += f", {hex(self.arg2)}"
            elif self.arg2_type == 2:
                s += ", "+ self.reg2
            else:
                s += ", "+self.reg1 + ", " + self.reg2
        return s

class PVMBranchInfo:
    def __init__(self):
        self.uncon_dest = None
        self.true_dest = None
        self.false_dest = None
        self.syscall = None
        self.exit = None

class PowerVMDisassembler:

    def __init__(self):
        self.opcodes = {
            0x0 : ['INC',1],
            0x1 : ['DEC',1],
            0x2 : ['IDK',1],
            0x3 : ['STORE',1],
            0x4 : ['STRLEN',1],
            0x5 : ['ADD',2],
            0x6 : ['ADD.b',2],
            0x7 : ['SUB',2],
            0x8 : ['SUB.b',2],
            0x9 : ['MUL',2],
            0xa : ['XOR',2],
            0xb : ['XOR.b',2],
            0xc : ['LSH',2],
            0xd : ['RSH',2],
            0xe : ['ROL',2],
            0xf : ['ROR',2],
            0x10 : ['AND',2],
            0x11 : ['STORE.b',2],
            0x12 : ['MOVE',2],
            0x13 : ['LOAD',2],
            0x14: ['SYSCALL',1],
            0x15 : ['CALL',1],
            0x16 : ['EXIT',1],
            0x17 : ['CMP',2],
            0x18 : ['JE',1],
            0x19 : ['JNE',1],
            0x1a : ["JMP",1],
        }
        self.branch_ops = [0x18,0x19,0x1a]

    def decode_imm(self,instr):
        instr.arg_size = instr.data[instr.length]
        instr.length += 1
        if instr.arg_size == 4:
            instr.arg = struct.unpack(">I",instr.data[instr.length:instr.length+4])[0]
            instr.length += 4
        else:
            instr.arg = instr.data[instr.length]
            instr.length += 1
        return instr
    
    def decode_reg(self,instr):
        instr.reg_off = instr.data[instr.length]
        instr.length += 1
        instr.reg = f'r{instr.reg_off//4}'
        return instr
    
    def decode_one(self,instr):
        instr.arg1_type = instr.data[1]
        instr.length += 1
        if instr.arg1_type == 3: #IMM
            instr = self.decode_imm(instr)
            instr.arg1_size = instr.arg_size
            instr.arg1 = instr.arg
        elif instr.arg1_type == 2: #REG
            instr = self.decode_reg(instr)
            instr.reg1_off = instr.reg_off
            instr.reg1 = instr.reg
        else: #memory operation
            instr = self.decode_reg(instr)
            instr.reg1_off = instr.reg_off
            instr.reg1 = instr.reg
            instr = self.decode_reg(instr)
            instr.reg2_off = instr.reg_off
            instr.reg2 = instr.reg
        return instr

    def decode_two(self,instr):
        instr.arg1_type = instr.data[1]
        instr.length += 1
        if instr.arg1_type == 3: #IMM
            instr = self.decode_imm(instr)
            instr.arg1_size = instr.arg_size
            instr.arg1 = instr.arg
        elif instr.arg1_type == 2: #REG
            instr = self.decode_reg(instr)
            instr.reg1_off = instr.reg_off
            instr.reg1 = instr.reg
        else: #memory operation
            instr = self.decode_reg(instr)
            instr.reg1_off = instr.reg_off
            instr.reg1 = instr.reg
            instr = self.decode_reg(instr)
            instr.reg2_off = instr.reg_off
            instr.reg2 = instr.reg
        instr.arg2_type = instr.data[instr.length]
        instr.length += 1
        if instr.arg2_type == 3: #IMM
            instr = self.decode_imm(instr)
            instr.arg2_size = instr.arg_size
            instr.arg2 = instr.arg
        elif instr.arg2_type == 2: #REG
            instr = self.decode_reg(instr)
            instr.reg3_off = instr.reg_off
            instr.reg3 = instr.reg
        else: #idk yet
            instr = self.decode_reg(instr)
            instr.reg3_off = instr.reg_off
            instr.reg3 = instr.reg
            instr = self.decode_reg(instr)
            instr.reg4_off = instr.reg_off
            instr.reg4 = instr.reg

        return instr

    def disasm(self,b,addr):
        instr = PowerInstruction(b)
        if instr.opcode not in self.opcodes:
            return instr, PVMBranchInfo()
        mnemonic, arg_count = self.opcodes[instr.opcode]
        if instr.opcode == 0x16:
            instr.mnem = mnemonic
            b_info = PVMBranchInfo()
            instr.exit = True
            return instr,b_info
        instr.arg_count = arg_count
        instr.mnem = mnemonic
        if arg_count == 1:
            instr = self.decode_one(instr)
        else:
            instr = self.decode_two(instr)

        # branching
        b_info = PVMBranchInfo()
        if instr.opcode == 0x1a: #jmp
            instr.arg1+=instr.length+addr
            instr.arg1 = ctypes.c_int32(instr.arg1).value
            b_info.uncon_dest = instr.arg1
        elif instr.opcode == 0x18: #je
            instr.arg1+=instr.length+addr
            instr.arg1 = ctypes.c_int32(instr.arg1).value
            b_info.true_dest = instr.arg1
            b_info.false_dest = addr+instr.length
        elif instr.opcode == 0x19: #jne
            instr.arg1+=instr.length+addr
            instr.arg1 = ctypes.c_int32(instr.arg1).value
            b_info.false_dest = instr.arg1
            b_info.true_dest = addr+instr.length
        elif instr.opcode == 0x14:
            b_info.syscall = instr.arg1
        
        return instr,b_info
