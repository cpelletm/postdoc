#
#  PyANC350 is a control scheme suitable for the Python coding style
#    for the attocube ANC350 closed-loop positioner system.
#
#  It implements ANC350v2lib, which in turn depends on anc350v2.dll
#    which is provided by attocube in the ANC350_DLL folders
#    on the driver disc.
#    This in turn requires nhconnect.dll and libusb0.dll. Place all
#    of these in the same folder as this module (and that of ANC350v2lib).
#
#  Unlike ANC350v2lib which is effectively a re-imagining of the
#    C++ header, PyANC350 is intended to behave as one might expect
#    Python to. This means: returning values; behaving as an object.
#
#  At present this only addresses the first ANC350 connected to the
#    machine.
#
#  Usage:
#  1. instantiate Positioner() class to begin, eg. pos = Positioner().
#  2. methods from the ANC350v2 documentation are implemented such that
#      function PositionerGetPosition(handle, axis, &pos)
#      becomes position = pos.getPosition(axis),
#      PositionerCapMeasure(handle,axis,&cap) becomes
#      cap = pos.capMeasure(axis), and so on. Return code handling is
#      within ANC350v2lib.
#  3. bitmask() and debitmask() functions have been added for
#      convenience when using certain functions
#      (e.g. getStatus,moveAbsoluteSync)
#  4. for tidiness remember to Positioner.close() when finished!
#
#                PyANC350 is written by Rob Heath
#                      rob@robheath.me.uk
#                         24-Feb-2015
#                       robheath.me.uk

import ANC350v2lib as ANC
import ctypes, math
import time

class Positioner:
    def __init__(self):
        pass
        # self.check()
        # self.connect()

    def acInEnable(self, axis, state):
        '''
        Activates/deactivates AC input of addressed axis; only applicable for dither axes
        '''
        ANC.positionerAcInEnable(self.handle,axis,ctypes.c_bool(state))

    def amplitude(self, axis, amp):
        '''
        set the amplitude setpoint in V
        '''
        ANC.positionerAmplitude(self.handle, axis, ANC.Int32(int(1000 * amp)))

    def amplitudeControl(self, axis, mode):
        '''
        selects the type of amplitude control.
        The amplitude is controlled by the positioner to hold the value constant
        determined by the selected type of amplitude control.
        mode takes values 0: speed, 1: amplitude, 2: step size
        '''
        ANC.positionerAmplitudeControl(self.handle, axis, mode)

    def bandwidthLimitEnable(self, axis, state):
        '''
        activates/deactivates the bandwidth limiter of the addressed axis.
        only applicable for scanner axes
        '''
        ANC.positionerBandwidthLimitEnable(self.handle,axis,ctypes.c_bool(state))

    def capMeasure(self, axis):
        '''
        determines the capacitance of the piezo addressed by axis
        '''
        self.status = ANC.Int32(0)
        ANC.positionerCapMeasure(self.handle, axis, ctypes.byref(self.status))
        return self.status.value

    def check(self):
        '''
        Determines number of connected positioners and their respective hardware IDs
        '''
        self.posinf = ANC.PositionerInfo() #create PositionerInfo Struct
        self.numconnected = ANC.positionerCheck(ctypes.byref(self.posinf)) #look for positioners!
        print("number of devices found: " +str(self.numconnected))
        if self.numconnected > 0:
            print(self.numconnected, 'ANC350 connected')
            print('ANC350 with id:', self.posinf.id, 'has locked state:', self.posinf.locked)

    def clearStopDetection(self, axis):
        '''
        when .setStopDetectionSticky() is enabled, this clears the stop detection status
        '''
        ANC.positionerClearStopDetection(self.handle,axis)

    def close(self):
        '''
        closes connection to ANC350 device
        '''
        ANC.positionerClose(self.handle)

    def connect(self, device_no=0):
        '''
        Establishes connection to first device found
        '''
        print('connecting to device no %i'%device_no)
        self.handle = ANC.Int32(0)
        try:
            ANC.positionerConnect(device_no,ctypes.byref(self.handle)) #0 means "first device"
            # print('connected to first positioner')
        except Exception as e:
            print('unable to connect!')
            raise e

    def dcInEnable(self, axis, state):
        '''
        Activates/deactivates DC input of addressed axis; only applicable for scanner/dither axes
        '''
        ANC.positionerDcInEnable(self.handle, axis, ctypes.c_bool(state))

    def dcLevel(self, axis, dclev):
        '''
        sets the dc level of selected axis. dclevel in V
        '''

        ANC.positionerDCLevel(self.handle, axis, ANC.Int32(int(1000 * dclev)))

    def dutyCycleEnable(self, state):
        '''
        controls duty cycle mode
        '''
        ANC.positionerDutyCycleEnable(self.handle, ctypes.c_bool(state))

    def dutyCycleOffTime(self, value):
        '''
        sets duty cycle off time
        '''
        ANC.positionerDutyCycleOffTime(self.handle, value)

    def dutyCyclePeriod(self, value):
        '''
        sets duty cycle period
        '''
        ANC.positionerDutyCyclePeriod(self.handle, value)

    def externalStepBkwInput(self, axis, input_trigger):
        '''
        configures external step trigger input for selected axis. a trigger on this input results in a backwards single step. input_trigger: 0 disabled, 1-6 input trigger
        '''
        ANC.positionerExternalStepBkwInput(self.handle, axis, input_trigger)

    def externalStepFwdInput(self, axis, input_trigger):
        '''
        configures external step trigger input for selected axis. a trigger on this input results in a forward single step. input_trigger: 0 disabled, 1-6 input trigger
        '''
        ANC.positionerExternalStepFwdInput(self.handle, axis, input_trigger)

    def externalStepInputEdge(self, axis, edge):
        '''
        configures edge sensitivity of external step trigger input for selected axis. edge: 0 rising, 1 falling
        '''
        ANC.positionerExternalStepInputEdge(self.handle, axis, edge)

    def frequency(self, axis, freq):
        '''
        sets the frequency of selected axis. frequency in Hz
        '''
        ANC.positionerFrequency(self.handle, axis, ANC.Int32(int(freq)))

    def getAcInEnable(self, axis):
        '''
        determines status of ac input of addressed axis. only applicable for dither axes
        '''
        self.status = ctypes.c_bool(None)
        ANC.positionerGetAcInEnable(self.handle,axis,ctypes.byref(self.status))
        return self.status.value

    def getAmplitude(self, axis):
        '''
        determines the actual amplitude in V. In case of standstill of the actor this
        is the amplitude setpoint. In case of movement the amplitude set by
        amplitude control is determined.
        '''
        self.status = ANC.Int32(0)
        ANC.positionerGetAmplitude(self.handle, axis, ctypes.byref(self.status))
        return self.status.value / 1000

    def getBandwidthLimitEnable(self, axis):
        '''
        determines status of bandwidth limiter of addressed axis. only applicable for scanner axes
        '''
        self.status = ctypes.c_bool(None)
        ANC.positionerGetBandwidthLimitEnable(self.handle, axis, ctypes.byref(self.status))
        return self.status.value

    def getDcInEnable(self, axis):
        '''
        determines status of dc input of addressed axis. only applicable for scanner/dither axes
        '''
        self.status = ctypes.c_bool(None)
        ANC.positionerGetDcInEnable(self.handle,axis,ctypes.byref(self.status))
        return self.status.value

    def getDcLevel(self, axis):
        '''
        determines the status actual DC level in V
        '''
        self.dclev = ANC.Int32(0)
        ANC.positionerGetDcLevel(self.handle, axis, ctypes.byref(self.dclev))
        return self.dclev.value / 1000

    def getFrequency(self, axis):
        '''
        determines the frequency in Hz
        '''
        self.freq = ANC.Int32(0)
        ANC.positionerGetFrequency(self.handle, axis, ctypes.byref(self.freq))
        return self.freq.value

    def getIntEnable(self, axis):
        '''
        determines status of internal signal generation of addressed axis.
        only applicable for scanner/dither axes
        '''
        self.status = ctypes.c_bool(None)
        ANC.positionerGetIntEnable(self.handle, axis, ctypes.byref(self.status))
        return self.status.value

    def getPosition(self, axis):
        '''
        determines actual position of addressed axis
        '''
        self.pos = ANC.Int32(0)
        ANC.positionerGetPosition(self.handle, axis, ctypes.byref(self.pos))
        return self.pos.value

    def getReference(self, axis):
        '''
        determines distance of reference mark to origin
        '''
        self.pos = ANC.Int32(0)
        self.validity = ctypes.c_bool(None)
        ANC.positionerGetReference(self.handle, axis, ctypes.byref(self.pos), ctypes.byref(self.validity))
        return self.pos.value, self.validity.value

    def getReferenceRotCount(self, axis):
        '''
        determines actual position of addressed axis
        '''
        self.rotcount = ANC.Int32(0)
        ANC.positionerGetReferenceRotCount(self.handle, axis, ctypes.byref(self.rotcount))
        return self.rotcount.value

    def getRotCount(self, axis):
        '''
        determines actual number of rotations in case of rotary actuator
        '''
        self.rotcount = ANC.Int32(0)
        ANC.positionerGetRotCount(self.handle, axis, ctypes.byref(self.rotcount))
        return self.rotcount.value

    def getSpeed(self, axis):
        '''
        determines the actual speed. In case of standstill of this actor this is the calculated speed resulting	from amplitude setpoint, frequency, and motor parameters. In case of movement this is measured speed.
        '''
        self.spd = ANC.Int32(0)
        ANC.positionerGetSpeed(self.handle, axis, ctypes.byref(self.spd))
        return self.spd.value

    def getStatus(self, axis):
        '''
        determines the status of the selected axis.
        result: bit0 (moving), bit1 (stop detected), bit2 (sensor error), bit3 (sensor disconnected)
        '''
        self.status = ANC.Int32(0)
        ANC.positionerGetStatus(self.handle, axis, ctypes.byref(self.status))
        return self.status.value

    def getStepwidth(self, axis):
        '''
        determines the step width. In case of standstill of the motor this
        is the calculated step width resulting from amplitude setpoint,
        frequency, and motor parameters. In case of movement this is measured
        step width
        '''
        self.stepwdth = ANC.Int32(0)
        ANC.positionerGetStepwidth(self.handle, axis, ctypes.byref(self.stepwdth))
        return self.stepwdth.value

    def intEnable(self, axis, state):
        '''
        Activates/deactivates internal signal generation of addressed axis; only applicable for scanner/dither axes
        '''
        ANC.positionerIntEnable(self.handle, axis, ctypes.c_bool(state))

    def load(self, axis, filename):
        '''
        loads a parameter file for actor configuration.	note: this requires a pointer to a char datatype. having no parameter file to test, I have no way of telling whether this will work, especially with the manual being as erroneous as it is. as such, use at your own (debugging) risk!
        '''
        ANC.positionerLoad(self.handle, axis, ctypes.byref(ctypes.char(filename)))

    def moveAbsolute(self, axis, position, rotcount=0):
        '''
        starts approach to absolute target position. previous movement will be stopped. rotcount optional argument position units are in 'unit of actor multiplied by 1000' (generally nanometres)
        '''
        ANC.positionerMoveAbsolute(self.handle, axis, position, rotcount)

    def moveAbsoluteSync(self, bitmask_of_axes):
        '''
        starts the synchronous approach to absolute target position for selected axis. previous movement will be stopped. target position for each axis defined by .setTargetPos() takes a *bitmask* of axes!
        '''
        ANC.positionerMoveAbsoluteSync(self.handle, bitmask_of_axes)

    def moveContinuous(self, axis, direction):
        '''
        starts continuously positioning with set parameters for ampl and speed and amp control respectively. direction can be 0 (forward) or 1 (backward)
        '''
        ANC.positionerMoveContinuous(self.handle, axis, ANC.Int32(direction))

    def moveReference(self, axis):
        '''
        starts approach to reference position. previous movement will be stopped.
        '''
        ANC.positionerMoveReference(self.handle, axis)

    def moveRelative(self, axis, position, rotcount=0):
        '''
        starts approach to relative target position.
        previous movement will be stopped. rotcount optional argument.
        position units are in 'unit of actor multiplied by 1000' (generally nanometres)
        '''
        ANC.positionerMoveRelative(self.handle, axis, position, rotcount)

    def moveSingleStep(self, axis, direction):
        '''
        starts a one-step positioning.
        Previous movement will be stopped. direction can be 0 (forward) or 1 (backward)
        '''
        ANC.positionerMoveSingleStep(self.handle, axis, ANC.Int32(direction))

    def quadratureAxis(self, quadratureno, axis):
        '''
        selects the axis for use with this trigger in/out pair.
        quadratureno: number of addressed quadrature unit (0-2)
        '''
        ANC.positionerQuadratureAxis(self.handle, quadratureno, axis)

    def quadratureInputPeriod(self, quadratureno, period):
        '''
        selects the stepsize the controller executes when detecting a step on
        its input AB-signal.
        quadratureno: number of addressed quadrature unit (0-2).
        period: stepsize in unit of actor * 1000
        '''
        ANC.positionerQuadratureInputPeriod(self.handle, quadratureno, period)

    def quadratureOutputPeriod(self, quadratureno, period):
        '''
        selects the position difference which causes a step on the output AB-signal.
        quadratureno: number of addressed quadrature unit (0-2).
        period: period in unit of actor * 1000
        '''
        ANC.positionerQuadratureOutputPeriod(self.handle, quadratureno, period)

    def resetPosition(self, axis):
        '''
        sets the origin to the actual position
        '''
        ANC.positionerResetPosition(self.handle, axis)

    def sensorPowerGroupA(self, state):
        '''
        switches power of sensor group A. Sensor group A contains either the
        sensors of axis 1-3 or 1-2 dependent on hardware of controller
        '''
        ANC.positionerSensorPowerGroupA(self.handle, ctypes.c_bool(state))

    def sensorPowerGroupB(self, state):
        '''
        switches power of sensor group B. Sensor group B contains either the
        sensors of axis 4-6 or 3 dependent on hardware of controller
        '''
        ANC.positionerSensorPowerGroupB(self.handle, ctypes.c_bool(state))

    def setHardwareId(self, hwid):
        '''
        sets the hardware ID for the device (used to differentiate multiple devices)
        '''
        ANC.positionerSetHardwareId(self.handle, hwid)

    def setOutput(self, axis, state):
        '''
        activates/deactivates the addressed axis
        '''
        ANC.positionerSetOutput(self.handle, axis, ctypes.c_bool(state))

    def setStopDetectionSticky(self, axis, state):
        '''
        when enabled, an active stop detection status remains active until
        cleared manually by .clearStopDetection()
        '''
        ANC.positionerSetStopDetectionSticky(self.handle, axis, state)

    def setTargetGround(self, axis, state):
        '''
        when enabled, actor voltage set to zero after closed-loop positioning finished
        '''
        ANC.positionerSetTargetGround(self.handle, axis, ctypes.c_bool(state))

    def setTargetPos(self, axis, pos, rotcount=0):
        '''
        sets target position for use with .moveAbsoluteSync()
        '''
        ANC.positionerSetTargetPos(self.handle, axis, pos, rotcount)

    def singleCircleMode(self, axis, state):
        '''
        switches single circle mode. In case of activated single circle mode
        the number of rotations are ignored and the shortest way to target
        position is used. Only relevant for rotary actors.
        '''
        ANC.positionerSingleCircleMode(self.handle, axis, ctypes.c_bool(state))

    def staticAmplitude(self, amp):
        '''
        sets output voltage for resistive sensors
        '''
        ANC.positionerStaticAmplitude(self.handle, amp)

    def stepCount(self, axis, stps):
        '''
        configures number of successive step scaused by external trigger or
        manual step request. steps = 1 to 65535
        '''
        ANC.positionerStepCount(self.handle, axis, stps)

    def stopApproach(self, axis):
        '''
        stops approaching target/relative/reference position. DC level of
        affected axis after stopping depends on setting by .setTargetGround()
        '''
        ANC.positionerStopApproach(self.handle, axis)

    def stopDetection(self, axis, state):
        '''
        switches stop detection on/off
        '''
        ANC.positionerStopDetection(self.handle, axis, ctypes.c_bool(state))

    def stopMoving(self, axis):
        '''
        stops any positioning, DC level of affected axis is set to zero after stopping.
        '''
        ANC.positionerStopMoving(self.handle, axis)

    def trigger(self, triggerno, lowlevel, highlevel):
        '''
        sets the trigger thresholds for the external trigger.
        triggerno is 0-5, lowlevel/highlevel in units of actor * 1000
        '''
        ANC.positionerTrigger(self.handle, triggerno, lowlevel, highlevel)

    def triggerAxis(self, triggerno, axis):
        '''
        selects the corresponding axis for the addressed trigger. triggerno is 0-5
        '''
        ANC.positionerTriggerAxis(self.handle, triggerno, axis)

    def triggerEpsilon(self, triggerno, epsilon):
        '''
        sets the hysteresis of the external trigger. epsilon in units of actor * 1000
        '''
        ANC.positionerTriggerEpsilon(self.handle, triggerno, epsilon)

    def triggerModeIn(self, mode):
        '''
        selects the mode of the input trigger signalsself.
        state:
            0 disabled - inputs trigger nothing,
            1 quadrature - three pairs of trigger in signals are used to accept
                AB-signals for relative positioning,
            2 coarse - trigger in signals are used to generate coarse steps
        '''
        ANC.positionerTriggerModeIn(self.handle, mode)

    def triggerModeOut(self, mode):
        '''
        selects the mode of the output trigger signals.
        state:
            0 disabled - inputs trigger nothing,
            1 position - the trigger outputs reacts to the defined position
                ranges with the selected polarity,
            2 quadrature - three pairs of trigger out signals are used to
                signal relative movement as AB-signals,
            3 IcHaus - the trigger out signals are used to output the internal
                position signal of num-sensors
        '''
        ANC.positionerTriggerModeOut(self.handle, mode)

    def triggerPolarity(self, triggerno, polarity):
        '''
        sets the polarity of the external trigger,
        triggerno: 0-5,
        polarity: 0 low active, 1 high active
        '''
        ANC.positionerTriggerPolarity(self.handle,triggerno,polarity)

    def updateAbsolute(self, axis, position):
        '''
        updates target position for a *running* approach.
        function has lower performance impact on running approach compared to
        .moveAbsolute(). position units are in 'unit of actor multiplied by 1000'
        (generally nanometres)
        '''
        ANC.positionerUpdateAbsolute(self.handle,axis,position)

def bitmask(input_array):
    '''
    takes an array or string and converts to integer bitmask;
    reads from left to right e.g. 0100 = 2 not 4
    '''
    total = 0
    for i in range(len(input_array)):
        if int(input_array[i]) != 0 and int(input_array[i])!=1:
            raise Exception('nonbinary value in bitmask, panic!')
        else:
            total += int(input_array[i])*(2**(i))
    return total

def debitmask(input_int,num_bits = False):
    '''
    takes a bitmask and returns a list of which bits are switched;
    reads from left to right e.g. 2 = [0, 1] not [1, 0]
    '''
    if num_bits == False and input_int>0:
        num_bits = int(math.ceil(math.log(input_int+1,2)))
    elif input_int == 0:
        return [0]

    result_array = [0] * num_bits
    for i in reversed(range(num_bits)):
        if input_int - 2**i >= 0:
            result_array[i] = 1
            input_int -= 2**i
    return result_array

if __name__ == "__main__":
    pos=Positioner()
    pos.check()
    pos.connect(device_no=1)
    for axis in range(6):
        print(pos.getPosition(axis=axis))
        time.sleep(0.01) #Needs to wait between each measurement ... Otherwise you get zeroes
    pos.setOutput(axis=3,state=True)
    time.sleep(1)
    pos.setOutput(axis=3,state=False)
    time.sleep(1)
    pos.setOutput(axis=3,state=False)
    pos.close()
    print(ANC.Int32(False).value)
