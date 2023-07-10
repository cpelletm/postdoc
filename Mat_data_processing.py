from scipy import io
import sys
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import analyse

exampleFolder=os.path.dirname(__file__)+'/Matlab example file'
fileESR=exampleFolder+'/Example ESR.mat'
fileESR1ctr=exampleFolder+'/Example ESR 1 ctr.mat'
fileScan=exampleFolder+'/Example scan.mat'
filePLtrace=exampleFolder+'/Example time trace charac.mat'
fileRFscan=exampleFolder+'/Example RF scan.mat'
fileFeedback=exampleFolder+'/Example feedback.mat'
fileScanFeedback=exampleFolder+'/Example scan feedback'

def headers(obj):
    return(list(obj.dtype.fields.keys()))

def showContent(item):
    head=headers(item)
    for h in head :
        try :
            print(h,':',item[h].item(0))
        except :
            print(h, 'Could not show content')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

class matFile():
    def __init__(self,pathToFile) -> None:
        self.matDic=io.loadmat(pathToFile,squeeze_me=True)
        self.matKeys=list(self.matDic.keys())
        self.path=os.path.abspath(pathToFile)
        self.folder=os.path.dirname(pathToFile)
        self.fileName=os.path.basename(pathToFile)
    def date(self,year=True,month=True,day=True,hour=True,minute=True,seconds=False) -> str:
        date=''
        monthDir={'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
        matDate=str(self.matDic['__header__']).split('Created on: ')[1][:-1].split()
        y=matDate[4]
        mo=monthDir[matDate[1]]
        d=matDate[2]
        h=matDate[3].split(':')[0]
        mi=matDate[3].split(':')[1]
        s=matDate[3].split(':')[2]
        if year :
            date+='_'+y
        if month :
            date+='_'+mo
        if day :
            date+='_'+d
        if hour :
            date+='_'+h
        if minute :
            date+='_'+mi
        if seconds :
            date+='_'+s
        return date[1:]

class NVAFM_ESR_matFile(matFile):
    keys=['__header__', '__version__', '__globals__', 'smNVesr', '__function_workspace__']
    def __init__(self, pathToFile) -> None:
        super().__init__(pathToFile)
        assert self.keys==self.matKeys, 'Wrong file (%s) for the class (%s)'%(self.matKeys[3],self.keys[3])
        
        self.sm=self.matDic['smNVesr']
        smkeys=['Status', 'InChannel', 'DAQ', 'Inst', 'Fields', 'AuxInfo']

        self.Inchan=self.sm['InChannel'].item()
        InchanKeys=['Name', 'InstName', 'SweepType', 'SweepVals', 'Data', 'DataSquared', 'CW', 'bPlot']

        self.CW=self.Inchan['CW'][0]
        CWkeys=['Freq', 'Power', 'State']

        self.Aux=self.sm['AuxInfo'].item()
        AuxKeys=['EmptyInChannelStr', 'EmptyDAQStr', 'FigureInd', 'RegChanFigN', 'InstStruct', 'RFStateColors', 'DisableGUIElems', 'Fitpos', 'FitFWHM', 'Fitcontrast', 'FitStruct', 'FitSNR', 'FitResults', 'textLocX', 'textLocY']

    def ctr1(self):
        return (self.Inchan['Data'][0])
    def ctr2(self):
        return (self.Inchan['Data'][1])
    def freqs(self):
        return(self.Inchan['SweepVals'][0])
    def power(self):
        return(self.CW['Power'])
    def fitParams(self): #center,width, contrast (GHz,GHz,%)
        return(self.Aux['Fitpos'].item(),self.Aux['FitFWHM'].item(),self.Aux['Fitcontrast'].item())

class NVAFM_scan_matFile(matFile):
    keys=['__header__', '__version__', '__globals__', 'smNVscan', '__function_workspace__']
    def __init__(self, pathToFile) -> None:
        super().__init__(pathToFile)
        self.sm=self.matDic[self.matKeys[3]]
        self.scdata=self.sm['Scanner'].item()['ScanCreate'].item(0)['scData'].item()['Fields'].item()
        scdatakeys=['ed_xmin', 'ed_xmax', 'ed_nx', 'cb_bFixX', 'ed_ymin', 'ed_ymax', 'ed_ny', 'cb_bFixY', 'ed_zmin', 'ed_zmax', 'ed_nz', 'cb_bFixZ', 'ed_loopOrder', 'ed_theta', 'ed_setRange', 'ed_setNpixels', 'nx', 'ny', 'nz', 'loopOrder']
        self.regin=self.sm['Scanner'].item()['MoveData'].item(0)['ReadChans'].item(0)
        self.dt=self.sm['Scanner'].item()['ScanData'].item(0)['dt'].item()

        self.dataDic={}
        for i in range(len(self.regin)) :
            reg=self.regin[i]
            self.dataDic[reg+' forward']=self.data(nForward=1,nRegin=i)
            self.dataDic[reg+' backward']=self.data(nForward=0,nRegin=i)

    def findRange(self,excludeNan=False,data=None):
        self.xmin=float(self.scdata['ed_xmin'].item())
        self.xmax=float(self.scdata['ed_xmax'].item())
        self.nx=int(self.scdata['nx'].item())
        self.ymin=float(self.scdata['ed_ymin'].item())
        self.ymax=float(self.scdata['ed_ymax'].item())
        self.ny=int(self.scdata['ny'].item())
        self.xplot=np.linspace(self.xmin,self.xmax,self.nx+1) #+1 because matplotlib colormesh is weird
        self.yplot=np.linspace(self.ymin,self.ymax,self.ny+1)
        if excludeNan:
            for i in range(self.ny):
                if np.isnan(data[i,0]) :
                    self.ny=i
                    self.ymax=self.yplot[i-1]
                    break
            for j in range(self.nx):
                if np.isnan(data[0,j]) :
                    self.nx=j
                    self.xmax=self.xplot[j-1]
                    break
            self.xplot=np.linspace(self.xmin,self.xmax,self.nx+1)
            self.yplot=np.linspace(self.ymin,self.ymax,self.ny+1)
            
    def xBeforeY(self):
        loopOrder=self.scdata['loopOrder'].item()
        return(loopOrder.find('x')<loopOrder.find('y'))
    
    def data(self,nForward=1,nRegin=0):
        #nForward = 1 : forward : =0 : backward
        #nRegin= according to the regin list
        data=self.sm['Scanner'].item()['ScanData'].item(0)['data'].item()['dir'].item(nRegin)['data'].item(1-nForward)
        if self.xBeforeY() :
            return data
        else :
            return data.T
    
    def plot(self,dataKey='Vz forward',excludeNan=True,invertX=True,invertY=True,flipXY=True,squarePixels=True,correctGradient=False, vmin=None, vmax=None):
        ctrMap="viridis"
        VzMap="viridis" #"Blues_r"
        magnetoMap="bwr"
        cmaps={"Vz forward":VzMap,"Vz backward":VzMap,'Counter1 forward':ctrMap, 'Counter1 backward':ctrMap, 'Counter2 forward':ctrMap, 'Counter2 backward':ctrMap, 'Norm forward' :magnetoMap, 'Norm backward':magnetoMap, 'Diff forward':magnetoMap, 'Diff backward':magnetoMap, 'RFFreq forward':magnetoMap, 'RFFreq backward':magnetoMap}
        C=self.dataDic[dataKey]
        self.findRange(excludeNan=excludeNan,data=C)
        C=C[:self.ny,:self.nx]
        xlabel='X voltage (V)'
        ylabel='Y voltage (V)'
        analyse.plot_map(C=C,xAxis=self.xplot,yAxis=self.yplot,color=cmaps[dataKey],xBeforeY=self.xBeforeY(),invertX=invertX,invertY=invertY, flipXY=flipXY, squarePixels=squarePixels,correctGradient=correctGradient,vmin=vmin,vmax=vmax,xlabel=xlabel,ylabel=ylabel)

class NVAFM_RFscan_matFile(matFile):
    keys=['__header__', '__version__', '__globals__', 'smNVscan_new', '__function_workspace__']
    def __init__(self, pathToFile) -> None:
        super().__init__(pathToFile)
        assert self.keys==self.matKeys, 'Wrong file (%s) for the class (%s)'%(self.matKeys[3],self.keys[3])

        self.sm=self.matDic['smNVscan_new']
        self.allFreqs=self.sm['Scanner'].item()['ScanData'].item(0)['sweepvals'].item()
        self.allESRData=self.sm['Scanner'].item()['ScanData'].item(0)['datapointmode'].item()

        self.nScans=0
        for esr in self.allESRData: #the program fills the last line/column with zeroes when you stop
            if esr[0]==0 :
                break
            else :
                self.nScans+=1
      

        self.dt=self.sm['Scanner'].item()['ScanData'].item(0)['esr'].item()['dt'].item()
        self.power=self.sm['Scanner'].item()['ScanData'].item(0)['esr'].item()['power'].item()

        f=self.sm['Scanner'].item()['ScanCreate'].item(0)['scData'].item()['Fields'].item()
        self.xmin,self.xmax,self.ymin,self.ymax=f['ed_xmin'].item(),f['ed_xmax'].item(),f['ed_ymin'].item(),f['ed_ymax'].item()
        self.nx,self.ny,self.nz=f['nx'].item(),f['ny'].item(),f['nz'].item()
        self.xrange=np.linspace(self.xmin,self.xmax,self.nx)
        self.yrange=np.linspace(self.ymin,self.ymax,self.ny)
        self.theta=f['ed_theta']
        if 'Vzdata' in headers(self.sm['Scanner'].item()['ScanData'].item(0)) :
            self.Vz=self.sm['Scanner'].item()['ScanData'].item(0)['Vzdata'].item()[:self.nScans]
        if 'centerFreqArray' in headers(self.sm['Scanner'].item()['ScanData'].item(0)) :
            self.centerFreq=self.sm['Scanner'].item()['ScanData'].item(0)['centerFreqArray'].item()[:self.nScans]
    def getESR(self,i=0):
        return(self.allFreqs[i],self.allESRData[i])
    def indexToXY(self,i):
        if self.xBeforeY():
            ix=i%self.nx
            iy=i//self.ny
        else :
            ix=i//self.nx
            iy=i%self.ny
        return ix,iy
    def xyToIndex(self,ix,iy):
        if self.xBeforeY():
            i=ix+self.nx*iy
        else :
            i=iy+self.ny*ix
        return i
    
    def VzLine(self,nLine=0):
        if self.xBeforeY():
            l=np.zeros(self.nx)
            t=np.linspace(self.xmin,self.xmax,self.nx)
            for ix in range(self.nx):
                i=self.xyToIndex(ix=ix,iy=nLine)
                if i<self.nScans :
                    l[ix]=self.Vz[i]
                else :
                    l[ix]=np.nan

        else :
            l=np.zeros(self.ny)
            t=np.linspace(self.ymin,self.ymax,self.ny)
            for iy in range(self.ny):
                i=self.xyToIndex(ix=nLine,iy=iy)
                if i<self.nScans :
                    l[iy]=self.centerFreq[i]
                else :
                    l[iy]=np.nan

        return t,l


    def ESRCentralFreqLine(self,nLine=0,excludeNan=True):
        if self.xBeforeY():
            l=np.zeros(self.nx)
            t=np.linspace(self.xmin,self.xmax,self.nx)
            for ix in range(self.nx):
                i=self.xyToIndex(ix=ix,iy=nLine)
                if i<self.nScans :
                    l[ix]=self.centerFreq[i]
                else :
                    l[ix]=np.nan

        else :
            l=np.zeros(self.ny)
            t=np.linspace(self.ymin,self.ymax,self.ny)
            for iy in range(self.ny):
                i=self.xyToIndex(ix=nLine,iy=iy)
                if i<self.nScans :
                    l[iy]=self.centerFreq[i]
                else :
                    l[iy]=np.nan
        if excludeNan :
            for i in range(len(l)):
                if np.isnan(l[i]):
                    break
            l=l[:i]
            t=t[:i]
        return t,l

    def xBeforeY(self):
        loopOrder=self.sm['Scanner'].item()['ScanCreate'].item(0)['scData'].item()['Fields'].item()['loopOrder'].item()
        return(loopOrder.find('x')<loopOrder.find('y'))

class NVAFM_feedback_matFile(matFile):
    keys=['__header__', '__version__', '__globals__', 'smfeedback', '__function_workspace__']
    def __init__(self, pathToFile) -> None:
        super().__init__(pathToFile)
        assert self.keys==self.matKeys, 'Wrong file (%s) for the class (%s)'%(self.matKeys[3],self.keys[3])
        self.sm=self.matDic[self.keys[3]]

        self.convPLFreq=self.sm['Fields'].item()['ed_f_conv'].item() # in cts/s/MHz

        self.time=self.sm['History'].item()['TotalTime'].item()
        self.ctr1=self.sm['History'].item()['fC1'].item()
        self.ctr2=self.sm['History'].item()['fC2'].item()
        self.freqs=self.sm['History'].item()['fFreq'].item()

class NVAFM_scan_with_fb(NVAFM_scan_matFile):
    def __init__(self, pathToFile, fbDirectory='default',startIndex='unknown') :
        super().__init__(pathToFile)
        if fbDirectory=='default' :
            fbDirectory=os.path.dirname(pathToFile)+'/fb'
        self.fbFiles=sorted(glob.glob(fbDirectory+'/fb_*.mat'))
        self.findFbFiles(startIndex=startIndex)
        self.addCtrData()

    def findFbFiles(self,startIndex='unknown'):
        #To find the starting fbFile, we scan all the files in the fb folder and find the one that matches the first line of the RFFreq scan
        C=self.dataDic['RFFreq forward']
        if startIndex=='unknown' :
            yscan=C[0]
            matching=np.inf
            for fbFile in self.fbFiles :   
                fb=NVAFM_feedback_matFile(fbFile)
                yf=fb.freqs
                if len(yf) >= len(yscan) :
                    yfReduced=analyse.reduce_array(yf,len(yscan))
                    if sum((yfReduced-yscan)**2) < matching :
                        matching=sum((yfReduced-yscan)**2)
                        startIndex=self.fbFiles.index(fbFile)
            print('startIndex= %i'%startIndex)
        for i in range(len(C)):
            if np.isnan(C[i][0]) :
                break
        self.nNonNaN=i
        self.fbIndices=[startIndex+3*i for i in range(self.nNonNaN)]

    def addCtrData(self):
        C=self.dataDic['RFFreq forward']
        n=len(C[0])
        ctr1=[]
        ctr2=[]
        for i in range(len(C)):
            if i < self.nNonNaN :
                fb=NVAFM_feedback_matFile(self.fbFiles[self.fbIndices[i]])
                ctr1+=[analyse.reduce_array(fb.ctr1,n)]
                ctr2+=[analyse.reduce_array(fb.ctr2,n)]
            else :
                ctr1+=[[np.nan]*n]
                ctr2+=[[np.nan]*n]
        ctr1=np.array(ctr1)
        ctr2=np.array(ctr2)
        self.dataDic['Counter1 forward']=ctr1
        self.dataDic['Counter2 forward']=ctr2

class NVAFM_sweeper(matFile):
    keys=['__header__', '__version__', '__globals__', 'smNVsweeper', '__function_workspace__']
    def __init__(self, pathToFile) -> None:
        super().__init__(pathToFile)
        assert self.keys==self.matKeys, 'Wrong file (%s) for the class (%s)'%(self.matKeys[3],self.keys[3])
        
        



if __name__=='__main__':
    t=NVAFM_scan_matFile(fileScan)
    t.plot(excludeNan=True)

   
    

    


