from .arch import PowerVMArch
from .plat import PowerVMPlatform
from .callingconvention import PowerVMCC
from binaryninja import Architecture

arch = PowerVMArch()
arch.register()
a = Architecture['powervm']
cc = PowerVMCC(Architecture['powervm'],"powervm_cc")
Architecture['powervm'].register_calling_convention(cc)
platform = PowerVMPlatform(a)
platform.register("powervm")
