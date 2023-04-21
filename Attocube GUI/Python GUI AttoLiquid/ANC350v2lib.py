#
#  ANC350lib is a Python implementation of the C++ header provided
#     with the attocube ANC350 closed-loop positioner system.
#
#  It depends on hvpositionerv2.dll which is provided by attocube in the
#     ANC350_DLL folders on the driver disc.
#     This in turn requires nhconnect.dll and libusb0.dll. Place all
#     of these in the same folder as this module (and that of ANC350lib).
#
#                ANC350lib is written by Rob Heath
#                      rob@robheath.me.uk
#                         24-Feb-2015
#                       robheath.me.uk
#
#    v1.1: corrected POINTER used in intEnable (!!)
#


import ctypes, os, time, glob
#
# List of error types
#

NCB_Ok = 0 #                    No error
NCB_Error = -1 #                Unknown / other error
NCB_Timeout = 1 #               Timeout during data retrieval
NCB_NotConnected = 2 #          No contact with the positioner via USB
NCB_DriverError = 3 #           Error in the driver response
NCB_BootIgnored	= 4 #           Ignored boot, equipment was already running
NCB_FileNotFound = 5 #          Boot image not found
NCB_InvalidParam = 6 #          Transferred parameter is invalid
NCB_DeviceLocked = 7 #          A connection attempt failed because the device is already in use
NCB_NotSpecifiedParam = 8 #     Transferred parameter is out of specification


#checks the errors returned from the dll
def checkError(code, func, args):
	if code == NCB_Ok:
		return
	elif code == NCB_BootIgnored:
		print("Warning: boot ignored in", func.__name__, "with parameters:", args)
		return
	elif code == NCB_Error:
		raise Exception("Error: unspecific in" + str(func.__name__) + "with parameters:" + str(args))
	elif code == NCB_Timeout:
		raise Exception("Error: comm. timeout in" + str(func.__name__) + "with parameters:" + str(args))
	elif code == NCB_NotConnected:
		raise Exception("Error: not connected")
	elif code == NCB_DriverError:
		raise Exception("Error: driver error")
	elif code == NCB_FileNotFound:
		raise Exception("Error: file not found")
	elif code == NCB_InvalidParam:
		raise Exception("Error: invalid parameter")
	elif code == NCB_DeviceLocked:
		raise Exception("Error: device locked")
	elif code == NCB_NotSpecifiedParam:
		raise Exception("Error: unspec. parameter in" + str(func.__name__) + "with parameters:" + str(args))
	else:
		raise Exception("Error: unknown in" + str(func.__name__) + "with parameters:" + str(args))
	return code

# import dll
directory_of_this_module_and_dlls = os.path.dirname(os.path.realpath(__file__))
current_directory = os.getcwd()
os.chdir(directory_of_this_module_and_dlls)
# print(glob.glob(directory_of_this_module_and_dlls+'/*'))
hvpositionerv2 = ctypes.windll.LoadLibrary(directory_of_this_module_and_dlls + "\\hvpositionerv2.dll")

# creates alias for c_int as "Int32"
Int32 = ctypes.c_int32

#structure for PositionerInfo to handle positionerCheck return data
class PositionerInfo(ctypes.Structure):
	_fields_ = [("id",Int32),
				("locked",ctypes.c_bool)]

#aliases for the strangely-named functions from the dll
positionerAcInEnable = getattr(hvpositionerv2,"PositionerAcInEnable")
positionerAmplitude = getattr(hvpositionerv2,"PositionerAmplitude")
positionerAmplitudeControl = getattr(hvpositionerv2,"PositionerAmplitudeControl")
positionerBandwidthLimitEnable = getattr(hvpositionerv2,"PositionerBandwidthLimitEnable")
positionerCapMeasure = getattr(hvpositionerv2,"PositionerCapMeasure")
positionerCheck = getattr(hvpositionerv2,"PositionerCheck")
positionerClearStopDetection = getattr(hvpositionerv2,"PositionerClearStopDetection")
positionerClose = getattr(hvpositionerv2,"PositionerClose")
positionerConnect = getattr(hvpositionerv2,"PositionerConnect")
positionerDcInEnable = getattr(hvpositionerv2,"PositionerDcInEnable")
positionerDCLevel = getattr(hvpositionerv2,"PositionerDCLevel")
positionerDutyCycleEnable = getattr(hvpositionerv2,"PositionerDutyCycleEnable")
positionerDutyCycleOffTime = getattr(hvpositionerv2,"PositionerDutyCycleOffTime")
positionerDutyCyclePeriod = getattr(hvpositionerv2,"PositionerDutyCyclePeriod")
positionerExternalStepBkwInput = getattr(hvpositionerv2,"PositionerExternalStepBkwInput")
positionerExternalStepFwdInput = getattr(hvpositionerv2,"PositionerExternalStepFwdInput")
positionerExternalStepInputEdge = getattr(hvpositionerv2,"PositionerExternalStepInputEdge")
positionerFrequency = getattr(hvpositionerv2,"PositionerFrequency")
positionerGetAcInEnable = getattr(hvpositionerv2,"PositionerGetAcInEnable")
positionerGetAmplitude = getattr(hvpositionerv2,"PositionerGetAmplitude")
positionerGetBandwidthLimitEnable = getattr(hvpositionerv2,"PositionerGetBandwidthLimitEnable")
positionerGetDcInEnable = getattr(hvpositionerv2,"PositionerGetDcInEnable")
positionerGetDcLevel = getattr(hvpositionerv2,"PositionerGetDcLevel")
positionerGetFrequency = getattr(hvpositionerv2,"PositionerGetFrequency")
positionerGetIntEnable = getattr(hvpositionerv2,"PositionerGetIntEnable")
positionerGetPosition = getattr(hvpositionerv2,"PositionerGetPosition")
positionerGetReference = getattr(hvpositionerv2,"PositionerGetReference")
positionerGetReferenceRotCount = getattr(hvpositionerv2,"PositionerGetReferenceRotCount")
positionerGetRotCount = getattr(hvpositionerv2,"PositionerGetRotCount")
positionerGetSpeed = getattr(hvpositionerv2,"PositionerGetSpeed")
positionerGetStatus = getattr(hvpositionerv2,"PositionerGetStatus")
positionerGetStepwidth = getattr(hvpositionerv2,"PositionerGetStepwidth")
positionerIntEnable = getattr(hvpositionerv2,"PositionerIntEnable")
positionerLoad = getattr(hvpositionerv2,"PositionerLoad")
positionerMoveAbsolute = getattr(hvpositionerv2,"PositionerMoveAbsolute")
positionerMoveAbsoluteSync = getattr(hvpositionerv2,"PositionerMoveAbsoluteSync")
positionerMoveContinuous = getattr(hvpositionerv2,"PositionerMoveContinuous")
positionerMoveReference = getattr(hvpositionerv2,"PositionerMoveReference")
positionerMoveRelative = getattr(hvpositionerv2,"PositionerMoveRelative")
positionerMoveSingleStep = getattr(hvpositionerv2,"PositionerMoveSingleStep")
positionerQuadratureAxis = getattr(hvpositionerv2,"PositionerQuadratureAxis")
positionerQuadratureInputPeriod = getattr(hvpositionerv2,"PositionerQuadratureInputPeriod")
positionerQuadratureOutputPeriod = getattr(hvpositionerv2,"PositionerQuadratureOutputPeriod")
positionerResetPosition = getattr(hvpositionerv2,"PositionerResetPosition")
positionerSensorPowerGroupA = getattr(hvpositionerv2,"PositionerSensorPowerGroupA")
positionerSensorPowerGroupB = getattr(hvpositionerv2,"PositionerSensorPowerGroupB")
positionerSetHardwareId = getattr(hvpositionerv2,"PositionerSetHardwareId")
positionerSetOutput = getattr(hvpositionerv2,"PositionerSetOutput")
positionerSetStopDetectionSticky = getattr(hvpositionerv2,"PositionerSetStopDetectionSticky")
positionerSetTargetGround = getattr(hvpositionerv2,"PositionerSetTargetGround")
positionerSetTargetPos = getattr(hvpositionerv2,"PositionerSetTargetPos")
positionerSingleCircleMode = getattr(hvpositionerv2,"PositionerSingleCircleMode")
positionerStaticAmplitude = getattr(hvpositionerv2,"PositionerStaticAmplitude")
positionerStepCount = getattr(hvpositionerv2,"PositionerStepCount")
positionerStopApproach = getattr(hvpositionerv2,"PositionerStopApproach")
positionerStopDetection = getattr(hvpositionerv2,"PositionerStopDetection")
positionerStopMoving = getattr(hvpositionerv2,"PositionerStopMoving")
positionerTrigger = getattr(hvpositionerv2,"PositionerTrigger")
positionerTriggerAxis = getattr(hvpositionerv2,"PositionerTriggerAxis")
positionerTriggerEpsilon = getattr(hvpositionerv2,"PositionerTriggerEpsilon")
positionerTriggerModeIn = getattr(hvpositionerv2,"PositionerTriggerModeIn")
positionerTriggerModeOut = getattr(hvpositionerv2,"PositionerTriggerModeOut")
positionerTriggerPolarity = getattr(hvpositionerv2,"PositionerTriggerPolarity")
positionerUpdateAbsolute = getattr(hvpositionerv2,"PositionerUpdateAbsolute")

#set error checking & handling
positionerAcInEnable.errcheck = checkError
positionerAmplitude.errcheck = checkError
positionerAmplitudeControl.errcheck = checkError
positionerBandwidthLimitEnable.errcheck = checkError
positionerCapMeasure.errcheck = checkError
positionerClearStopDetection.errcheck = checkError
positionerClose.errcheck = checkError
positionerConnect.errcheck = checkError
positionerDcInEnable.errcheck = checkError
positionerDCLevel.errcheck = checkError
positionerDutyCycleEnable.errcheck = checkError
positionerDutyCycleOffTime.errcheck = checkError
positionerDutyCyclePeriod.errcheck = checkError
positionerExternalStepBkwInput.errcheck = checkError
positionerExternalStepFwdInput.errcheck = checkError
positionerExternalStepInputEdge.errcheck = checkError
positionerFrequency.errcheck = checkError
positionerGetAcInEnable.errcheck = checkError
positionerGetAmplitude.errcheck = checkError
positionerGetBandwidthLimitEnable.errcheck = checkError
positionerGetDcInEnable.errcheck = checkError
positionerGetDcLevel.errcheck = checkError
positionerGetFrequency.errcheck = checkError
positionerGetIntEnable.errcheck = checkError
positionerGetPosition.errcheck = checkError
positionerGetReference.errcheck = checkError
positionerGetReferenceRotCount.errcheck = checkError
positionerGetRotCount.errcheck = checkError
positionerGetSpeed.errcheck = checkError
positionerGetStatus.errcheck = checkError
positionerGetStepwidth.errcheck = checkError
positionerIntEnable.errcheck = checkError
positionerLoad.errcheck = checkError
positionerMoveAbsolute.errcheck = checkError
positionerMoveAbsoluteSync.errcheck = checkError
positionerMoveContinuous.errcheck = checkError
positionerMoveReference.errcheck = checkError
positionerMoveRelative.errcheck = checkError
positionerMoveSingleStep.errcheck = checkError
positionerQuadratureAxis.errcheck = checkError
positionerQuadratureInputPeriod.errcheck = checkError
positionerQuadratureOutputPeriod.errcheck = checkError
positionerResetPosition.errcheck = checkError
positionerSensorPowerGroupA.errcheck = checkError
positionerSensorPowerGroupB.errcheck = checkError
positionerSetHardwareId.errcheck = checkError
positionerSetOutput.errcheck = checkError
positionerSetStopDetectionSticky.errcheck = checkError
positionerSetTargetGround.errcheck = checkError
positionerSetTargetPos.errcheck = checkError
positionerSingleCircleMode.errcheck = checkError
positionerStaticAmplitude.errcheck = checkError
positionerStepCount.errcheck = checkError
positionerStopApproach.errcheck = checkError
positionerStopDetection.errcheck = checkError
positionerStopMoving.errcheck = checkError
positionerTrigger.errcheck = checkError
positionerTriggerAxis.errcheck = checkError
positionerTriggerEpsilon.errcheck = checkError
positionerTriggerModeIn.errcheck = checkError
positionerTriggerModeOut.errcheck = checkError
positionerTriggerPolarity.errcheck = checkError
positionerUpdateAbsolute.errcheck = checkError
#positionerCheck.errcheck = checkError
#positionerCheck returns number of attached devices; gives "comms error" if this is applied, despite working fine

#set argtypes
positionerAcInEnable.argtypes = [Int32, Int32, ctypes.c_bool]
positionerAmplitude.argtypes = [Int32, Int32, Int32]
positionerAmplitudeControl.argtypes = [Int32, Int32, Int32]
positionerBandwidthLimitEnable.argtypes = [Int32, Int32, ctypes.c_bool]
positionerCapMeasure.argtypes = [Int32, Int32, ctypes.POINTER(Int32)]
positionerCheck.argtypes = [ctypes.POINTER(PositionerInfo)]
positionerClearStopDetection.argtypes = [Int32, Int32]
positionerClose.argtypes = [Int32]
positionerConnect.argtypes = [Int32, ctypes.POINTER(Int32)]
positionerDcInEnable.argtypes = [Int32, Int32, ctypes.c_bool]
positionerDCLevel.argtypes = [Int32, Int32, Int32]
positionerDutyCycleEnable.argtypes = [Int32, ctypes.c_bool]
positionerDutyCycleOffTime.argtypes = [Int32, Int32]
positionerDutyCyclePeriod.argtypes = [Int32, Int32]
positionerExternalStepBkwInput.argtypes = [Int32, Int32, Int32]
positionerExternalStepFwdInput.argtypes = [Int32, Int32, Int32]
positionerExternalStepInputEdge.argtypes = [Int32, Int32, Int32]
positionerFrequency.argtypes = [Int32, Int32, Int32]
positionerGetAcInEnable.argtypes = [Int32, Int32, ctypes.POINTER(ctypes.c_bool)]
positionerGetAmplitude.argtypes = [Int32, Int32, ctypes.POINTER(Int32)]
positionerGetBandwidthLimitEnable.argtypes = [Int32, Int32, ctypes.POINTER(ctypes.c_bool)]
positionerGetDcInEnable.argtypes = [Int32, Int32, ctypes.POINTER(ctypes.c_bool)]
positionerGetDcLevel.argtypes = [Int32, Int32, ctypes.POINTER(Int32)]
positionerGetFrequency.argtypes = [Int32, Int32, ctypes.POINTER(Int32)]
positionerGetIntEnable.argtypes = [Int32, Int32, ctypes.POINTER(ctypes.c_bool)]
positionerGetPosition.argtypes = [Int32, Int32, ctypes.POINTER(Int32)]
positionerGetReference.argtypes = [Int32, Int32, ctypes.POINTER(Int32), ctypes.POINTER(ctypes.c_bool)]
positionerGetReferenceRotCount.argtypes = [Int32, Int32, ctypes.POINTER(Int32)]
positionerGetRotCount.argtypes = [Int32, Int32, ctypes.POINTER(Int32)]
positionerGetSpeed.argtypes = [Int32, Int32, ctypes.POINTER(Int32)]
positionerGetStatus.argtypes = [Int32, Int32, ctypes.POINTER(Int32)]
positionerGetStepwidth.argtypes = [Int32, Int32, ctypes.POINTER(Int32)]
positionerIntEnable.argtypes = [Int32, Int32, ctypes.c_bool]
positionerLoad.argtypes = [Int32, Int32, ctypes.POINTER(ctypes.c_char)]
positionerMoveAbsolute.argtypes = [Int32, Int32, Int32, Int32]
positionerMoveAbsoluteSync.argtypes = [Int32, Int32]
positionerMoveContinuous.argtypes = [Int32, Int32, Int32]
positionerMoveReference.argtypes = [Int32, Int32]
positionerMoveRelative.argtypes = [Int32, Int32, Int32, Int32]
positionerMoveSingleStep.argtypes = [Int32, Int32, Int32]
positionerQuadratureAxis.argtypes = [Int32, Int32, Int32]
positionerQuadratureInputPeriod.argtypes = [Int32, Int32, Int32]
positionerQuadratureOutputPeriod.argtypes = [Int32, Int32, Int32]
positionerResetPosition.argtypes = [Int32, Int32]
positionerSensorPowerGroupA.argtypes = [Int32, ctypes.c_bool]
positionerSensorPowerGroupB.argtypes = [Int32, ctypes.c_bool]
positionerSetHardwareId.argtypes = [Int32, Int32]
positionerSetOutput.argtypes = [Int32, Int32, ctypes.c_bool]
positionerSetStopDetectionSticky.argtypes = [Int32, Int32, ctypes.c_bool]
positionerSetTargetGround.argtypes = [Int32, Int32, ctypes.c_bool]
positionerSetTargetPos.argtypes = [Int32, Int32, Int32, Int32]
positionerSingleCircleMode.argtypes = [Int32, Int32, ctypes.c_bool]
positionerStaticAmplitude.argtypes = [Int32, Int32]
positionerStepCount.argtypes = [Int32, Int32, Int32]
positionerStopApproach.argtypes = [Int32, Int32]
positionerStopDetection.argtypes = [Int32, Int32, ctypes.c_bool]
positionerStopMoving.argtypes = [Int32, Int32]
positionerTrigger.argtypes = [Int32, Int32, Int32, Int32]
positionerTriggerAxis.argtypes = [Int32, Int32, Int32]
positionerTriggerEpsilon.argtypes = [Int32,Int32, Int32]
positionerTriggerModeIn.argtypes = [Int32, Int32]
positionerTriggerModeOut.argtypes = [Int32, Int32]
positionerTriggerPolarity.argtypes = [Int32, Int32, Int32]
positionerUpdateAbsolute.argtypes = [Int32, Int32, Int32]
