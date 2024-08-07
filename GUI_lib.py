import sys
import os
import time
import traceback
from ruamel.yaml import YAML
yaml=YAML()
from typing import Literal
import numpy as np
import csv
import datetime
import rpyc
import importlib.util
import shutil



from PyQt5 import QtCore, uic,QtWidgets
from PyQt5.QtGui import QFont,QTransform,QCloseEvent
from PyQt5.QtCore import (Qt, QTimer,QSize, QEvent)
from PyQt5.QtWidgets import (QWidget, QPushButton, QComboBox,
    QHBoxLayout, QVBoxLayout, QApplication, QDesktopWidget, QMainWindow, QLineEdit, QLabel, QCheckBox, QFileDialog, QErrorMessage, QMessageBox, QFrame, QSpinBox)

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar

import pyqtgraph as pg #Plot library
import qdarkstyle #For dark mode
from pyqt_led import Led as ledWidget #For LED widget

from qcodes import Parameter, validators as vals, instrument

qapp=QtWidgets.QApplication([])

'''
Config files (.yaml) and design files (.ui) are defined here.
These files exist always in two folder : 
one global (in the same folder as this file) which should be the same on all installations,
and one local (emplacement stored in Local folder.txt) which can be customized by each user.

The local version overrides the global version,
but if a variable is not present in the local version, it will be added with the default value from the global version.
'''

#~~~~~~~~~~~~~~~~~~~~ Config folders ~~~~~~~~~~~~~~~~~~~~#

def findLocalFolder():
    #Find the local folder where the config (yaml) and design files are stored
    if "LOCAL_FOLDER" in os.environ.keys():
        localFolder=os.environ['LOCAL_FOLDER']
    else :
        raise KeyError("LOCAL_FOLDER environment variable not found, please look at the documentation to set it up")
        # Creating an environment variable with conda : 
        # conda activate labcontrol (or whatever env you are using)
        # conda env config vars set LOCAL_FOLDER="D:\...\python local folder"
        # conda activate labcontrol
        # conda env config vars list (to check the variable)


    if not os.path.exists(localFolder):
        raise FileNotFoundError("LOCAL_FOLDER environment variable points to a non existing folder")
   
    #Makes sure the local config folder and subfolders exists
    localConfigFolder=os.path.join(localFolder,'Config files')
    if not os.path.exists(localConfigFolder):
        os.mkdir(localConfigFolder)
    if not os.path.exists(os.path.join(localConfigFolder,'Experiments')):
        os.mkdir(os.path.join(localConfigFolder,'Experiments'))
    if not os.path.exists(os.path.join(localConfigFolder,'Instruments')):
        os.mkdir(os.path.join(localConfigFolder,'Instruments'))

    #Same for the design folders
    localDesignFolder=os.path.join(localFolder,'GUI design files')
    if not os.path.exists(localDesignFolder):
        os.mkdir(localDesignFolder)
    localFitFolder=os.path.join(localFolder,'Fits')
    if not os.path.exists(localFitFolder):
        os.mkdir(localFitFolder)
    localPulseFolder=os.path.join(localFolder,'Pulses')
    if not os.path.exists(localPulseFolder):
        os.mkdir(localPulseFolder)
    return localConfigFolder,localDesignFolder,localFitFolder,localPulseFolder

localConfigFolder,localDesignFolder,localFitFolder,localPulseFolder=findLocalFolder()

#~~~~~~~~~~~~~~~~~~~~ Config files ~~~~~~~~~~~~~~~~~~~~#

def updateYamlFile(filename, d):
    #Updates the yaml file with the dictionnary d
    if not filename.endswith('.yaml'):
        filename+='.yaml'
    filename=os.path.join(localConfigFolder,filename)
    with open(filename,'w') as f:
        yaml.dump(d,f)   

#TODO : make file@save@ESR work
def localVariableDic(configFileName):
    #Returns a dictionnary with all local variables. If a variable is not present in the local file (after a code update for instance), it will update the local file with the default value form the global file
    if not configFileName.endswith('.yaml'):    
        configFileName+='.yaml'
    localFilename=os.path.join(localConfigFolder,configFileName)

    globalFolder=os.path.join(os.path.dirname(__file__),'Config files')
    globalFilename=os.path.join(globalFolder,configFileName)

    if not os.path.exists(localFilename):
        shutil.copyfile(globalFilename,localFilename)
    with open(localFilename,'r') as f:
        dloc=yaml.load(f)
    with open(globalFilename,'r') as f:
        dglob=yaml.load(f)
    
    updateLocalFile=False
    for key in dglob.keys():
        if key not in dloc.keys():
            dloc[key]=dglob[key]
            updateLocalFile=True
    if updateLocalFile :
        updateYamlFile(configFileName,dloc)

    def recursiveAll(elem):
        if isinstance(elem,dict):
            return recursiveDict(elem)
        elif isinstance(elem,list):
            return recursiveList(elem)
        elif isinstance(elem,str):
            return recursiveStr(elem)
        else :
            return elem

    def recursiveDict(d:dict):
        for key in d.keys():
            d[key]=recursiveAll(d[key])
        return d

    def recursiveList(l:list):
        for i in range(len(l)):
            l[i]=recursiveAll(l[i])
        return l

    def recursiveStr(elem):

        if elem[0]=='@':
            file,key=elem[1:].split('.',1)
            if key :
                return localVariableDic(file)[key]
            else :
                return localVariableDic(file)
        elif elem.split('.')>1:
            dic=dloc
            key,value=elem.split('.',1)
            while value:
                dic=dic[key]
                key,value=value.split('.',1)
            return dic[key]
        else :
            return elem
        

    return recursiveAll(dloc)

def localDesignFile(designFileName: str):   
    #Returns the path to the local design file. If it doesn't exist, it will create it from the global design file
    if not designFileName.endswith('.ui'):
        designFileName+='.ui'
    localFilename=os.path.join(localDesignFolder,designFileName)

    globalFolder=os.path.join(os.path.dirname(__file__),'GUI design files')
    globalFilename=os.path.join(globalFolder,designFileName)
    if not os.path.exists(globalFilename):
        raise FileNotFoundError("Global design '%s' file not found"%(globalFilename))


    if not os.path.exists(localFilename):
        shutil.copyfile(globalFilename,localFilename)
    return localFilename

def localFit(fitFileName: str):
    if not fitFileName.endswith('.py'):
        fitFileName+='.py'
    completeFitFileName=os.path.join(localFitFolder,fitFileName)
    if not os.path.exists(completeFitFileName):
        completeGlobalFit=os.path.join(os.path.dirname(__file__),'Fits',fitFileName)
        if os.path.exists(completeGlobalFit):           
            shutil.copyfile(completeGlobalFit,completeFitFileName)
        else :
            raise FileNotFoundError("Global fit '%s' file not found"%(completeGlobalFit))
    spec=importlib.util.spec_from_file_location("fit", completeFitFileName)
    foo=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    return foo.fit()

def checkComputerDic():
    change=False
    if computerDic['computer_name']=="":
        print("Computer name not found. Please enter a neame for this computer :")
        computerDic['computer_name']=input()
        change=True
    if computerDic['save_folder']=="":
        print("Save folder not found. Please select a folder to save data :")
        computerDic['save_folder']=QFileDialog.getExistingDirectory(None, "Select Save Folder")
        change=True
    if change:
        updateYamlFile('Computer.yaml',computerDic)

#Usefule libraries and checks
computerDic=localVariableDic('Computer.yaml')
unitsDic=localVariableDic('units')
checkComputerDic()




class styleSheet():
    def __init__(self,configFileName='default_style_sheet.yaml') -> None:
        self.d=localVariableDic(configFileName)
        self.theme=self.d['default theme']  
        if self.theme=='light':
            #Global Config of pyqtgrqph (dark by default)
            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', 'k')	
        if self.theme=='dark':
            #Global config of pyQT (light by default)
            qapp.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

        self.penColors=self.d['penColors'][self.theme]
        self.infiniteLineColor=self.d['infiniteLineColor'][self.theme]
    """
    We define bellow the functions returning the plot parameters of each type of line (data,trace,fit).
    - style : "data", "trace" or "fit"
    - penIndex (int) is used to know which colour to apply to each line
    - ydata (np.array) is used because we apply different tchickness for different length of arrays : for an array with a substantial amount of points (eg > 1000), pyqtgraph is significantly faster to plot with a thinner line. Don't ask me why.
    """

    def lineStyle(self,style : str):
        #Implemented line styles : "solid", "dash", "dot", "dashdot", "dashdotdot"
        if style=='solid':
            return Qt.SolidLine
        elif style=='dash':
            return Qt.DashLine
        elif style=='dot':
            return Qt.DotLine
        elif style=='dashdot':
            return Qt.DashDotLine
        elif style=='dashdotdot':
            return Qt.DashDotDotLine
        
    def plottingArgs(self,style,penIndex,ydata):
        #Supported styles : "data", "trace", "fit"
        n=len(ydata)
        if n>self.d['threshold for thin line']:
            width=self.d[style+' params']['thin width']
        else :
            width=self.d[style+' params']['large width']
        lineStyle=self.lineStyle(self.d[style+' params']['style'])
        pen=pg.mkPen(color=self.penColors[penIndex],width=width,style=lineStyle)
        symbol=self.d[style+' params']['symbol']
        symbolBrush=pg.mkBrush(self.d[style+' params']['symbol brush'])
        return {"pen":pen, "symbol":symbol, "symbolPen":pen, "symbolBrush":symbolBrush}
        

        
''' 
Plotting GUI with pyQtGraph (pg) :

We follow here the matplotlib nomenclature : 
- Each graphical widget is constituted of a single figure (pgFig).
- Each figure can contain several axes (pgAx) which are subfigures defined by an x and y axis.
- Each ax can contain several lines (pgLine) and infinite lines (work as markers).
You can bypass the ax level and directly add lines to the figure, this will automaticallty create an ax.

- Maps (pgMap) are a specific object which act as an ax.
'''

class generalWidget():
    #All base "widget-like" objects should inherit this class, and store their true widget object in self.widget
    #Widget-like objects composed of two are more true widgets should inherit box instead
    def __init__(self):
        pass
    def setEnabled(self,b):
        self.widget.setEnabled(b)
    def isEnabled(self):
        return self.widget.isEnabled()
    def setFont(self,font='custom',fontName='Sans Serif',fontSize=12,weight=400): #weight=700 for Bold
        if font=='big':
            font=self.bigfontText
        elif font=='BIG':
            font=self.BIGfontText
        elif font=='bigNumber':
            font=self.bigfontNumber
        elif font=='BIGNumber':
            font=self.BIGfontNumber
        elif font=='custom':
            font=QFont(fontName, pointSize=fontSize, weight=weight)
        self.widget.setFont(font)
        self.resize()
    def resize(self,height='min',width='min'):
        if height=='min':
            height=self.widget.minimumSizeHint().height()
        if width=='min':
            width=self.widget.minimumSizeHint().width()
        self.widget.setFixedSize(width,height)
    def setColor(self,color='default',backgroundColor='default'):
        style=''
        if color!='default':
            style+='color: %s ;'%(color)
        if backgroundColor!='default':
            style+='background-color: %s ;'%(backgroundColor)
        self.widget.setStyleSheet(style)

    def addToBox(self,box):
        box.addWidget(self.widget)

class box(generalWidget):
    #box is what is called "layout" in Qt. It is a widget-like object which can contain other widget-like objects.
    #All widget-like objects composed of two or more true widgets should inherit this class
    def __init__(self,*items,typ='H',spacing='default',designerLayout=None ): #typ='H' or 'V'
        super().__init__()
        if typ=='H':
            self.box=QHBoxLayout()
        elif typ=='V':
            self.box=QVBoxLayout()
        if designerLayout!=None:
            self.box=designerLayout
        self.items=[]
        if spacing=='default':
            self.box.addStretch(1)
        for item in items :
            if item=='stretch':
                self.box.addStretch(1)
            elif type(item)==int or type(item)==float :               
                w=QWidget()
                if typ=='H':
                    w.setFixedSize(item,1)
                elif typ=='V':
                    w.setFixedSize(1,item)
                self.box.addWidget(w)
            else :
                if type(item)!=box and len(items)>1 :
                    if typ=='H':
                        item=box(item,typ='V')
                    elif typ=='V':
                        item=box(item,typ='H')
                # item.resize()
                item.addToBox(self.box)
                self.items+=[item]
        if spacing=='default':
            self.box.addStretch(1)

        # self.box.setAlignment(Qt.AlignHCenter)
        # self.box.setAlignment(Qt.AlignVCenter)
        # self.widget=QWidget()
        # self.widget.setLayout(self.box)
    def setEnabled(self,b):
        for item in self.items:
            item.setEnabled(b)
    def setFont(self,*args,**kwargs):
        for item in self.items:
            try:
                item.setFont(*args,**kwargs)
            except:
                pass
    def resize(self,height='min',width='min'):
        #Resize for boxes resize each item with the given values. 
        for item in self.items:
            item.resize(height=height,width=width)
    def addToBox(self, box):
        box.addLayout(self.box)

class pgFig(generalWidget) :
    def __init__(self,style='default_style_sheet.yaml', designerWidget=None, size=None,refreshRate=10,title=None, config:dict=None):
        #refreshRate in frames per second
        super().__init__()
        if config:
            if 'refresh_rate' in config.keys():
                refreshRate=config['refresh_rate']
            if 'title' in config.keys():
                title=config['title']
            if 'style' in config.keys():
                style=config['style']
            

        self.ss=styleSheet(style)
        if designerWidget==None:
            self.widget=pg.GraphicsLayoutWidget(size=size,title=title)
        else :
            # self.widget=pg.GraphicsLayoutWidget(title=title,parent=designerWidget,size=[designerWidget.width(),designerWidget.height()])   
            self.widget=designerWidget
        self.axes=[] #Contains axes and maps
        self.refreshRate=refreshRate
        self.timeLastUpdate=time.time()
    def addAx(self, map=False, row=None, col=None, rowspan=1, colspan=1, axTitle=''):
        if map :
            ax=pgMap(title=axTitle, fig=self)
        else :
            ax=pgAx(title=axTitle, fig=self)
        self.axes+=[ax]
        self.widget.addItem(ax,row=row, col=col, rowspan=rowspan, colspan=colspan)
        return ax
    def addLine(self,x=[],y=[],ax=None,typ='data',label=None,addToLegend=False):
        if len(self.axes)==0:
            ax=self.addAx()
        elif ax==None :
            ax=self.axes[0]
        ax.addLine(x=x,y=y,typ=typ,label=label,addToLegend=addToLegend)
    def removeAx(self,ax):
        self.widget.removeItem(ax)
        self.axes.remove(ax)
    def clear(self):
        self.widget.clear()
    def saveData(self,filename):
        for ax in self.axes:
            ax.saveData(filename)
    def setXLabel(self,label):
        for ax in self.axes:
            ax.setXLabel(label)
    def setYLabel(self,label):
        for ax in self.axes:
            ax.setYLabel(label)
    def saveFig(self,filename):
        #Note pg.exporters not fully released yet, switching to Qt for now
        self.widget.grab().save(filename)
        # exporter=pg.exporters.ImageExporter(self.widget.scene())
        # exporter.export(filename)

class pgAx(pg.PlotItem):
    def __init__(self,title :str, fig :pgFig):
        super().__init__(title=title)
        self.baseTitle=title
        self.fig=fig
        self.ss=self.fig.ss
        #Create the list of available colors (True = available, False = taken)
        self.penIndices=[True]*len(self.ss.penColors)
        #Create space for legend
        self.legend=self.addLegend(labelTextSize='15pt')
        #Create the catalog of lines ,infinite lines, traces and fits in the ax
        self.infiniteLines=[]
        self.dataLines=[]
        self.traces=[]
        self.fits=[]
        #Adds the ax to the figure
        self.fig.widget.addItem(self)
        tickFont=QFont(self.ss.d['pg_ticks']['font_name'],self.ss.d['pg_ticks']['font_size'])
        self.getAxis('bottom').setTickFont(font=tickFont)
        self.getAxis('left').setTickFont(font=tickFont)
        self.norm=False

    def addLine(self,x=[],y=[],typ='instant',label=None,addToLegend=False,updateIter=True):
        '''
        typ='instant' : when given a new set of x and y value will replace the previous line
        typ='average' : will add the new x and/or y value to the current line and average with the proper weight
        typ='scroll' : will place the new given points at the right of the curve and discard an equivalent amount to the left.
        typ='trace' : reserved for traces
        typ='fit' : resserved for fits
        '''
        penIndex=self.nextPenIndex()
        self.penIndices[penIndex]=False
        #Creates the line
        if not label:
            label='Line %i'%(len(self.allLines())+1)
        l=pgLine(ax=self,penIndex=penIndex,x=x,y=y,typ=typ,label=label,addToLegend=addToLegend,norm=self.norm,updateIter=updateIter)
        #Adds the line to the ax
        self.addItem(l)
        #Adds the line to the line inventory
        if typ=='instant' or typ=='average' or typ=='scroll' :
            self.dataLines+=[l]
        elif typ=='trace':
            self.traces+=[l]
        elif typ=='fit':
            self.fits+=[l]
        return l

    def allLines(self):
        return self.dataLines+self.traces+self.fits
    
    def setNorm(self,norm:bool):
        self.norm=norm
        for line in self.allLines():
            line.setNorm(norm)

    def addTrace(self):
        for line in self.dataLines:
            label='Trace %i'%(len(self.traces)+1)
            self.addLine(x=line.x,y=line.y,typ='trace',label=label)
        
    def removeLastTrace(self):
        if len(self.traces)>0:
            self.removeLine(self.traces[-1])
    
    def removeLine(self,line):
        self.removeItem(line)
        if line.typ=='instant' or line.typ=='average' or line.typ=='scroll' :
            self.dataLines.remove(line)
        elif line.typ=='trace':
            self.traces.remove(line)
        elif line.typ=='fit':
            self.fits.remove(line)
        if line.existingLegend :
            self.legend.removeItem(line)
        self.penIndices[line.penIndex]=True
        
    def nextPenIndex(self):
        for i in range(len(self.penIndices)):
            if self.penIndices[i]:
                break
        return i
    
    def setXLabel(self,label):
        if self.ss.d['default theme']=='dark':
            color='white'
        else :
            color='black'
        labelStyle={'font-size': '%ipt'%(self.ss.d['pg_labels']['font_size']),'color':color}
        self.setLabel('bottom',label,**labelStyle)

    def setYLabel(self,label):
        if self.ss.d['default theme']=='dark':
            color='white'
        else :
            color='black'
        labelStyle={'font-size': '%ipt'%(self.ss.d['pg_labels']['font_size']),'color':color}
        self.setLabel('left',label,**labelStyle)

    def saveData(self,filename):
        for line in self.allLines():
            line.saveData(filename)

class pgLine(pg.PlotDataItem):
    def __init__(self,
                 ax:pgAx,
                 penIndex:int,
                 x:np.array,
                 y:np.array,
                 typ:Literal['instant','average','scroll','trace','fit'],
                 label:str,
                 addToLegend:bool,
                 norm:bool,
                 updateIter:bool):
        
        self.ax=ax
        self.typ=typ
        self.penIndex=penIndex
        self.label=label
        self.addToLegend=addToLegend
        self.ss=self.ax.ss
        self.norm=norm #Norm only affects display, the data is always stored with its real value
        self.updateIter=updateIter #Will update the number of iterations on the title of the plot

        if len(x)==0:
            x=np.linspace(0,1,101)
        if len(y)==0:
            y=np.zeros(101)
        self.x=x
        self.y=y
        # plotType is used to look for the correct plotting parameters in the styleSheet
        if self.typ=='instant' or self.typ=='average' or self.typ=='scroll' :
            self.plotType='data'
        else :
            self.plotType=self.typ
        #Collects the plotting parameters for the line
        plotArgs=self.ss.plottingArgs(style=self.plotType,penIndex=self.penIndex,ydata=self.y)

        #Creates the line item (Pg.PlotDataItem)
        super().__init__(x,y,**plotArgs)
        #Adds a legend if provided
        self.existingLegend=False
        self.updateLegend(label)

        self.nIteration=0 



    def setNorm(self,norm=True):
        self.norm=norm
        self.redraw()

    def updateLegend(self,label):
        if self.addToLegend :
            if self.existingLegend :
                self.ax.legend.removeItem(self)
                self.ax.legend.addItem(self,label)
            else :
                self.existingLegend=True
                self.ax.legend.addItem(self,label)

    def saveData(self,filename):
        with open (filename,'a') as f:
            writer=csv.writer(f,delimiter=',',lineterminator='\n',quoting=csv.QUOTE_NONNUMERIC)
            x=['x'+self.label]+list(self.x)
            y=['y'+self.label]+list(self.y)
            writer.writerow(x)
            writer.writerow(y)

    def reset(self):
        self.nIteration=0
        self.x=np.array([])
        self.y=np.array([])

    def redraw(self):
        self.update(self.x,self.y,bypassRefresh=True)

    def update(self,x=[],y=[],bypassRefresh=False):
        """
        Leave x or y as [] if you dont want to change them.

        Basis of updating line for each type :
        instant/trace/data : will simply plot the new x and/or y value instead of the old ones
        average : will average the new y values with the previous ones. If new x is given will simply replace old x
        scroll : take a list of new y and/or x points to add to the end of the line. E.g. y=[12.0] will just add one point at the end of the line and delete the first point. If you update x with values inferiors to the previous ones, you are looking for troubles
        """
        #bypassRefresh will show the updated line regardless of the time delay since the laste update
        self.nIteration+=1
        #We should by default use numpy arrays, but just in case
        if isinstance(y,list):
            y=np.array(y)
        if isinstance(x,list):
            x=np.array(x)

        if len(x)==0:
            pass
        else :
            if self.typ=='scroll':
                n=len(x)
                newX=np.roll(self.x,-n)
                newX[-n:]=x
            else :
                newX=x

            self.x=newX

        if len(y)==0:
            pass
        else :
            if self.typ=='average':
                oldY=self.y
                if self.nIteration==1:
                    newY=y #This is required because the placeholder y does not have the same length as the new y
                else :
                    newY=oldY*(1-1/self.nIteration)+y*1/self.nIteration
            elif self.typ=='scroll':
                n=len(y)
                assert n <= len(self.y) #Checks there are less new values than total displayed values
                if self.nIteration==1: #For a new scroll line, ensure that all the initial values are of the  same order of the measured ones
                    self.y=np.ones(len(self.y))*y[0]
                newY=np.roll(self.y,-n)
                newY[-n:]=y
            else :
                newY=y

            self.y=newY

        if time.time()>self.ax.fig.timeLastUpdate + 1/self.ax.fig.refreshRate or bypassRefresh:
            show=True
            self.ax.fig.timeLastUpdate=time.time()
        else :
            show=False


        if show :
            plotArgs=self.ss.plottingArgs(style=self.plotType,penIndex=self.penIndex,ydata=self.y)
            yToPlot=self.y
            if self.norm :
                normFactor=np.max(np.abs(self.y))
                if normFactor!=0:
                    yToPlot=self.y/normFactor
            if self.updateIter:
                self.ax.setTitle(self.ax.baseTitle+' (%i)'%(self.nIteration))
            self.setData(self.x,yToPlot,**plotArgs)

class pgMap(pg.ImageItem):
    def __init__(self, image=None, **kargs):
        super().__init__(image, **kargs)

class mplFig(box):
    def __init__(self, designerLayout=None, size=(10,8),toolbar=True,tightLayout=True):

        super().__init__(designerLayout=designerLayout)


        self.fig=matplotlib.figure.Figure(figsize=size)
        if tightLayout :
            self.fig.set_layout_engine('tight')
        self.mplFig=FigureCanvas(self.fig)
        self.box.addWidget(self.mplFig)
        if toolbar :
            self.toolbar = NavigationToolbar(self.mplFig)
            self.box.addWidget(self.toolbar)

        self.axes=[]

    def addAx(self, nrows=1, ncols=1, index=(1,1), **kargs):
        ax=self.fig.add_subplot(nrows,ncols,index,**kargs)
        self.axes+=[ax]
        return ax
    
    def update(self):
        self.fig.canvas.draw()

    def setAction(self,action):
        self.fig.canvas.mpl_connect('button_press_event', action)
        #event.button : 1=left, 2=middle, 3=right
        #event.xdata, event.ydata : coordinates of the click in the data units
        #Example action :
        # def dummyAction(event):
        #     print("clicked with button %d at (%f,%f)"%(event.button,event.xdata,event.ydata))

    def clear(self):
        self.fig.clear()
        self.axes=[]
        
class Graphical_interface(QMainWindow) :
    def __init__(self,
                 *itemLists,
                 designerFile='',
                 title='Unnamed',
                 size='default',
                 keyPressed='default', 
                 keyReleased='default',
                 parent=None, 
                 config:dict=None, 
                 styleSheetFile='default_style_sheet.yaml'):
        super().__init__(parent=parent) #Creates a window

        if config!=None:
            if "designer_file" in config.keys():
                designerFile=config["designer_file"]
            if "name" in config.keys():
                title=config["name"]
            if "style_sheet" in config.keys():
                styleSheetFile= config['style_sheet']

        sys.excepthook=self.excepthook #If the GUI crash, it will execute self.excepthook which calls self.closeEvent

        self.title=title #if loading UI form designer, this will be ignored
        self.keyPressed=keyPressed #Function to be called when a key is pressed and the window is in focus, see examples
        self.keyReleased=keyReleased #Same for released key
        self.styleSheet=styleSheet(configFileName=styleSheetFile)
        if designerFile :
            uic.loadUi(localDesignFile(designerFile), self)
        else :
            self.setWindowTitle(title)
            main = QFrame()
            self.widget=main
            self.setCentralWidget(main)
            layout= QHBoxLayout()
            #Assumes that widgets in itemLists are of the form ([widg1,widg2,widg3],[widg4,widg5],[widg6]) which will produce 3 vertical columns of widgets
            for itemList in itemLists :
                vBox=QVBoxLayout()
                layout.addLayout(vBox)
                if isinstance(itemList,list):
                    for item in itemList :
                        item.addToBox(vBox)
                else :
                    itemList.addToBox(vBox)
            main.setLayout(layout)
            self.layout=layout
            if size=='default' :
                self.resize(1200,800)
            elif size=='auto' :
                pass
            else :
                self.resize(size[0],size[1])	
    def keyPressEvent(self, e):
        #See example in Plot_data
        if self.keyPressed=='default':
            return
        else :
            self.keyPressed(e)
    def keyReleaseEvent(self, e):
        if self.keyReleased=='default':
            return
        else :
            self.keyReleased(e)
    def setTitle(self,title):
        self.setWindowTitle(title)
    def setBackGroundColor(self,backgroundColor):
        style='QFrame {background-color: %s ;}'%(backgroundColor)
        self.widget.setStyleSheet(style)
    def run(self):
        self.show()
        qapp.exec_()
    def closeEvent(self, event): 
        self.close()
    def excepthook(self,exc_type, exc_value, exc_tb):
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print("error catched!:")
        print("error message:\n", tb)
        self.closeEvent(QCloseEvent())

class label(generalWidget):
    def __init__(self,name='',precision='exact',designerWidget:QLabel=False):
        super().__init__()
        self.precision=precision
        if designerWidget : 
            self.widget=designerWidget
            self.text=self.widget.text()
        else :
            self.widget=QLabel()
            self.text=name
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self,text):
        self._text=text
        self.widget.setText(repr_numbers(text,precision=self.precision))
        self.resize()
        

class button(generalWidget):
    def __init__(self,name='',action=False,designerWidget:QPushButton=False): 
        super().__init__()
        if designerWidget : 
            self.widget=designerWidget
        else :
            self.widget=QPushButton(name)    
            self.resize()  
        if action :
            self.setAction(action)        
    def setAction(self,action,actionType='clicked'):
        if actionType=='clicked':
            self.widget.clicked.connect(action)
        elif actionType=='pressed' :
            self.widget.pressed.connect(action)
        elif actionType=='released' :
            self.widget.released.connect(action)

class startStopButtons(box):
    """
    This class creates two buttons to start and stop timed actions.
    The start button first calls initAction, then create a Qtimer instance which will call repeatdly updateAction every time it times out.
    The stop button stops the timer and calls stopAction.
    initAction and stopAction take the arguments given in initArgs and stopArgs respectively. The arguemnts must be given as a dictionary with the key as the argument name and the value as the argument value.
    updateAction takes a single argument which is the iteration number of the timer.
    timerDelay is the delay between each call of updateAction in ms.
    """
    def __init__(self,initAction=False,updateAction=False,stopAction=False,initArgs={},stopArgs={},startDesignerWidget=None,stopDesignerWidget=None, timerDelay=0):
        self.initAction=initAction
        self.updateAction=updateAction
        self.stopAction=stopAction
        self.initArgs=initArgs
        self.stopArgs=stopArgs
        self.timerDelay=timerDelay
        self.startButton=button('Start',action=self.start,designerWidget=startDesignerWidget)
        self.stopButton=button('Stop',action=self.stop,designerWidget=stopDesignerWidget)
        self.stopButton.setEnabled(False)
        super().__init__(self.startButton,self.stopButton,typ='V')
        self.iteration=0

    def start(self):
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        if self.initAction :
            self.initAction(**self.initArgs)
        self.timer=QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.timerDelay)
    
    def update(self):
        self.iteration+=1
        self.updateAction(self.iteration)

    def stop(self):
        self.timer.stop()
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        if self.stopAction :
            self.stopAction(**self.stopArgs)
        self.iteration=0
        
class led(generalWidget):
    def __init__(self,shape="circle",radius=20):
        super().__init__()
        self.widget=ledWidget(parent=None,shape=ledWidget.circle ,on_color=ledWidget.green,off_color=ledWidget.red)
        self.resize(radius,radius)
    def turnOn(self):
        self.widget.set_status(True)
    def turnOff(self):
        self.widget.set_status(False)

class buttonWithLed(box):
    def __init__(self,name,action=False,ledRadius=20):
        self.button=button(name,action=action)
        self.led=led(radius=ledRadius)
        super().__init__(self.button,self.led,typ='H')
    def setAction(self,*args,**kwargs):
        self.button.setAction(*args,**kwargs)
    def resize(self,*args,**kwargs):
        self.button.resize(*args,**kwargs)
    def setFont(self, *args, **kwargs):
        self.button.setFont(*args, **kwargs)
    
class checkBox(generalWidget):
    def __init__(self,name='',action=False,initialState=False,designerWidget:QCheckBox=None): 
        super().__init__()
        if designerWidget != None :
            self.widget=designerWidget
        else :
            self.widget=QCheckBox(name)

        self.setState(initialState)
        if action :
            self.setAction(action)  
    def setAction(self,action):		
            self.widget.stateChanged.connect(action)
    def setState(self,state):
        self.widget.setCheckState(state)
        self.widget.setTristate(False)
    def state(self):
        return(self.widget.isChecked())

class comboBox(generalWidget):
    #Comboboxes are basically menus
    #I implemented here the possibility to access the entry either by its index or by its text
    #I added a dictionary to store the index of each entry to make things easier
    def __init__(self,*items,action=False,actionType='currentIndexChanged',designerWidget:QComboBox=None):
        super().__init__()
        #Remark : a combo box with no entry is condered as 'False'
        if designerWidget != None :
            self.widget=designerWidget
        else :
            self.widget=QComboBox()
        self.dic={}
        for item in items :
            self.addItem(item)
        if action :
            self.setAction(action,actionType)
    def setAction(self,action,actionType='currentIndexChanged'):
        if actionType=='currentIndexChanged':
            self.widget.currentIndexChanged.connect(action)
        elif actionType=='activated' :
            self.widget.activated.connect(action)
        else :
            raise ValueError('Action type not understood')
    def index(self):
        #Returns the index of the current entry
        return self.widget.currentIndex()
    def setValue(self,v):
        #v can be either the index or the text of the entry
        if isinstance(v,str) :
            i=self.dic[v]
        else :
            i=v
        return self.widget.setCurrentIndex(i)
    def text(self):
        #Returns the text of the current entry
        return self.widget.currentText()
    def addItem(self,item):
        self.dic[item]=self.widget.count() #Doing it first so its starts at 0
        self.widget.addItem(item)
    def addItems(self,items):
        for item in items :
            self.addItem(item)
    def removeItem(self,item):
        if isinstance(item,str) :
            i=self.dic[item]
            key=item
        else :
            i=item
            key=self.widget.itemText(i)
        self.widget.removeItem(i)
        self.dic.pop(key)
    def removeAll(self):
        self.widget.clear()
        self.dic={}


class lineEdit(generalWidget):
    def __init__(self,initialValue='noValue',action="update",precision='exact',designerWidget:QLineEdit=None): 
        super().__init__()
        self.precision=precision
        if designerWidget : 
            self.widget=designerWidget
            self.value=self.widget.text()
        else :
            self.widget=QLineEdit()
            self.widget.minimumSizeHint=lambda : QSize(100,20)
            self.resize()
        if initialValue != 'noValue' :
            self.value=initialValue
        if action :
            self.setAction(action)
        
    @property
    def value(self):
        return self._value
    
    
    @value.setter
    def value(self,new_value):
        self._value=self.convertTextToValue(new_value)
        self.updateTofield()

    def getValue(self):
        return self.value
    
    def setValue(self,new_value):
        self.value=new_value
    def convertTextToValue(self,text):
        try :
            value=float(text)
            if value.is_integer():
                value=int(value)
        except :
            value=text
        return value
        
    def updateFromField(self):
        self.value=self.widget.text()
        
    def updateTofield(self):
        self.widget.setText(repr_numbers(self.value,precision=self.precision))
        
    def setAction(self,action,actionType='editing finished'):
        if action=="update":
            action=self.updateFromField
        
        if actionType=='editing finished':
            self.widget.editingFinished.connect(action)
        elif actionType=='return pressed' :
            self.widget.returnPressed.connect(action)

class spinBox(generalWidget):
    def __init__(self,
                 default_value=0,
                 action="update",
                 action_type='editing finished',
                 unit='',
                 minimum=-1000000000,
                 maximum=1000000000,
                 step_size=1,
                 designerWidget:QSpinBox=None): 
        super().__init__()
        self.widget=QSpinBox()
        self.widget.setValue(default_value)
        self.widget.setMinimum(minimum)
        self.widget.setMaximum(maximum)
        self.widget.setSingleStep(step_size)
        self.unit=unit
        self.widget.setSuffix(' '+self.unit)
        

class field(lineEdit):
    def __init__(
            self,
            name='',
            initialValue='noValue',
            action=False,
            precision='exact',
            unit='no_unit',
            labelDesignerWidget:QLabel=None,
            lineDesignerWidget:QLineEdit=None,
            config:dict=None
            ):  
              
        if config :
            if "name" in config:
                name=config["name"]
            if "default_value" in config:
                initialValue=config["default_value"]
            if "precision" in config:
                precision=config["precision"]
            if "unit" in config:
                unit=config["unit"]
        if isinstance(unit,str):
            unit=unitsDic[unit]
        self.unit=unit
        super().__init__(initialValue=initialValue,action=action,precision=precision,designerWidget=lineDesignerWidget)
        self.label=label(name,designerWidget=labelDesignerWidget)

        if self.unit['base']!='no_unit':
            self.label.text+=' (%s)'%self.unit['base']

    def addToBox(self, box):
        box.addWidget(self.label.widget)
        box.addWidget(self.widget)

class fieldParameter(field):
    def __init__(
            self,
            parameter:Parameter,
            name='',
            initialValue='noValue',
            action='update',
            precision='exact',
            unit='no_unit',
            labelDesignerWidget:QLabel=None,
            lineDesignerWidget:QLineEdit=None,
            config:dict=None
            ):  
        self.parameter=parameter
        super().__init__(name=name,initialValue=initialValue,action=action,precision=precision,unit=unit,labelDesignerWidget=labelDesignerWidget,lineDesignerWidget=lineDesignerWidget,config=config)
        self.update()

    def update(self):
        paramValue=self.parameter.get()
        try :
            self.value=conversion_unit(paramValue,self.parameter.unit,self.unit)
        except :
            self.value=paramValue

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,new_value):
        self._value=self.convertTextToValue(new_value)
        self.updateTofield()
        #Automatically converts the field unit into the parameter unit.
        #If it fails, it just sets the parameter to the field value
        try :
            paramValue=conversion_unit(self._value,self.unit,self.parameter.unit)
        except :
            paramValue=self._value
        self.parameter.set(paramValue)
        

class saveButton(button):
    def __init__(self,fig:pgFig, config:dict, designerWidget:QPushButton=None, exp_name:field=None, sample_name:field=None):
        super().__init__(designerWidget=designerWidget)
        self.config=config
        self.fig=fig
        self.exp_name=exp_name
        self.sample_name=sample_name
        self.setAction(lambda : self.save()) #Dont ask me why but just putting self.save as the action does not work
        #Seriously wtf Qt ?
    def folder(self):
        saveFolder=computerDic['save_folder']
        expFolder=self.config['folder']
        saveFolder=os.path.join(saveFolder,expFolder)
        subfolders=self.config['subfolders']
        if subfolders:
            if 'y' in subfolders:
                year=datetime.datetime.now().strftime("%Y")
                saveFolder=os.path.join(saveFolder,year)
            if 'm' in subfolders:
                month=datetime.datetime.now().strftime("%m")
                saveFolder=os.path.join(saveFolder,month)
            if 'd' in subfolders:
                day=datetime.datetime.now().strftime("%d")
                saveFolder=os.path.join(saveFolder,day)
        os.makedirs(saveFolder,exist_ok=True)
        return saveFolder
    def filename(self):
        if self.exp_name:
            filename=self.exp_name.value+'_'
        filename+=datetime.datetime.now().strftime("%Y-%m-%d")
        if self.sample_name:
            filename+='_'+self.sample_name.value
        return filename
    def dataFile(self):
        filename=os.path.join(self.folder(),self.filename()+'.csv')
        if os.path.isfile(filename):
            i=1
            f=filename[:-4]
            while True:
                filename=f+'_%i.csv'%i
                if not os.path.isfile(filename):
                    break
                i+=1
        return filename
    def figFile(self):
        filename=os.path.join(self.folder(),self.filename()+'.png')
        if os.path.isfile(filename):
            i=1
            f=filename[:-4]
            while True:
                filename=f+'_%i.png'%i
                if not os.path.isfile(filename):
                    break
                i+=1
        return filename
    def saveData(self):
        self.fig.saveData(self.dataFile())
    def saveFig(self):
        self.fig.saveFig(self.figFile())
    def save(self):
        print("Saving data and figure")
        if self.config['save_data']:
            self.saveData()
        if self.config['save_fig']:
            self.saveFig()

class stationConnect(button):
    def __init__(self,buttonDesignerWidget:QPushButton,comboBoxDesignerWidget:QComboBox,config:dict):
        super().__init__(name='Connect',designerWidget=buttonDesignerWidget)
        self.stationMenu=comboBox(designerWidget=comboBoxDesignerWidget)
        allServices=rpyc.list_services()
        self.stations={}
        for serviceName in allServices:
            if serviceName.startswith('STATION ON '):
                (IP_address,port)=rpyc.discover(serviceName)[0]
                self.stations[serviceName[11:]]={'IP_address':IP_address,'port':port}
        self.stationMenu.addItems(self.stations.keys())
        self.setAction(self.connectAction)
    def connectAction(self):
        stationName=self.stationMenu.text()
        print('Connecting to station %s'%stationName)
        print('IP address : %s, port : %i'%(self.stations[stationName]['IP_address'],self.stations[stationName]['port']))
        c=rpyc.connect(self.stations[stationName]['IP_address'],self.stations[stationName]['port'])
        print(c.root.uptime())

class addFitButton(button):
    def __init__(self,line:pgLine,config:dict,designerWidget:QPushButton=None,ax='sameAsLine'):
        super().__init__(name='Add fit',designerWidget=designerWidget)
        if ax=='sameAsLine':
            ax=line.ax
        self.ax=ax
        self.line=line
        self.fit=localFit(config['fit_function'])
        self.setAction(lambda: self.addFit())
    def addFit(self):
        x=self.line.x
        y=self.line.y
        try :
            self.fit.fit(x,y)
        except Exception as e:
            print(e)
            return
            
        self.ax.addLine(x=x,y=self.fit.fittedY,typ='fit',label=self.fit.legend(),addToLegend=True)

class removeFitButton(button):
    def __init__(self,ax:pgAx,designerWidget:QPushButton=None):
        super().__init__(name='Remove fit',designerWidget=designerWidget)
        self.ax=ax
        self.setAction(lambda: self.removeFit())
    def removeFit(self):
        if len(self.ax.fits)>0:
            self.ax.removeLine(self.ax.fits[-1])

class mpt_colormap(generalWidget):
    def __init__(self):
        super().__init__()

class GUI_enterValue(QMainWindow):
    def __init__(self, label="Value title", defaultValue=""):
        super().__init__()
        self.label=label
        self.defaultValue=defaultValue
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.label)
        self.main = QFrame()
        self.setCentralWidget(self.main)
        layout= QVBoxLayout()
        self.main.setLayout(layout)
        self.value=QLineEdit()
        self.value.setText(self.defaultValue)
        self.value.editingFinished.connect(self.close)
        self.Qlabel=QLabel(self.label)
        layout.addWidget(self.Qlabel)
        layout.addWidget(self.value)
        self.show()

################### Utility functions #####################
def repr_numbers(value,precision='exact',maxScientficExponent=4,minScientficExponent=-2):
    if isinstance(value,str):
        label=(value)
    elif value==0:
        label=('0')
    elif abs(value)>10**maxScientficExponent or abs(value) <10**minScientficExponent :
        if precision=='exact' :
            label=('%e'%value)
        else :
            label=('{:.{}e}'.format(value,precision))
    elif isinstance(value,int) :
        label=('%i'%value)
    else :
        if precision=='exact' :
            label=('%f'%value)
        else :
            label=('{:.{}f}'.format(value,precision))
    return label

def conversion_unit(value,oldUnit,newUnit):   
    if isinstance(oldUnit,str):
        oldUnit=unitsDic[oldUnit]
    if isinstance(newUnit,str):
        newUnit=unitsDic[newUnit]
    if oldUnit==newUnit:
        return value
    if oldUnit['base']!=newUnit['base']:
        raise ValueError('Cannot convert from %s to %s'%(oldUnit['name'],newUnit['name']))
    return value*oldUnit['multiplier']/newUnit['multiplier']

def valueToBaseUnit(value,unit):
    return conversion_unit(value=value, oldUnit=unit, newUnit=unit['base'])
    
def valueFromBaseUnit(value,unit):
    return conversion_unit(value=value, oldUnit=unit['base'], newUnit=unit)

def currentFolder():
    return os.path.dirname(os.path.realpath(__file__))



################### Test functions #####################
def changeColorWhenInFocus(oldWidget,newWidget):
    if newWidget :
        style='background-color: blue'
        newWidget.setStyleSheet(style)
    if oldWidget :
        style='background-color: palette(base)'
        oldWidget.setStyleSheet(style)

def testWithDesigner():
    GUI=Graphical_interface(designerFile='testUI',title='Example GUI')
    print(dir(GUI))

    # class MainWindow(QtWidgets.QMainWindow):
    #     def __init__(self, *args, **kwargs):
    #         super().__init__(*args, **kwargs)
    #         uic.loadUi('/home/clement/Postdoc/python/Perso/testUI.ui', self)
    # GUI=MainWindow()


    gra=pgFig(designerWidget=GUI.glw)
    ax=gra.addAx()
    x=np.linspace(0,10,101)
    y=np.cos(x)
    # l1=pgLine(x=x,y=y,ax=ax,penIndex=0,typ='instant',label=None)
    l1=ax.addLine(x=x,y=y,typ='instant',label=None)

    def update(i):
        y=np.cos(x+time.time())
        l1.update(y=y)
    def init():
        print('init')
    def cleanUp():
        print('cleanUp')
    startStop=startStopButtons(initAction=init,stopAction=cleanUp,updateAction=update,startDesignerWidget=GUI.start,stopDesignerWidget=GUI.stop)

    GUI.show()
    qapp.exec_()

def test_pg():

    f1=field('toto',10)
    f2=field('toto2',5)
    fields=[f1,f2]

    b1=buttonWithLed('test button')
    def b1_action():
        print(f1.getValue())
        print(qapp.activeWindow().title)
        return
    b1.setAction(b1_action)

    fig=pgFig(refreshRate=30)
    ax=fig.addAx()
    x=np.linspace(0,10,101)
    y=np.cos(x)
    l1=ax.addLine(x=x,y=y,typ='instant',label=None)

    def update(i):
        y=np.cos(x+time.time())
        l1.update(y=y)
    def init():
        print('init')
    def cleanUp():
        print('cleanUp')
    startStop=startStopButtons(initAction=init,stopAction=cleanUp, updateAction=update)
    buttons=[b1,startStop]
    GUI=Graphical_interface(fields,fig,buttons,title='Example GUI')
    # print(dir(GUI))
    GUI.run()

def test_fit_params_window():
    import matplotlib.pyplot as plt
    fit=localFit('Lorentzian')
    # x=np.linspace(0,50,101)
    # y=10-2*1/(1+((x-20)/7)**2)+np.random.normal(0,0.1,101)
    # plt.plot(x,y)
    # fit.fit(x,y)
    # plt.plot(x,fit.fitting_curve)
    # plt.show()
    for param in fit.free_param_guess.keys():
        pass
if __name__ == "__main__":
    testWithDesigner()