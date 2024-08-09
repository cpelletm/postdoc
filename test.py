import os
import sys
import json
import yaml
import pyqtgraph as pg
import numpy as np
import matplotlib.pyplot as plt
import qcodes as qc
# import nidaqmx 
# from nidaqmx.system.system import System
import GUI_lib as glib

def jsonwrite(): 
    fname=os.path.join(os.path.dirname(__file__),'GUI config files','test_config.json')
    d={}
    d['data large symbol brush']=None
    d["truc faux"]=False


    with open(fname,'w') as f:
        json.dump(d,f,indent=2)

def jsonread():
    fname=os.path.join(os.path.dirname(__file__),'GUI config files','style sheet.json')
    with open(fname,'r') as f:
        d1=json.load(f)
    print(d1)

def test_pg():
    x = np.random.normal(size=1000)
    y = np.random.normal(size=1000)
    pg.plot(x, y, pen=None, symbol='o')
    pg.QtGui.QGuiApplication.exec_()

def pg_example():
    import pyqtgraph.examples
    pyqtgraph.examples.run()

def test_func_args(x=1,y=2):
    print(x,y)

def test_local_file():
    import GUI_lib
    GUI_lib.localVariableDic('style sheet.json')


def terminals_nidaq():

    daq_sys=System.local()
    print(daq_sys.devices.device_names)
    for device in daq_sys.devices:
        print("Ni card name :",device._name)
        print("Ni card product type :",device.product_type)
        print("NI card terminals :",device.terminals)
        print("\n \n")

# terminals_nidaq()

def test_env_variables():
    import os
    print(os.environ['test_path'])
    #check if the file exists
    if os.path.isfile(os.environ['test_path']):
        print("File exists")
    else:
        print("File does not exist")

def test_ni_daq():
    import nidaqmx
    import qslabcontrol.instruments.ni_daq.virtual_channels as virtual_channels
    daq_sys=nidaqmx.system.System.local()
    chanDic=glib.localVariableDic('ni_daq_physical_chan_conversion.yaml')
    ai_physicalChan=daq_sys.devices[0].ai_physical_chans[0]
    ai_physicalChan=nidaqmx.system.physical_channel.PhysicalChannel('PXI1Slot4/ai0') #Both works, but the second one is easier
    tipVx=virtual_channels.AiVoltageChannel('tipVx', ai_physicalChan)
    print(tipVx.get())

# test_ni_daq()

def make_ni_conversion_sheet(fname=r'D:\Clement python dev\postdoc\Config files\ni_daq_physical_chan_conversion.json'):
    daq_sys=nidaqmx.system.System.local()
    
    d={}
    d["ai_chans"]={}
    d["ao_chans"]={}
    d["ci_chans"]={}
    d["co_chans"]={}
    d["di_chans"]={}
    d["do_chans"]={}
    for i in range(len(daq_sys.devices)):
        device=daq_sys.devices[i]
        for j in range(len(device.ai_physical_chans)):
            ai_chan=device.ai_physical_chans[j]
            d["ai_chans"][ai_chan.name]={"device_no":i,"chan_no":j}
        for j in range(len(device.ao_physical_chans)):
            ao_chan=device.ao_physical_chans[j]
            d["ao_chans"][ao_chan.name]={"device_no":i,"chan_no":j}
        for j in range(len(device.ci_physical_chans)):
            ci_chan=device.ci_physical_chans[j]
            d["ci_chans"][ci_chan.name]={"device_no":i,"chan_no":j}
        for j in range(len(device.co_physical_chans)):
            co_chan=device.co_physical_chans[j]
            d["co_chans"][co_chan.name]={"device_no":i,"chan_no":j}
        for j in range(len(device.di_lines)):
            di_chan=device.di_lines[j]
            d["di_chans"][di_chan.name]={"device_no":i,"chan_no":j}
        for j in range(len(device.do_lines)):
            do_chan=device.do_lines[j]
            d["do_chans"][do_chan.name]={"device_no":i,"chan_no":j}
        
    with open(fname,'w') as f:
        json.dump(d,f,indent=2)

def test_yaml_write():
    import yaml
    d={}
    d['test']=1

    yaml.dump(d,open(r'D:\Clement python dev\postdoc\Config files\test_YAML.yaml','w'))

def convert_json_to_yaml(fname_json):
    yaml_file=fname_json.replace('.json','.yaml')
    with open(fname_json,'r') as f:
        d=json.load(f)
    with open(yaml_file,'w') as f:
        yaml.dump(d,f,indent=2)


def test_save_csv():
    import csv
    x=np.array([1,2,3,4,5,6,7,8])
    y=x**2
    fname='Test file.csv'
    with open (fname,'a') as f:
        writer=csv.writer(f,delimiter=',',lineterminator='\n',quoting=csv.QUOTE_NONNUMERIC)
        x=['x']+list(x)
        y=['y']+list(y)
        writer.writerow(x)
        writer.writerow(y)      
# test_save_csv()

def test_read_csv():
    import csv
    fname='Test file.csv'
    with open (fname,'r') as f:
        reader=csv.reader(f,delimiter=',',lineterminator='\n',quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            print(row)
# test_read_csv()

def test_property():
    class testClass:
        def __init__(self):
            self.prop=1
        @property
        def prop(self):
            return self._prop
        @prop.setter
        def prop(self,value):
            print('setter 1')
            self._prop=value

        @prop.setter
        def prop(self,value):
            print('setter 2')
            self._prop=value
    t=testClass()
    print(t.prop)
    t.prop=2
    print(t.prop)

def square(x):
    return x**2

def callFunction(func):
    return func()

def Jodok_carbon_guessing_game():
    kWhToJ=3600000
    sToMin=60
    sToH=3600
    sToDay=24*3600

    compressorPower=10000 #W
    switzerlandPowerToCo2=0.05/kWhToJ #kg/J
    compressorCo2Rate=compressorPower*switzerlandPowerToCo2 #kg/s

    LasVegasRoundTripCo2=3000 #kg

    veggieFoodCo2=2.5 #kg Co2/kg food
    beefFoodCo2=60 #kg Co2/kg food

    LargeVeggiePortionCo2=0.5*veggieFoodCo2 #kg Co2
    SmallBeefPortionCo2=0.05*beefFoodCo2+0.2*veggieFoodCo2 #kg Co2

    elevatorEnergy=50000 #J (Standars size elevator from ground floor to 3rd floor)
    elevatorCo2=elevatorEnergy*switzerlandPowerToCo2 #kg Co2

    trainEnergy = 400 #J/m/passenger
    BaselZurichDistance=80e3 #m
    BselZurichCommuteCo2=BaselZurichDistance*trainEnergy*switzerlandPowerToCo2*2 #kg Co2 (*2 for round trip)

    boatDeliveryCo2=30e-6 #kg Co2/kg package/km
    truckDeliveryCo2=210e-6 #kg Co2/kg package/km
    ShangaiRotterdamDistance=22000 #km
    BaselRotterdamDistance=680 #km
    packageWieght=1 #kg
    AliBabaPackageDeliveryCo2=boatDeliveryCo2*ShangaiRotterdamDistance*packageWieght+truckDeliveryCo2*BaselRotterdamDistance*packageWieght #kg Co2

    bitCoin2022Co2=77e9 #kg Co2/year
    bitcoin2022Transactions=300000*365 #transactions/year
    bitcoinTransactionCo2=bitCoin2022Co2/bitcoin2022Transactions #kg Co2/transaction

    humanBreathingOneDayCo2=0.9 #kg Co2/day

    co2Dic={}
    co2Dic['compressor one day']=compressorCo2Rate*sToDay
    co2Dic['Las Vegas round trip']=LasVegasRoundTripCo2
    co2Dic['large veggie portion']=LargeVeggiePortionCo2
    co2Dic['small beef portion']=SmallBeefPortionCo2
    co2Dic['elevator']=elevatorCo2
    co2Dic['Basel Zurich commute']=BselZurichCommuteCo2
    co2Dic['Ali Baba package delivery']=AliBabaPackageDeliveryCo2
    co2Dic['bitcoin transaction']=bitcoinTransactionCo2
    co2Dic['human breathing one day']=humanBreathingOneDayCo2

    def sToDHMS(t):
        days=int(t/sToDay)
        hours=int((t-days*sToDay)/sToH)
        minutes=int((t-days*sToDay-hours*sToH)/sToMin)
        seconds=int(t-days*sToDay-hours*sToH-minutes*sToMin)
        return days,hours,minutes,seconds

    for key in co2Dic.keys():
        print(key+':')
        print("kg Co2 : %.2e"%(co2Dic[key]))
        days,hours,minutes,seconds=sToDHMS(co2Dic[key]/compressorCo2Rate)
        print("Equivalent compressor time : %.2f days, %.2f hours, %.2f minutes, %.2f seconds"%(days,hours,minutes,seconds))
        print('\n')


def test_qc_station():
    import nidaqmx
    import qslabcontrol.instruments.ni_daq.virtual_channels as virtual_channels
    station=qc.Station()
    AOM=virtual_channels.AoVoltageChannel('AOM',nidaqmx.system.physical_channel.PhysicalChannel('PXI1Slot5/ao6'))
    station.add_component(AOM)
    station.AOM.set(0.)
    print(station.snapshot())
# test_qc_station()

def securite_routiere():
    L=30000
    Vs=np.linspace(0,250,1000)
    Vs_mps=Vs*1000/3600
    Delta_V_mps=10*1000/3600
    Delta_T=L/Vs_mps-L/(Vs_mps+Delta_V_mps)
    plt.plot(Vs,Delta_T)
    plt.plot(Vs,30*np.ones(len(Vs)))
    plt.xlabel('Vitesse (km/h)')
    plt.ylabel('Temps gagné (s)')
    plt.title('Temps gagné en fonction de la vitesse')
    plt.ylim(0,200)
    plt.show()
# securite_routiere()


