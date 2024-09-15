from binaryninja import (
    Architecture,
    Endianness,
    RegisterInfo,
    InstructionInfo,
    InstructionTextToken,
    InstructionTextTokenType,
    BranchType,
    InstructionBranch,
    IntrinsicInfo,
    Type,
    IntrinsicInput,
)
from .disas import PowerVMDisassembler
from .lifter import PowerVMLifter

def get_tokens_from_instr(instr):
    tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken,instr.mnem+" ")]
    if instr.arg1_type == 3:
        tokens.append(InstructionTextToken(InstructionTextTokenType.IntegerToken,hex(instr.arg1),instr.arg1))
    elif instr.arg1_type == 2:
        tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken,instr.reg1))
    else:
        tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken,instr.reg1))
        tokens.append(InstructionTextToken(InstructionTextTokenType.BeginMemoryOperandToken,"[")) 
        tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken,instr.reg2))
        tokens.append(InstructionTextToken(InstructionTextTokenType.EndMemoryOperandToken,"]"))

    if instr.arg_count == 2:
        tokens.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken,", "))
        if instr.arg2_type == 3:
            tokens.append(InstructionTextToken(InstructionTextTokenType.IntegerToken,hex(instr.arg2),instr.arg2))
        elif instr.arg2_type == 2:
            tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken,instr.reg3))
        else:
            tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken,instr.reg3))
            tokens.append(InstructionTextToken(InstructionTextTokenType.BeginMemoryOperandToken,"[")) 
            tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken,instr.reg4))
            tokens.append(InstructionTextToken(InstructionTextTokenType.EndMemoryOperandToken,"]"))
    return tokens


class PowerVMArch(Architecture):
    name = "powervm"
    endianness = Endianness.LittleEndian
    default_int_size = 4
    address_size = 4
    max_instr_size = 0x10
    

    regs = {}
    # regs['sp'] = RegisterInfo("sp",4)
    # regs['pc'] = RegisterInfo("pc",4)
    # regs['lr'] = RegisterInfo("lr",4)
    for x in range(0,13):
        reg_name = f"r{x}"
        regs[reg_name] = RegisterInfo(reg_name,4)
    regs['sp'] = RegisterInfo("r7",4)
    stack_pointer = "r7"

    intrinsics = {
        "open":IntrinsicInfo([
            IntrinsicInput(Type.pointer(Architecture['ppc'],Type.char()),"pathname"),
            IntrinsicInput(Type.int(4),"mode"),
            ],[Type.int(4)]),
        "strlen":IntrinsicInfo([
            IntrinsicInput(Type.pointer(Architecture['ppc'],Type.char()),"str"),
            ],[Type.int(4)]),
        "write":IntrinsicInfo([
            IntrinsicInput(Type.int(4),"fd"),
            IntrinsicInput(Type.pointer(Architecture['ppc'],Type.char()),"pathname"),
            IntrinsicInput(Type.int(4),"size"),
            ],[Type.int(4)]),
        "exit":IntrinsicInfo([],[]),
        "getdents":IntrinsicInfo([
             IntrinsicInput(Type.int(4),"fd"),
            IntrinsicInput(Type.pointer(Architecture['ppc'],Type.void()),"dirp"),
            IntrinsicInput(Type.int(4),"count"),
            ],[Type.int(4)]),
    }


    def __init__(self):
        super().__init__()
        self.disassembler = PowerVMDisassembler()
        self.lifter = PowerVMLifter(self.disassembler)
    
    def get_instruction_info(self,data,addr):
        instr, branch_info = self.disassembler.disasm(data,addr)
        instr_info = InstructionInfo(instr.length)
        #TODO:handle branch
        if branch_info.uncon_dest is not None:
            instr_info.add_branch(BranchType.UnconditionalBranch,branch_info.uncon_dest)
        if branch_info.true_dest is not None:
            instr_info.add_branch(BranchType.TrueBranch,branch_info.true_dest)
        if branch_info.false_dest is not None:
            instr_info.add_branch(BranchType.FalseBranch,branch_info.false_dest)
        if branch_info.syscall is not None:
            instr_info.add_branch(BranchType.SystemCall,branch_info.syscall)
        if branch_info.exit == True:
            instr_info.add_branch(BranchType.FunctionReturn)
        return instr_info
    
    def get_instruction_text(self,data,addr):
        instr, branch_info = self.disassembler.disasm(data,addr)
        tokens = get_tokens_from_instr(instr)
        return tokens, instr.length
  
    def get_instruction_low_level_il(self,data,addr,il):
        try:
            return self.lifter.lift(data,addr,il)
        except:
            return il.unimplemented()
        

