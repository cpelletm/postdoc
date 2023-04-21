from GUI_lib import (qapp, Qt, QEvent, QTimer, label, field, button, buttonWithLed, checkBox, dropDownMenu,box, led, Graphical_interface, traceback, whereIsFocus)
from PyANC350v2 import Positioner
import os
import pyperclip
import time

controllerIdNumber=0 # There is something in 0 which is already detected. Maybe the ASC500 ?

tipOrientation={
    'xUp':'right',
    'xDown':'left',
    'yUp':'up',
    'yDown':'down'
}

sampleOrientation={
    'xUp':'down',
    'xDown':'up',
    'yUp':'left',
    'yDown':'right'
}

class ANC350controller():
    def __init__(self,lib,stack,orientation,controllerIdNumber):
        self.lib=lib
        self.stack=stack
        self.orientation=orientation
        self.controllerIdNumber=controllerIdNumber
        self.status=0 #0 : disconnected, 1: connected
        if self.stack=='sample':
            self.x=self.add_axis(axis_no=0,name='x-axis')
            self.y=self.add_axis(axis_no=1,name='y-axis')
            self.z=self.add_axis(axis_no=2,name='z-axis')
        elif self.stack=='tip':
            self.x=self.add_axis(axis_no=3,name='x-axis')
            self.y=self.add_axis(axis_no=4,name='y-axis')
            self.z=self.add_axis(axis_no=5,name='z-axis')
        self.axes=[self.x,self.y,self.z]
        self.makePanel()
        self.timerUpdatePos=QTimer()
        self.timerUpdatePos.timeout.connect(self.updatePos)


    def connect(self):
        if self.stack=='tip':
            self.handle=self.lib.connect(device_no=self.controllerIdNumber)
        print("connected %s to device no %i"%(self.stack, self.controllerIdNumber))
        self.status=1
        self.disconnectButton.setEnabled(True)
        self.connectButton.setEnabled(False)
        self.connectedLed.turnOn()
        self.allAxesBox.setEnabled(True)
        self.XYZbox.setEnabled(True)
        self.allAxesMenuAction() #Disable and ground all axes
        self.allAxesInitialize()
        self.timerUpdatePos.start(100) #time in ms between each update


    def disconnect(self):
        if self.status :
            self.stop_all_motion()
            self.timerUpdatePos.stop()
            self.allAxesMenu.setIndex('Off')
            if self.stack=='tip':
                self.lib.close()
            print("disconnected %s to device no %i"%(self.stack, self.controllerIdNumber))
            self.connectedLed.turnOff()
            self.XYZbox.setEnabled(False)
            self.allAxesBox.setEnabled(False)
            self.disconnectButton.setEnabled(False)
            self.connectButton.setEnabled(True)
        
        self.status=0

    def stop_all_motion(self):
        for ax in self.axes:
            try:
                ax.stop_continuous(direction='up')
            except Exception:
                pass
                # print(traceback.format_exc())
            try:
                ax.stop_continuous(direction='down')
            except Exception:
                pass
                # print(traceback.format_exc())

    def add_axis(self, axis_no, name):
        ax=ANC350axis(self, axis_no=axis_no, name=name)
        return ax

    def checkAxisStatus(self):
        for ax in self.axes:
            if ax.status :
                return 1
        return 0

    def makePanel(self):
        self.connectButton=button('Connect')
        self.connectButton.setAction(self.connect)
        self.connectButton.setFont('big')

        if self.stack=='tip':
            self.stackLabel=label('Tip')
            self.stackLabel.setColor(color='red')
        elif self.stack=='sample':
            self.stackLabel=label('Sample')
            self.stackLabel.setColor(color='blue')
        self.stackLabel.setFont('BIG')

        self.disconnectButton=button('Disconnect')
        self.disconnectButton.setAction(self.disconnect)
        self.disconnectButton.setFont('big')
        self.disconnectButton.setEnabled(False)

        self.connectedLed=led(32)


        self.boxConnect=box(self.connectButton,self.disconnectButton,self.connectedLed,typ='H')
        if self.stack=='tip':
            self.boxConnectTitle=box(self.stackLabel,self.boxConnect,typ='V')
        elif self.stack=='sample':
            self.boxConnectTitle=box(self.stackLabel)

        ##### Brake button is not needed nor useful
        # self.brakeButton=button('BRAKE')
        # self.brakeButton.setFont('big')
        # self.brakeButton.widget.setStyleSheet('background-color: red')
        # self.brakeButton.setAction(self.stop_all_motion)

        self.allAxesMenu=dropDownMenu("Mode","Off","On")
        self.allAxesMenu.setAction(self.allAxesMenuAction)
        self.allAxesMenu.setFont(fontSize=14)

        self.allAxesAmpField=field("Amplitude (V)",30)
        self.allAxesAmpField.setAction(self.allAxesAmpFieldAction)

        self.allAxesFreqField=field("Frequency (Hz)",100)
        self.allAxesFreqField.setAction(self.allAxesFreqFieldAction)

        self.allAxesLabel=label('All axes')
        self.allAxesLabel.setFont('big')

        self.allAxesFieldBox=box(self.allAxesFreqField,self.allAxesAmpField,typ='V')
        self.allAxesMenuFieldBox=box(self.allAxesMenu,self.allAxesFieldBox, typ='H')

        self.allAxesMeasureCapa=button("Measure capacitance (all)",action=self.updateCapa)
        self.copyCoordButton=button('Copy coordinates',action=self.copyCoord )
        self.measurCapaCopyCoordBox=box(self.allAxesMeasureCapa,self.copyCoordButton, typ='H')
        self.allAxesBox=box(self.allAxesLabel,self.allAxesMenuFieldBox,self.measurCapaCopyCoordBox,typ='V')
        self.allAxesBox.setEnabled(False)


        # self.topBox=box(self.boxConnectTitle,'stretch',self.allAxesBox,typ='H')
        # self.XYZbox=box(self.x.panel,20, self.y.panel,20, self.z.panel, typ='H')
        # self.XYZbox.setEnabled(False)
        # self.panel=box(self.topBox,30,self.XYZbox,typ='V')

        self.XYZbox=box(self.x.panel, self.y.panel, self.z.panel, typ='V')
        self.XYZbox.setEnabled(False)
        self.panel=box(self.boxConnectTitle, self.allAxesBox, self.XYZbox,typ='V')


    def updatePos(self):
        for ax in self.axes:
            ax.updatePos()

    def updateCapa(self):
        for ax in self.axes :
            ax.updateCapa()

    def copyCoord(self):
        coordText="%s coordinates \n x=%s\n y=%s\n z=%s"%(self.stack,self.x.posLabel.getText(),self.y.posLabel.getText(),self.z.posLabel.getText())
        pyperclip.copy(coordText)
        return coordText

    def allAxesMenuAction(self):
        for ax in self.axes :
            ax.displacementMode.setIndex(self.allAxesMenu.index())
            ax.menuAction()

    def allAxesFreqFieldAction(self):
        for ax in self.axes :
            ax.freqField.setValue(self.allAxesFreqField.getValue())
            ax.freqFieldAction()

    def allAxesAmpFieldAction(self):
        for ax in self.axes :
            ax.ampField.setValue(self.allAxesAmpField.getValue())
            ax.ampFieldAction()

    def allAxesInitialize(self):
        for ax in self.axes :
            ax.initializeAxis()


class ANC350axis():
    def __init__(self, controller, axis_no, name):
        self.controller=controller
        self.lib=self.controller.lib
        self.axis_no=axis_no
        self.name=name
        self.status=0
        self.make_box()

    def getPos(self,navg=30):
        # time.sleep(0.01) #Might be unnecessary
        return self.lib.getPosition(axis=self.axis_no)/1e3 #returns in nm -> um

    def updatePos(self):
        pos=self.getPos()
        self.posLabel.setText(pos)

    def getCapa(self):
        # time.sleep(0.01) #Might be unnecessary
        capa=self.lib.capMeasure(axis=self.axis_no)/1e3 #returns in nF -> uF
        return capa

    def updateCapa(self):
        capa=self.getCapa()
        self.capaLabel.setText('%.3f \u03bcF'%(capa))

    def getFrequency(self):
        # time.sleep(0.01) #Might be unnecessary
        freq=self.lib.getFrequency(axis=self.axis_no)
        return freq

    def getAmplitude(self):
        # time.sleep(0.01) #Might be unnecessary
        amp=self.lib.getAmplitude(axis=self.axis_no)
        return amp

    def setFrequency(self,freq):
        self.lib.frequency(axis=self.axis_no,freq=freq)

    def setAmplitude(self,amp):
        self.lib.amplitude(axis=self.axis_no,amp=amp)

    def single_step(self,direction):
        if direction=='up':
            self.lib.moveSingleStep(axis=self.axis_no, direction=0)
        elif direction=='down':
            self.lib.moveSingleStep(axis=self.axis_no, direction=1)

    def start_continuous(self,direction):
        if direction=='up':
            self.lib.moveContinuous(axis=self.axis_no, direction=0)
        elif direction=='down':
            self.lib.moveContinuous(axis=self.axis_no, direction=1)

    def stop_continuous(self,direction):
        self.lib.stopMoving(axis=self.axis_no)

    def setOuput(self,state=False): #state=False: grounded, state=True: not grounded
        self.lib.setOutput(axis=self.axis_no,state=state)

    def make_box(self):
        self.label=label(self.name)
        self.label.setFont('big')
        self.posLabel=label('Off',precision=2)
        self.posLabel.setFont('big')

        self.displacementMode=dropDownMenu("Mode","Off","On",actionType="activated")
        self.displacementMode.setAction(self.menuAction)
        self.ledStatus=led(radius=30)
        self.boxMenu=box(self.displacementMode,self.ledStatus,typ='H')

        self.buttonStepUp=buttonWithLed(self.upButtonSymbol())
        self.buttonStepUp.setFont('big')
        self.buttonStepUp.setAction(lambda : self.upPressedAction(shift=False), actionType='pressed')
        self.buttonStepUp.setAction(lambda : self.upReleasedAction(shift=False),actionType='released')

        self.buttonStepDown=buttonWithLed(self.downButtonSymbol())
        self.buttonStepDown.setFont('big')
        self.buttonStepDown.setAction(lambda : self.downPressedAction(shift=False),actionType='pressed')
        self.buttonStepDown.setAction(lambda : self.downReleasedAction(shift=False),actionType='released')

        self.labelStep=label("Step")
        self.boxStep=box(self.labelStep,self.buttonStepDown,self.buttonStepUp,typ='H')

        self.buttonContinuousUp=buttonWithLed(self.upButtonSymbol())
        self.buttonContinuousUp.setFont('big')
        self.buttonContinuousUp.setAction(lambda : self.upPressedAction(shift=True), actionType='pressed')
        self.buttonContinuousUp.setAction(lambda : self.upReleasedAction(shift=True),actionType='released')
        

        self.buttonContinuousDown=buttonWithLed(self.downButtonSymbol())
        self.buttonContinuousDown.setFont('big')
        self.buttonContinuousDown.setAction(lambda : self.downPressedAction(shift=True),actionType='pressed')
        self.buttonContinuousDown.setAction(lambda : self.downReleasedAction(shift=True),actionType='released')

        self.labelContinuous=label("Cont")
        self.boxContinuous=box(self.labelContinuous,self.buttonContinuousDown,self.buttonContinuousUp,typ='H')

        self.boxArrows=box(self.boxStep,self.boxContinuous,typ='V')
        

        self.capaLabel=label("Off")
        self.capaLabel.setFont('big')

        self.boxArrowsAndChoice=box(self.boxMenu,self.boxArrows,self.capaLabel,typ="V")

        self.ampField=field("Amplitude (V)",'Off',precision=2)
        self.ampField.line.resize(20,50)
        self.ampField.setAction(self.ampFieldAction)

        self.freqField=field("Frequency (Hz)",'Off',precision=2)
        self.freqField.line.resize(20,50)
        self.freqField.setAction(self.freqFieldAction)

        self.boxAmpAndFreq=box(self.freqField,self.ampField,typ="V")

        self.boxDisplacement=box(self.boxArrowsAndChoice,self.boxAmpAndFreq,typ="H")
        self.panel=box(self.label,self.posLabel,self.boxDisplacement,typ='V')

    def initializeAxis(self):
        freq=self.getFrequency()
        amp=self.getAmplitude()
        self.freqField.setValue(freq)
        self.ampField.setValue(amp)

    def menuAction(self): #To add : grouding the axis when 'off'
        if self.displacementMode.text()=='Off':
            self.boxArrows.setEnabled(False)
            self.setOuput(False)
            self.status=0
            self.ledStatus.turnOff()
        elif self.controller.status==1:
            self.boxArrows.setEnabled(True)
            self.setOuput(True)
            self.status=1
            self.ledStatus.turnOn()

    def findMatchingSymbol(self,direction):
        if direction=='left':
            return '\u2190'
        elif direction=='right':
            return '\u2192'
        elif direction=='up':
            return '\u2191'
        elif direction=='down':
            return '\u2193'


    def upButtonSymbol(self):
        if self.name=='x-axis':
            return "%s (x\u2191)"%(self.findMatchingSymbol(direction=self.controller.orientation['xUp']))
        elif self.name=='y-axis':
            return "%s (y\u2191)"%(self.findMatchingSymbol(direction=self.controller.orientation['yUp']))
        elif self.name=='z-axis':
            return "\u219f (z\u2191)"
        

    def downButtonSymbol(self):
        if self.name=='x-axis':
            return "%s (x\u2193)"%(self.findMatchingSymbol(direction=self.controller.orientation['xDown']))
        elif self.name=='y-axis':
            return "%s (y\u2193)"%(self.findMatchingSymbol(direction=self.controller.orientation['yDown']))
        elif self.name=='z-axis':
            return "\u219f (z\u2193)"


    def upPressedAction(self,shift=False):
        if self.status:
            if shift:
                self.buttonContinuousUp.led.turnOn()
                self.start_continuous(direction='up')
            else:
                self.buttonStepUp.led.turnOn()
                self.single_step(direction='up')


    def upReleasedAction(self,shift=False):
        if self.status:
            if shift:
                self.buttonContinuousUp.led.turnOff()
                self.stop_continuous(direction='up')
            else:
                self.buttonStepUp.led.turnOff()
                self.stop_continuous(direction='up') #Additional protection


    def downPressedAction(self,shift=False):
        if self.status:
            if shift:
                self.buttonContinuousDown.led.turnOn()
                self.start_continuous(direction='down')
            else:
                self.buttonStepDown.led.turnOn()
                self.single_step(direction='down')


    def downReleasedAction(self,shift=False):
        if self.status:
            if shift:
                self.buttonContinuousDown.led.turnOff()
                self.stop_continuous(direction='down')
            else:
                self.buttonStepDown.led.turnOff()
                self.stop_continuous(direction='up') #Additional protection


    def ampFieldAction(self):
        self.setAmplitude(self.ampField.getValue())
        print("changed %s amp value to %f"%(self.name, self.ampField.getValue()))
        self.initializeAxis() #Checks that the change is taken into account

    def freqFieldAction(self):
        self.setFrequency(self.freqField.getValue())
        print("changed %s freq value to %f"%(self.name, self.freqField.getValue()))
        self.initializeAxis() #Checks that the change is taken into account



class ANC350GUI(Graphical_interface):
    def __init__(self, size='auto',stack='tip',lib=None):
        if stack=='tip':
            self.lib=Positioner() #Keeping the same nomenclature as for AttoDry
            self.lib.check()
            self.orientation=tipOrientation
            title='Tip steppers'
        elif stack=='sample':
            self.lib=lib
            self.orientation=sampleOrientation
            title='Sample steppers'
        self.controller=ANC350controller(lib=self.lib,stack=stack,controllerIdNumber=controllerIdNumber, orientation=self.orientation)
        super().__init__(self.controller.panel,size=size,title=title)
        self.setFocusPolicy(Qt.StrongFocus)# Required to not activate the fields with the keyboard arrows

    def findFunctionForArrowKey(self,arrowKey='up',pressed='released'):
        ori=list(self.orientation.keys())[list(self.orientation.values()).index(arrowKey)] #Find the orientation from the keyPressed in the dictionnary
        if ori=='xUp':
            if pressed=='pressed':
                return self.controller.x.upPressedAction
            elif pressed=='released':
                return self.controller.x.upReleasedAction
        elif ori=='xDown':
            if pressed=='pressed':
                return self.controller.x.downPressedAction
            elif pressed=='released':
                return self.controller.x.downReleasedAction
        elif ori=='yUp':
            if pressed=='pressed':
                return self.controller.y.upPressedAction
            elif pressed=='released':
                return self.controller.y.upReleasedAction
        elif ori=='yDown':
            if pressed=='pressed':
                return self.controller.y.downPressedAction
            elif pressed=='released':
                return self.controller.y.downReleasedAction
        

    def keyPressEvent(self,e):
        if e.key()==Qt.Key_Up and not e.isAutoRepeat(): #Without the autoRepeat clause, the key will keep being pressed and released when being maitained pressed
            action=self.findFunctionForArrowKey(arrowKey='up',pressed='pressed')
        elif e.key()==Qt.Key_Down and not e.isAutoRepeat():
            action=self.findFunctionForArrowKey(arrowKey='down',pressed='pressed')
        elif e.key()==Qt.Key_Right and not e.isAutoRepeat():
            action=self.findFunctionForArrowKey(arrowKey='right',pressed='pressed')
        elif e.key()==Qt.Key_Left and not e.isAutoRepeat():
            action=self.findFunctionForArrowKey(arrowKey='left',pressed='pressed')
        elif e.key()==Qt.Key_PageUp and not e.isAutoRepeat():
            action=self.controller.z.upPressedAction
        elif e.key()==Qt.Key_PageDown and not e.isAutoRepeat():
            action=self.controller.z.downPressedAction
        else :
            return
        
        if qapp.focusWidget()==self: #Additional security : can only be activated when the focus is on the main window (aka when the background color has changed)
            action(shift=e.modifiers()==Qt.ShiftModifier)

    def keyReleaseEvent(self,e):
        if e.key()==Qt.Key_Up and not e.isAutoRepeat(): #Without the autoRepeat clause, the key will keep being pressed and released when being maitained pressed
            action=self.findFunctionForArrowKey(arrowKey='up',pressed='released')
        elif e.key()==Qt.Key_Down and not e.isAutoRepeat():
            action=self.findFunctionForArrowKey(arrowKey='down',pressed='released')
        elif e.key()==Qt.Key_Right and not e.isAutoRepeat():
            action=self.findFunctionForArrowKey(arrowKey='right',pressed='released')
        elif e.key()==Qt.Key_Left and not e.isAutoRepeat():
            action=self.findFunctionForArrowKey(arrowKey='left',pressed='released')
        elif e.key()==Qt.Key_PageUp and not e.isAutoRepeat():
            action=self.controller.z.upReleasedAction
        elif e.key()==Qt.Key_PageDown and not e.isAutoRepeat():
            action=self.controller.z.downReleasedAction
        else :
            return
        action(shift=e.modifiers()==Qt.ShiftModifier)

    def closeEvent(self, event):
        try:
            self.controller.disconnect()
        except:
            pass
        return super().closeEvent(event)




if __name__ == "__main__":
    GUI1=ANC350GUI(stack='tip')
    GUI2=ANC350GUI(stack='sample',lib=GUI1.lib)
    GUI1.controller.connectButton.setAction(GUI2.controller.connect) # This action is added to the connect of GUI1
    GUI1.controller.disconnectButton.setAction(GUI2.controller.disconnect)
    GUI1.setBackGroundColor('palette(midlight)')
    GUI2.setBackGroundColor('palette(midlight)')
    def changeColorWhenInFocus(oldWidget,newWidget):
        if newWidget==GUI1 or newWidget==GUI2 :
            if newWidget.controller.checkAxisStatus() :
                newWidget.setBackGroundColor('bisque')
        if oldWidget==GUI1 or oldWidget==GUI2 :
            oldWidget.setBackGroundColor('palette(midlight)')
            if oldWidget.controller.checkAxisStatus() :
                oldWidget.controller.stop_all_motion()
    qapp.focusChanged.connect(changeColorWhenInFocus)
    GUI1.run()
