import os
import sys
import json

def jsonwrite():
    
    fname=os.path.join(os.path.dirname(__file__),'GUI config files','style sheet.json')
    d={}
    d['lightPenColors']=[(31, 119, 180),(255, 127, 14),(44, 160, 44),(214, 39, 40),(148, 103, 189),(140, 86, 75),(227, 119, 194),(127, 127, 127),(188, 189, 34),(23, 190, 207)]
    d['darkPenColors']=[(255, 127, 14),(31, 119, 180),(44, 160, 44),(214, 39, 40),(148, 103, 189),(140, 86, 75),(227, 119, 194),(127, 127, 127),(188, 189, 34),(23, 190, 207)] 
    d['lightInfiniteLineColor']=(100,100,100)
    d['darkInfiniteLineColor']=(255,255,255)


    with open(fname,'w') as f:
        json.dump(d,f,indent=2)

jsonwrite()

def jsonread():
    fname=os.path.join(os.path.dirname(__file__),'GUI config files','style sheet.json')
    with open(fname,'r') as f:
        d1=json.load(f)
    print(d1)


