import sys
import os
import time
import traceback

from PyQt5.QtGui import QFont,QTransform,QCloseEvent
from PyQt5.QtCore import (Qt, QTimer,QSize, QEvent)
from PyQt5.QtWidgets import (QWidget, QPushButton, QComboBox,
    QHBoxLayout, QVBoxLayout, QApplication, QDesktopWidget, QMainWindow, QLineEdit, QLabel, QCheckBox, QFileDialog, QErrorMessage, QMessageBox, QFrame)

import qdarkstyle
from pyqt_led import Led as ledWidget


qapp = QApplication(sys.argv)

class Graphical_interface(QMainWindow) :
    def __init__(self,*itemLists,title='Unnamed',theme='light',size='default',keyPressed='default', keyReleased='default'):
        super().__init__()
        sys.excepthook=self.excepthook #If the GUI crash, it will execute self.excepthook and self.closeEvent
        self.title=title
        self.setWindowTitle(title)
        main = QFrame()
        self.widget=main
        self.setCentralWidget(main)
        layout= QHBoxLayout()
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
        if theme=='dark' :
            qapp.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        self.keyPressed=keyPressed
        self.keyReleased=keyReleased
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

class generalWidget():
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


class box(generalWidget):
    def __init__(self,*items,typ='H',spacing='default'): #typ='H' or 'V', For Horizontal boxes, spaceAbove/below becomes left/right
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
    qapp.focusChanged.connect(changeColorWhenInFocus)
    test_pg()