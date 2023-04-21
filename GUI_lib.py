import sys
import os
import time
import traceback
import json


from PyQt5 import uic
from PyQt5.QtGui import QFont,QTransform,QCloseEvent
from PyQt5.QtCore import (Qt, QTimer,QSize, QEvent)
from PyQt5.QtWidgets import (QWidget, QPushButton, QComboBox,
    QHBoxLayout, QVBoxLayout, QApplication, QDesktopWidget, QMainWindow, QLineEdit, QLabel, QCheckBox, QFileDialog, QErrorMessage, QMessageBox, QFrame)

import pyqtgraph as pg #Plot library
import qdarkstyle #For dark mode
from pyqt_led import Led as ledWidget #For LED widget


qapp = QApplication(sys.argv)

local_config_files_folder='default'

def localConfigFolder(localFolder):
    if localFolder=='default':
        import platform
        if platform.system()=='Windows':
            pass
        elif platform.system()=='Linux':
            f=os.path.expanduser('~/Documents/Python/GUI config files')
        else :
            raise ValueError('OS %s not supported for now(but you can change that !)'%(platform.system()))
    else :
        f=localFolder

    if not os.path.exists(f):
        ask=input('\n\nLocal config file not found. \n Would you like to create one in %s ? (y/n)'%(f))
        if ask=='y':
            os.mkdir(f)
        else :
            raise KeyboardInterrupt
    return f

def localVariableDic(configFileName):
    #Returns a dictionnary with all local variables. If a variable is not present in the local file (after a code update for instance), it will update the local file with the default value form the global file
    localFolder=localConfigFolder(localFolder=local_config_files_folder)
    localFilename=os.path.join(localFolder,configFileName)

    globalFolder=os.path.join(os.path.dirname(__file__),'GUI config files')
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
        with open(localFilename,'w') as f:
            json.dump(dloc,f,indent=0)

    return dloc





class styleSheet():
    def __init__(self,theme='light') -> None:
        self.theme=theme
        d=localVariableDic('style sheet.json')
        if theme=='light':
            #Global Config of pyqtgrqph (dark by default)
            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', 'k')	
            #Default colors of matplotlib		
            self.penColors=d['lightPenColors']
            self.infiniteLineColor=d['lightInfiniteLineColor']
        if theme=='dark':
            #Global config of pyQT (lifgt by default)
            qapp.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

            self.penColors=d['darkPenColors']
            self.infiniteLineColor=d['darkInfiniteLineColor']




''' 
Plotting GUI with pyQtGraph (pg) :

We follow here the matplotlib nomenclature : 
- Each graphical widget is constituted of a single figure (pgFig).
- Each figure con conatin several axes (pgAx) which are subfigures defined by an x and y axis.
- Each ax can contain several lines (pgLine) and infinite lines (work as markers).

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

class pgFig(generalWidget) :
    def __init__(self,style :styleSheet, graphicsLayoutWidget='make new', size=(20,15),refreshRate=30,title=None):
        #refreshRate in fps
        super().__init__()
        self.style=style
        if graphicsLayoutWidget=='make new':
            self.widget=pg.GraphicsLayoutWidget(size=size,title=title)
        else :
            assert graphicsLayoutWidget.__class__==pg.GraphicsLayoutWidget
            self.widget=graphicsLayoutWidget
        self.axes=[] #Contains axes and maps
        self.refreshRate=refreshRate
        self.timeLastUpdate=time.time()
    def addAx(self, map=False, row=None, col=None, rowspan=1, colspan=1, axTitle=None):
        if map :
            ax=pgMap(title=axTitle, fig=self)
        else :
            ax=pgAx(title=axTitle, fig=self)
        self.axes+=[ax]
        self.widget.addItem(row=row, col=col, rowspan=rowspan, colspan=colspan)
    def removeAx(self,ax):
        self.widget.removeItem(ax)
        self.axes.remove(ax)
    def clear(self):
        self.widget.clear()

class pgAx(pg.PlotItem):
    def __init__(self,title :str, fig :pgFig):
        super().__init__(title=title)
        self.fig=fig
        #Create the list of available colors
        self.penIndices=[True]*len(self.fig.style.penColors)
        #Create space for legend
        self.legend=self.addLegend(labelTextSize='15pt')
        #Create the catalog of lines and infinite lines in the ax
        self.infiniteLines=[]
        self.lines=[]
        #Adds the ax to the figure
        self.fig.widget.addItem(self)
    def addLine(self):
        pass

class pgLine(pg.PlotDataItem):
    def __init__(self,ax,x,y,typ='instant',label=None):
        '''
        typ='instant' : when given a new set of x and y value will replace the previous line
        typ='average' : will add the new x and/or y value to the current line and average with the proper weight
        typ='scroll' : will place the new given points at the right of the curve and discard an equivalent amount to the left.
        typ='trace' : reserved for traces
        typ='fit' : resserved for fits
        '''
        self.ax=ax
        self.typ=typ

        super().__init__()

class pgMap(pg.ImageItem):
    def __init__(self, image=None, **kargs):
        super().__init__(image, **kargs)

class Graphical_interface(QMainWindow) :
    def __init__(self,*itemLists,designerFile='',title='Unnamed',size='default',keyPressed='default', keyReleased='default'):
        super().__init__() #Creates a window

        sys.excepthook=self.excepthook #If the GUI crash, it will execute self.excepthook which calls self.closeEvent

        self.title=title #if loading UI form designer, this will be ignored
        self.keyPressed=keyPressed #Function to be called when a key is pressed and the window is in focus, see examples
        self.keyReleased=keyReleased #Same for released key

        if designerFile :
            uic.loadUi("python/Perso/testUI.ui", self)
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
        self.show()		
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
        qapp.exec_()
    def closeEvent(self, event): 
        self.close()
    def excepthook(self,exc_type, exc_value, exc_tb):
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print("error catched!:")
        print("error message:\n", tb)
        self.closeEvent(QCloseEvent())

class box(generalWidget):
    def __init__(self,*items,typ='H',spacing='default'): #typ='H' or 'V'
        super().__init__()
        if typ=='H':
            self.box=QHBoxLayout()
        elif typ=='V':
            self.box=QVBoxLayout()
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
        for item in self.items:
            item.resize(height=height,width=width)
    def addToBox(self, box):
        box.addLayout(self.box)

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
    def __init__(self,name,action=False): 
        super().__init__()
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
    def __init__(self,name,action=False,initialState=False): 
        super().__init__()
        self.widget=QCheckBox(name)
        self.setState(initialState)
        if action :
            self.setAction(action)  
    def setAction(self,action):		
            self.cb.stateChanged.connect(action)
    def setState(self,state):
        self.cb.setCheckState(state)
        self.cb.setTristate(False)
    def state(self):
        return(self.cb.isChecked())

class comboBox(generalWidget):
    def __init__(self,*items,action=False,actionType='currentIndexChanged'):
        super().__init__()
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
    def __init__(self,initialValue='noValue',action="update",precision='exact'): 
        super().__init__()
        self.precision=precision
        self.widget=QLineEdit()
        self.widget.minimumSizeHint=lambda : QSize(100,20)
        if initialValue != 'noValue' :
            self.setValue(initialValue)
        if action :
            self.setAction(action)
        self.resize()
    def getValue(self):
        self.updateValue()
        return self.v
    def updateValue(self):
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

def repr_numbers(value,precision='exact'):
    if isinstance(value,str):
        label=(value)
    elif value==0:
        label=('0')
    elif abs(value)>1E4 or abs(value) <1E-1 :
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

def test_pg():

    def dummyf(e):
        pos=e[0]
        print(pos.pos())


    f1=field('toto',10)
    f2=field('toto2',5)
    fields=[f1,f2]

    b1=buttonWithLed('test button')
    def b1_action():
        print(f1.getValue())
        print(qapp.activeWindow().title)
        return
    b1.setAction(b1_action)

    buttons=[b1]
    GUI=Graphical_interface(fields,buttons,title='Example GUI')
    # print(dir(GUI))
    GUI.run()

def whereIsFocus(oldWidget,newWidget):
    print('old widget:')
    print(oldWidget)
    print('new widget:')
    print(newWidget)

def changeColorWhenInFocus(oldWidget,newWidget):
    if newWidget :
        style='background-color: blue'
        newWidget.setStyleSheet(style)
    if oldWidget :
        style='background-color: palette(base)'
        oldWidget.setStyleSheet(style)

if __name__ == "__main__":
    localConfigFolder(localFolder=local_config_files_folder)