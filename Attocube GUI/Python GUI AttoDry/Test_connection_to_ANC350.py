from qcodes_contrib_drivers.drivers.Attocube.ANC350 import ANC350
from qcodes_contrib_drivers.drivers.Attocube.ANC350Lib.v4 import ANC350v4Lib
import ctypes
import struct
import os


fileFolder=os.path.dirname(os.path.abspath(__file__))
# pathToDll=fileFolder+'\\ANC350_Python_Control-master\\ANC350\\win64\\anc350v4.dll'  #DLL files found on https://github.com/attocube-systems/ANC350_Python_Control
pathToDll=fileFolder+'\\anc350v4.dll'

  
dummyDll=ctypes.windll.LoadLibrary(pathToDll)
lib=ANC350v4Lib(path_to_dll=pathToDll)

print(lib.discover(search_usb=True, search_tcp=False))
# print(lib.get_device_info(dev_no=0))
# print(lib.get_device_info(dev_no=1))
handle_0=lib.connect(dev_no=0)
print(lib.get_actuator_type(dev_handle=handle_0, axis_no=2))
print(lib.get_actuator_name(dev_handle=handle_0, axis_no=0))
print(lib.get_position(dev_handle=handle_0, axis_no=0)*1e6)
# print(dir(lib))

# ANC=ANC350(name='ANCDry', library=lib)
