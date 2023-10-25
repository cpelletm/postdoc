import sys
import os
import time
import traceback
import json
import typing
import numpy as np



from PyQt5 import QtCore, uic,QtWidgets
from PyQt5.QtGui import QFont,QTransform,QCloseEvent
from PyQt5.QtCore import (Qt, QTimer,QSize, QEvent)
from PyQt5.QtWidgets import (QWidget, QPushButton, QComboBox,
    QHBoxLayout, QVBoxLayout, QApplication, QDesktopWidget, QMainWindow, QLineEdit, QLabel, QCheckBox, QFileDialog, QErrorMessage, QMessageBox, QFrame)

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar

import pyqtgraph as pg #Plot library
import qdarkstyle #For dark mode
from pyqt_led import Led as ledWidget #For LED widget

qapp = QApplication(sys.argv)

'''
Config files (.json) and design files (.ui) are defined here.
These files exist always in two folder : 
one global (in the same folder as this file) which should be the same on all installations,
and one local (emplacement stored in Local folder.txt) which can be customized by each user.

The local version overrides the global version,
but if a variable is not present in the local version, it will be added with the default value from the global version.
'''

def findLocalFolder():
    #Find the local folder where the config files (json files and design files) are stored
    currentFolder=os.path.dirname(__file__)
    localFolder_path=os.path.join(currentFolder,'Local folder.txt')
    if os.path.exists(localFolder_path):
        with open(localFolder_path,'r') as f:
            localFolder=f.read()
    if not os.path.exists(localFolder):
        localFolder=QFileDialog.getExistingDirectory(None, "Select Local Config Folder", currentFolder)
        with open(localFolder_path,'w') as f:
            f.write(localFolder)
    
    localConfigFolder=os.path.join(localFolder,'Config files')
    if not os.path.exists(localConfigFolder):
        os.mkdir(localConfigFolder)
    localDesignFolder=os.path.join(localFolder,'GUI design files')
    if not os.path.exists(localDesignFolder):
        os.mkdir(localDesignFolder)
    return localConfigFolder,localDesignFolder

localConfigFolder,localDesignFolder=findLocalFolder()

def updateJsonFile(filename, d):
    #Updates the json file with the dictionnary d
    if not filename.endswith('.json'):
        filename+='.json'
    filename=os.path.join(localConfigFolder,filename)
    with open(filename,'w') as f:
        json.dump(d,f,indent=2)

def localVariableDic(configFileName):
    #Returns a dictionnary with all local variables. If a variable is not present in the local file (after a code update for instance), it will update the local file with the default value form the global file
    if not configFileName.endswith('.json'):    
        configFileName+='.json'
    localFilename=os.path.join(localConfigFolder,configFileName)

    globalFolder=os.path.join(os.path.dirname(__file__),'Config files')
    globalFilename=os.path.join(globalFolder,configFileName)

    if not os.path.exists(localFilename):
        import shutil
        shutil.copyfile(globalFilename,localFilename)
    with open(localFilename,'r') as f:
        dloc=json.load(f)
    with open(globalFilename,'r') as f:
        dglob=json.load(f)
    
    updateLocalFile=False
    for key in dglob.keys():
        if key not in dloc.keys():
            dloc[key]=dglob[key]
            updateLocalFile=True
    if updateLocalFile :
        updateJsonFile(configFileName,dloc)

    return dloc
 
computerDic=localVariableDic('Computer.json')
def checkComputerDic():
    change=False
    if computerDic['computer name']=="":
        print("Computer name not found. Please enter a neame for this computer :")
        computerDic['computer name']=input()
        change=True
    if computerDic['save folder']=="":
        computerDic['save folder']=QFileDialog.getExistingDirectory(None, "Select Save Folder")
        change=True
    if change:
        updateJsonFile('Computer.json',computerDic)
checkComputerDic()

def localDesignFile(designFileName: str):   
    #Returns the path to the local design file. If it doesn't exist, it will create it from the global design file
    if not designFileName.endswith('.ui'):
        designFileName+='.ui'
    localFilename=os.path.join(localDesignFolder,designFileName)

    globalFolder=os.path.join(os.path.dirname(__file__),'GUI design files')
    globalFilename=os.path.join(globalFolder,designFileName)

    if not os.path.exists(localFilename):
        import shutil
        shutil.copyfile(globalFilename,localFilename)
    return localFilename

class styleSheet():
    def __init__(self,theme='default',configFileName='style sheet.json') -> None:
        #theme : "light" or "dark". "default" will take the value from the default value from the config file
        self.d=localVariableDic(configFileName)
        if theme=='default':
            theme=self.d['default theme']
        self.theme=theme     
        if theme=='light':
            #Global Config of pyqtgrqph (dark by default)
            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', 'k')	
            #Default colors of matplotlib		
            self.penColors=self.d['lightPenColors']
            self.infiniteLineColor=self.d['lightInfiniteLineColor']
        if theme=='dark':
            #Global config of pyQT (lifgt by default)
            qapp.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

            self.penColors=self.d['darkPenColors']
            self.infiniteLineColor=self.d['darkInfiniteLineColor']
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
        n=len(ydata)
        if style=='data':
            if n > self.d['threshold for thin line']:
                width=self.d['data thin width']
            else :
                width=self.d['data large width']
            style=self.lineStyle(self.d['data style'])
            pen=pg.mkPen(color=self.penColors[penIndex],width=width,style=style)
            symbol=self.d['data symbol']
            symbolBrush=pg.mkBrush(self.d['data symbol brush'])
            return {"pen":pen, "symbol":symbol, "symbolPen":pen, "symbolBrush":symbolBrush}
        
        elif style=='trace':
            if n > self.d['threshold for thin line']:
                width=self.d['trace thin width']
            else :
                width=self.d['trace large width']
            style=self.lineStyle(self.d['trace style'])
            pen=pg.mkPen(color=self.penColors[penIndex],width=width,style=style)
            symbol=self.d['trace symbol']
            symbolBrush=pg.mkBrush(self.d['trace symbol brush'])
            return {"pen":pen, "symbol":symbol, "symbolPen":pen, "symbolBrush":symbolBrush}
        
        elif style=='fit':
            if n > self.d['threshold for thin line']:
                width=self.d['fit thin width']
            else :
                width=self.d['fit large width']
            style=self.lineStyle(self.d['data style'])
            pen=pg.mkPen(color=self.penColors[penIndex],width=width,style=style)
            symbol=self.d['fit symbol']
            symbolBrush=pg.mkBrush(self.d['fit symbol brush'])
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
    bigfontText=QFont( "Sans Serif", 15, QFont.Bold)
    BIGfontText=QFont( "Sans Serif", 30, QFont.Bold)
    bigfontNumber=QFont( "Consolas", 20, QFont.Bold)
    BIGfontNumber=QFont( "Consolas", 40, QFont.Bold)
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
    def __init__(self,style :styleSheet=None, designerWidget=None, size=None,refreshRate=30,title=None):
        #refreshRate in frames per second
        super().__init__()
        if style==None:
            style=styleSheet()
        self.style=style
        if designerWidget==None:
            self.widget=pg.GraphicsLayoutWidget(size=size,title=title)
        else :
            self.widget=pg.GraphicsLayoutWidget(title=title,parent=designerWidget,size=[designerWidget.width(),designerWidget.height()])   
        self.axes=[] #Contains axes and maps
        self.refreshRate=refreshRate
        self.timeLastUpdate=time.time()
    def addAx(self, map=False, row=None, col=None, rowspan=1, colspan=1, axTitle=None):
        if map :
            ax=pgMap(title=axTitle, fig=self)
        else :
            ax=pgAx(title=axTitle, fig=self)
        self.axes+=[ax]
        self.widget.addItem(ax,row=row, col=col, rowspan=rowspan, colspan=colspan)
        return ax
    def addLine(self,x=[],y=[],ax=None,style='data',name=None):
        if len(self.axes)==0:
            ax=self.addAx()
        elif ax==None :
            ax=self.axes[0]
        ax.addLine(x=x,y=y,style=style,name=name)
    def removeAx(self,ax):
        self.widget.removeItem(ax)
        self.axes.remove(ax)
    def clear(self):
        self.widget.clear()

class pgAx(pg.PlotItem):
    def __init__(self,title :str, fig :pgFig):
        super().__init__(title=title)
        self.fig=fig
        #Create the list of available colors (True = available, False = taken)
        self.penIndices=[True]*len(self.fig.style.penColors)
        #Create space for legend
        self.legend=self.addLegend(labelTextSize='15pt')
        #Create the catalog of lines ,infinite lines, traces and fits in the ax
        self.infiniteLines=[]
        self.lines=[]
        self.traces=[]
        self.fits=[]
        #Adds the ax to the figure
        self.fig.widget.addItem(self)
    def addLine(self,x=[],y=[],typ='instant',label=None):
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
        l=pgLine(ax=self,penIndex=penIndex,x=x,y=y,typ=typ,label=label)
        #Adds the line to the ax
        self.addItem(l)
        #Adds the line to the line inventory
        self.lines+=[l]
        return l
    
    def removeLine(self,line):
        self.removeItem(line)
        self.lines.remove(line)
        if line.existingLegend :
            self.legend.removeItem(line)
        self.penIndices[line.penIndex]=True
        
    def addTrace(self,line,label=None):
        t=self.addLine(x=line.x,y=line.y,typ='trace',label=label)
        self.traces+=[t]
        return t
    
    def removeTrace(self,trace):
        self.traces.remove(trace)
        self.removeLine(trace)

    def nextPenIndex(self):
        for i in range(len(self.penIndices)):
            if self.penIndices[i]:
                break
        return i

class pgLine(pg.PlotDataItem):
    def __init__(self,ax:pgAx,penIndex,x,y,typ,label):
        
        self.ax=ax
        self.typ=typ
        self.penIndex=penIndex
        self.label=label
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
        self.ss=self.ax.fig.style
        #Collects the plotting parameters for the line
        plotArgs=self.ss.plottingArgs(style=self.plotType,penIndex=self.penIndex,ydata=self.y)

        #Creates the line item (Pg.PlotDataItem)
        super().__init__(x,y,**plotArgs)
        #Adds a legend if provided
        self.existingLegend=False
        self.updateLegend(label)

        self.nIteration=0 
        self.norm=False #Norm only affects display, the data is always stored with its real value



    def setNorm(self,norm=True):
        self.norm=norm

    def updateLegend(self,label):
        if label :
            if self.existingLegend :
                self.ax.legend.removeItem(self)
                self.ax.legend.addItem(self,label)
            else :
                self.existingLegend=True
                self.ax.legend.addItem(self,label)

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
            if self.norm :
                yToPlot=self.y/max(y)
            else :
                yToPlot=self.y
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
    def __init__(self,*itemLists,designerFile='',title='Unnamed',size='default',keyPressed='default', keyReleased='default',parent=None):
        super().__init__(parent=parent) #Creates a window

        sys.excepthook=self.excepthook #If the GUI crash, it will execute self.excepthook which calls self.closeEvent

        self.title=title #if loading UI form designer, this will be ignored
        self.keyPressed=keyPressed #Function to be called when a key is pressed and the window is in focus, see examples
        self.keyReleased=keyReleased #Same for released key

        if designerFile :
            uic.loadUi(designerFile, self)
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
    def __init__(self,name,precision='exact'):
        super().__init__()
        self.precision=precision
        self.widget=QLabel(repr_numbers(name,precision=self.precision))     
    def setText(self,text):
        self.widget.setText(repr_numbers(text,precision=self.precision))
        self.resize()
    def getText(self):
        return self.widget.text()

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
        
class saveButton(button):
    def __init__(self,designerWidget=None,saveConfigFile="default_save_config.json"):
        super().__init__("Save",action=self.save,designerWidget=designerWidget)
    def save(self):
        self.saveFunction()

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
        return self.widget.currentIndex()
    def setIndex(self,index):
        if isinstance(index,str) :
            i=self.dic[index]
        else :
            i=index
        return self.widget.setCurrentIndex(i)
    def text(self):
        return self.widget.currentText()
    def addItem(self,item):
        self.dic[item]=self.widget.count() #je le fait avant pour qu'il commence à 0
        self.widget.addItem(item)
    def addItems(self,items):
        for item in items :
            self.addItem(item)
    def removeItem(self,item):
        #Attention : ca vire pas du dictionnaire. Faudrait faire ça plus propre
        if isinstance(item,str) :
            i=self.dic[item]
        else :
            i=item
        return self.widget.removeItem(i)
    def removeAll(self):
        self.widget.clear()
        self.dic={}

class dropDownMenu(box):
    def __init__(self,name,*items,action=False,actionType='currentIndexChanged'):
        self.label=label(name)
        self.cb=comboBox(*items,action=action,actionType=actionType)
        super().__init__(self.label,self.cb,typ='V')

    def setAction(self,action,actionType='currentIndexChanged'):
        return self.cb.setAction(action=action,actionType=actionType)
    def index(self):
        return self.cb.index()
    def setIndex(self,index):
        return self.cb.setIndex(index)
    def text(self):
        return self.cb.text()
    def addItem(self,item):
        return self.cb.addItem(item)
    def removeItem(self,item):
        return self.cb.removeItem(item)
    def removeAll(self):
        return self.cb.removeAll()

class lineEdit(generalWidget):
    def __init__(self,initialValue='noValue',action="update",precision='exact',designerWidget:QLineEdit=False): 
        super().__init__()
        self.precision=precision
        if designerWidget : 
            self.widget=designerWidget
        else :
            self.widget=QLineEdit()
            self.widget.minimumSizeHint=lambda : QSize(100,20)
            self.resize()
        if initialValue != 'noValue' :
            self.setValue(initialValue)
        self.updateValue()
        if action :
            self.setAction(action)
        
    def getValue(self):
        self.updateValue()
        return self.v
    def updateValue(self):
        #Not the cleanest, but this will return a float, int or string depending on the input
        try : 
            self.v=float(self.widget.text())
            if self.v.is_integer():
                self.v=int(self.v)
        except :
            self.v=self.widget.text()
    def setValue(self,new_value):
        self.v=new_value
        label=repr_numbers(self.v,precision=self.precision)
        self.widget.setText(label)
    def setAction(self,action,actionType='editing finished'):
        if action=="update":
            action=self.updateValue
        
        if actionType=='editing finished':
            self.widget.editingFinished.connect(action)
        elif actionType=='Return Pressed' :
            self.widget.returnPressed.connect(action)

class field(box):
    def __init__(self,name,initialValue='noValue',action="update",precision='exact'): 
        self.label=label(name)
        self.line=lineEdit(initialValue=initialValue,action=action,precision=precision)
        super().__init__(self.label,self.line,typ='V')
    def getValue(self):
        return self.line.getValue()
    def setValue(self,new_value):
        return self.line.setValue(new_value=new_value)
    def setAction(self,action,actionType='editing finished'):
        return self.line.setAction(action=action,actionType=actionType)

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

def currentFolder():
    return os.path.dirname(os.path.realpath(__file__))

def changeColorWhenInFocus(oldWidget,newWidget):
    if newWidget :
        style='background-color: blue'
        newWidget.setStyleSheet(style)
    if oldWidget :
        style='background-color: palette(base)'
        oldWidget.setStyleSheet(style)

def testWithDesigner():
    GUI=Graphical_interface(designerFile="/home/clement/Postdoc/python/Perso/testUI.ui")

    # class MainWindow(QtWidgets.QMainWindow):
    #     def __init__(self, *args, **kwargs):
    #         super().__init__(*args, **kwargs)
    #         uic.loadUi('/home/clement/Postdoc/python/Perso/testUI.ui', self)
    # GUI=MainWindow()


    gra=pgFig(designerWidget=GUI.gra)
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

def testpgFig():
    ss=styleSheet()
    gra=pgFig(style=ss)
    ax=gra.addAx()
    x=np.linspace(0,10,101)
    y=np.cos(x)
    y2=np.sin(x)
    
    l1=pgLine(x=x,y=y2,ax=ax,penIndex=0,typ='instant',label=None)
    ax.addItem(l1)
    gra.widget.show()
    qapp.exec_()
    # pg.QtGui.QGuiApplication.exec_()
    # l1=ax.addLine(x,y)
    # GUI=Graphical_interface(gra,title='Example GUI')
    # GUI.run()

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

    fig=pgFig()
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

if __name__ == "__main__":
    testWithDesigner()