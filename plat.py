from binaryninja import (
    Architecture,
    Platform
)
from .callingconvention import PowerVMCC

class PowerVMPlatform(Platform):
    name = "powervm"
    
    system_calls = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
    ]


    def __init__(self, arch: Architecture | None = None, handle=None):
        super().__init__(arch, handle)
        self.add_related_platform(Architecture['ppc'],Platform['ppc'])
        self.default_calling_convention = PowerVMCC(Architecture['powervm'],"powervm_cc")