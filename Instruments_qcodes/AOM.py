import numpy as np
import qcodes as qc
from qcodes import Parameter, validators as vals, instrument
import GUI_lib as glib
import qslabcontrol.instruments.ni_daq.virtual_channels as virtual_channels
import nidaqmx


class AOM(instrument.Instrument):
    def __init__(
            self,
            config='Instruments/AOM.yaml'
    ):

        config=glib.localVariableDic(config)
        self.config=config
        name=config['name']
        min_val=config['Voltage']['min_value']
        max_val=config['Voltage']['max_value']
        self.unit=config['Voltage']['unit']
        port=config['NI_chan']

        super().__init__(name)

        physical_chan=nidaqmx.system.physical_channel.PhysicalChannel(port)
        self.voltage=virtual_channels.AoVoltageChannel(config['Voltage']['name'],physical_chan,instrument=self)

        val_AOM=vals.Numbers(glib.valueToBaseUnit(min_val,self.unit),glib.valueToBaseUnit(max_val,self.unit))
        self.voltage.vals=val_AOM #By default, the range is the max range of the NI card

    def set(self,value):
        self.voltage.set(glib.valueToBaseUnit(value,self.unit))

    def get(self):
        return glib.valueFromBaseUnit(self.voltage.get(),self.unit)
    
    def get_idn(self):
        return self.config['IDN']
    
class AOM_control_panel(glib.Graphical_interface):
    def __init__(self,
                 instrument: AOM,
                 designerFile='AOM_control_panel',
                 parent=None,
        ):
        super().__init__(designerFile=designerFile,parent=parent)
        self.instrument=instrument
        self.voltageField=glib.fieldParameter(parameter=self.instrument.voltage,
                                              config=self.instrument.config['Voltage'],
                                              labelDesignerWidget=self.VLabel,
                                              lineDesignerWidget=self.VLine)

if __name__ == "__main__":
    from pprint import pprint
    aom=AOM()
    station=qc.Station(aom)
    station.AOM.voltage(0.)
    pprint(station.snapshot())



        