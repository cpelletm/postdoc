import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ctypes import c_byte, c_uint, POINTER, WinDLL
from ctypes.wintypes import HANDLE
import numpy as np
import qcodes as qc
from qcodes import Parameter, validators as vals, instrument
import GUI_lib as glib

class Meadowlark_D5020(instrument.Instrument):
    def __init__(
            self,
            config='Instruments/Meadowlark_D5020.yaml'
    ):

        ############# Config File part
        config=glib.localVariableDic(config)
        self.config=config
        name=config['name']
        min_val=config['Voltage']['min_value']
        max_val=config['Voltage']['max_value']
        self.unit=config['Voltage']['unit']
        self.working_unit='mV' #The D5020 works in mV
        self.port=config['port']
        if self.port=='both':
            raise ValueError("Not implemented yet. Please choose a port.")
        self._V=config['Voltage']['default_value']
        super().__init__(name)


        self.voltage=Parameter(
            name=name,
            label="Voltage",
            instrument=self,
            unit=self.unit,
            get_cmd=self.get_voltage,
            set_cmd=self.set_voltage,
            vals=vals.Numbers(min_val,max_val)
        )

        ############# dll part
        usbdrvdpath = os.path.dirname(__file__) + r"\usbdrvd_Meadowlark" #Find usbdrvd.dll at path of this example file.
        self.lib = WinDLL(usbdrvdpath) #Load the DLL.
        #Set up return and argument defines for DLL Functions
        self.lib.USBDRVD_OpenDevice.restype = HANDLE
        self.lib.USBDRVD_InterruptWrite.argtypes = [HANDLE, c_uint, POINTER(c_byte), c_uint]
        self.lib.USBDRVD_InterruptRead.argtypes = [HANDLE, c_uint, POINTER(c_byte), c_uint]
        self.lib.USBDRVD_CloseDevice.argtypes = [HANDLE]
        
        #Device variables
        self.usb_pid = c_uint(5020) #Device PID for D5020
        self.numdevices = c_uint(0)
        self.devhandle = HANDLE()
        self.flagsandattrs = c_uint(1073741824)
        self.devnumber = c_uint(1) #If several devices are connected you should change this line
        self.writepipe = c_uint(1)
        self.readpipe = c_uint(0)
        self.bytecount = c_uint(0)

        #command variables
        usbbuffer = c_byte * 64 #controller response buffer definition
        self.cmdstatus = usbbuffer() #variable to hold controller response
        self.bufferlen = c_uint(64) #buffer size variable, set to default size of butter
        self.cmdresponsestr = "" #Blank command response string variable.

        self.find_devices()
        self.connected=False

    def makecmd (self,cmdstr):
    #This function converts a command string to a byte array and adds the carriage return character to the end.
        cmdlen = len(cmdstr) + 1 #set up length
        cmdarr = c_byte * cmdlen #and command byte array
        cmdtosend = cmdarr()
        chartmp = 0  #temp char variable
        for x in range(cmdlen - 1):#go through command string
            chartmp = ord(cmdstr[x]) #and get current character and convert to byte
            cmdtosend[x] = chartmp #then put it as the current character in the array.
        cmdtosend[cmdlen-1] = 13 #add CR
        return (cmdtosend,cmdlen) #return the command array and length.   
    
    def buffer2str (self):
        #This function converts a char array to a string, finishing when it sees a carriage return.
        responsestr = "" #make empty string
        for x in range (64): #Go through response buffer.
            if self.cmdstatus[x] == 13: #if found carriage return
                break #function is done
            responsestr = responsestr + chr(self.cmdstatus[x]) #otherwise add current character to string.
        return responsestr #return the response string

    def find_devices(self):
        self.numdevices = self.lib.USBDRVD_GetDevCount(self.usb_pid)
        if(self.numdevices == 0):
            return False
        elif(self.numdevices == 1):
            return True
        else:
            raise ValueError("More than one device found. This is not supported.")

    def connect(self):
        if self.numdevices == 0:
            if self.find_devices():
                pass
            else:
                raise ValueError("No devices found.")

        self.devhandle = self.lib.USBDRVD_OpenDevice(self.devnumber,self.flagsandattrs,self.usb_pid)
        self.connected=True

    def disconnect(self):
        if self.connected:
            self.lib.USBDRVD_CloseDevice(self.devhandle)
            self.connected=False

    def _write_and_read(self,cmdstr):
        (cmdtosend,cmdlen) = self.makecmd(cmdstr)
        cmdptr = (c_byte * len(cmdtosend))(*cmdtosend)
        self.lib.USBDRVD_InterruptWrite(self.devhandle,self.writepipe,cmdptr,cmdlen) #Send command
        self.lib.USBDRVD_InterruptRead(self.devhandle,self.readpipe,self.cmdstatus,self.bufferlen) #Read buffer
        return self.buffer2str()
    
    def generic_command(self,command):
        try :
            self.connect()
            print("Connected, new command : ",command)
            response=self._write_and_read(command)
            time.sleep(0.1)
        except Exception as e:
            response=str(e)
            print(response)
        finally:
            self.disconnect()
        return response


    def set_voltage(self,value):
        val_mV=int(glib.conversion_unit(value,self.unit,self.working_unit))
        command="inv:%i,%i"%(self.port,val_mV)
        print(self.generic_command(command))
        self._V=value

    def get_voltage(self):
        return self._V
    
    def get_idn(self):
        SN=self.generic_command("rsn:?")
        ver=self.generic_command("ver:?")
        return {'serial number':SN,'firmware version':ver}

    def make_control_panel(self):
        return Meadowlark_D5020_control_panel(self)

class Meadowlark_D5020_control_panel(glib.Graphical_interface):
    def __init__(self,
                 instrument: Meadowlark_D5020,
                 designerFile='Meadowlark_D5020_control_panel',
                 parent=None,
        ):
        super().__init__(designerFile=designerFile,parent=parent)
        self.instrument=instrument
        self.voltageField=glib.fieldParameter(parameter=self.instrument.voltage,
                                              config=self.instrument.config['Voltage'],
                                              labelDesignerWidget=self.VLabel,
                                              lineDesignerWidget=self.VLine)

if __name__ == "__main__":
    d5020=Meadowlark_D5020()
    print(d5020.get_idn())
    cp=d5020.make_control_panel()
    cp.run()
