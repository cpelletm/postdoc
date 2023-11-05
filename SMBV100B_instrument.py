from typing import Any

import numpy as np
import qcodes as qc
from qcodes import Parameter, validators as vals
from qcodes.instrument.base import InstrumentBase
from qcodes.instrument.instrument_base import InstrumentBase
from qcodes.utils.helpers import create_on_off_val_mapping
from qcodes.instrument import (
    ParameterWithSetpoints,
    Instrument,
    VisaInstrument,
    InstrumentChannel,
    InstrumentModule,
)

class RS_SMBV100B(VisaInstrument):
    """
    This is the based on the QCoDeS driver for the Rohde & Schwarz SMB100A signal generator.

    """

    def __init__(self, name: str, address: str, **kwargs: Any) -> None:
        super().__init__(name, address, terminator="\n", **kwargs)

        self.frequency = Parameter(
            name="frequency",
            instrument=self,
            label="Frequency",
            unit="Hz",
            get_cmd="SOUR:FREQ?",
            set_cmd="SOUR:FREQ {:.2f}",
            get_parser=float,
            vals=vals.Numbers(100e3, 12.75e9),
        )

        self.frequency_mode = Parameter(
            name="frequency_mode",
            instrument=self,
            label="Mode",
            get_cmd="FREQ:MODE?",
            set_cmd="FREQ:MODE {}",
            vals=vals.Enum("CW", "FIX", "SWE", "LIST"),
        )

        self.phase = Parameter(
            name="phase",
            instrument=self,
            label="Phase",
            unit="deg",
            get_cmd="SOUR:PHAS?",
            set_cmd="SOUR:PHAS {:.2f}",
            get_parser=float,
            vals=vals.Numbers(0, 360),
        )

        self.power = Parameter(
            name="power",
            instrument=self,
            label="Power",
            unit="dBm",
            get_cmd="SOUR:POW?",
            set_cmd="SOUR:POW {:.2f}",
            get_parser=float,
            vals=vals.Numbers(-120, 25),
        )

        self.power_mode = Parameter(
            name="power_mode",
            instrument=self,
            label="Mode",
            get_cmd="POW:MODE?",
            set_cmd="POW:MODE {}",
            vals=vals.Enum("CW", "FIX", "SWE", "LIST"),
        )

        self.status = Parameter(
            name="status",
            instrument=self,
            label="RF Output",
            get_cmd=":OUTP?",
            set_cmd=":OUTP {}",
            val_mapping=create_on_off_val_mapping(on_val="1", off_val="0"),
        )

        self.displayUpdate = Parameter(
            name="displayUpdate",
            instrument=self,
            label="Display frequencies (sweep mode)",
            get_cmd="SYST:DISP:UPD?",
            set_cmd="SYST:DISP:UPD {}",
            val_mapping=create_on_off_val_mapping(on_val="1", off_val="0"),
        ) 

        self.sweepTrigger = Parameter(
            name="trigger",
            instrument=self,
            label="Frequency Sweep Trigger",
            get_cmd=":TRIG:FSW:SOUR?",
            set_cmd=":TRIG:FSW:SOUR {}",
            vals=vals.Enum("AUTO", "IMM", "SING", "BUS", "EXT", "EAUT"),
        )

        self.sweepSpan = Parameter(
            name="span",
            instrument=self,
            label="Frequency Sweep Span",
            unit="Hz",
            get_cmd=":FREQ:SPAN?",
            set_cmd=":FREQ:SPAN {}",
            get_parser=float,
            vals=vals.Numbers(0, 12.75e9),
        )


        self.connect_message()

    def on(self) -> None:
        self.status("ON")

    def off(self) -> None:
        self.status("OFF")

    def cw(self) -> None:
        """Sets power and frequency to CW mode."""
        self.frequency_mode.set("CW")
        self.power_mode.set("CW")

    def reset(self) -> None:
        self.write("*RST")

    def clear(self) -> None:
        self.write("*CLS")

    def run_self_tests(self) -> None:
        self.ask("*TST?")

    def send_trigger(self) -> None:
        self.write("*TRG")

    def set_sweep(self, start, stop, num_points, spacing, shape):
        pass

    def get_errors(self, raise_err: bool = True):
        error_str = self.ask(":SYST:ERR:ALL?")
        if raise_err and error_str != '0,"No error"':
            raise RuntimeError(error_str)
        else:
            return error_str



if __name__ == "__main__":
    station = qc.Station()
    mw=RS_SMBV100B(name='mw1',address='TCPIP0::192.168.1.52::inst0::INSTR')
    station.add_component(mw)
    print(mw.frequency())
    mw.frequency(2e9)
    print(mw.frequency())
    print(mw.status())


