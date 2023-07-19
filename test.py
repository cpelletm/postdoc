import os
import sys
import json
import pyqtgraph as pg
import numpy as np

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

print([0,15] is None)
