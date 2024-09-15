from binaryninja import CallingConvention

class PowerVMCC(CallingConvention):
    name = "powervmcc"
    int_arg_regs = ["r1","r2","r3","r4"]
    int_return_reg = "r1"
