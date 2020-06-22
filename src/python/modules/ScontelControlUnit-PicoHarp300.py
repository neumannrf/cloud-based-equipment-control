# Access to Scontel Control Unit via PicoHarp 300 Hardware via PHLIB.DLL v 3.0.
# Ralph Krupke, KIT, May 2020

import time
import ctypes as ct
import numpy as np
from ctypes import byref, c_float, c_ushort, c_ubyte

phlib = ct.CDLL("C:\\Windows\\SysWOW64\\phlib.dll")
culib = ct.WinDLL("C:\\ControlUnit Toolset\\biasbox.dll")

# PicoHarp: from phdefin.h
LIB_VERSION = "3.0"
HISTCHAN = 65536
MAXDEVNUM = 8
MODE_HIST = 0
FLAG_OVERFLOW = 0x0040

# PicoHarp: define measurement parameters
binning = 0         # you can change this
offset = 0
tacq = 1000         # Measurement time in millisec, you can change this
syncDivider = 1     # you can change this
CFDZeroCross0 = 10  # you can change this (in mV)
CFDLevel0 = 50      # you can change this (in mV)
CFDZeroCross1 = 10  # you can change this (in mV)
CFDLevel1 = 30      # you can change this (in mV)
cmd = 0

# ScontelControlUnit: define measurement parameters
Detector = 0    # select detector 0 or 1
Istart = -20    # in uA
Istop = -21     # in uA
Istep = -0.2    # in uA
average = 1     # time average in s
steps = int((Istop-Istart)/Istep)+1

# PicoHarp: variables to store information read from PicoHarp DLL
dev = []
counts = (ct.c_uint * HISTCHAN)()
libVersion = ct.create_string_buffer(b"", 8)
hwSerial = ct.create_string_buffer(b"", 8)
hwPartno = ct.create_string_buffer(b"", 8)
hwVersion = ct.create_string_buffer(b"", 8)
hwModel = ct.create_string_buffer(b"", 16)
errorString = ct.create_string_buffer(b"", 40)
resolution = ct.c_double()
countRate0 = ct.c_int()
countRate1 = ct.c_int()
flags = ct.c_int()


# PicoHarp: functions
def closeDevices():
    for i in range(0, MAXDEVNUM):
        phlib.PH_CloseDevice(ct.c_int(i))
    exit(0)


def tryfunc(retcode, funcName):
    if retcode < 0:
        phlib.PH_GetErrorString(errorString, ct.c_int(retcode))
        print("PH_%s error %d (%s)!" % (funcName, retcode, errorString.value.decode("utf-8")))
        closeDevices()


phlib.PH_GetLibraryVersion(libVersion)
print("Library version is %s" % libVersion.value.decode("utf-8"))
if libVersion.value.decode("utf-8") != LIB_VERSION:
    print("Warning: The application was built for version %s" % LIB_VERSION)

# PicoHarp: write PicoHarp parameters to local file
outputfile = open("dlldemo.out", "w+")
outputfile.write("Binning           : %d\n" % binning)
outputfile.write("Offset            : %d\n" % offset)
outputfile.write("AcquisitionTime   : %d\n" % tacq)
outputfile.write("SyncDivider       : %d\n" % syncDivider)
outputfile.write("CFDZeroCross0     : %d\n" % CFDZeroCross0)
outputfile.write("CFDLevel0         : %d\n" % CFDLevel0)
outputfile.write("CFDZeroCross1     : %d\n" % CFDZeroCross1)
outputfile.write("CFDLevel1         : %d\n" % CFDLevel1)

# PicoHarp: search for PicoHarp devices and use first one
print("\nSearching for PicoHarp devices...")
print("Devidx     Status")

for i in range(0, MAXDEVNUM):
    retcode = phlib.PH_OpenDevice(ct.c_int(i), hwSerial)
    if retcode == 0:
        print("  %1d        S/N %s" % (i, hwSerial.value.decode("utf-8")))
        dev.append(i)
    else:
        if retcode == -1:   # ERROR_DEVICE_OPEN_FAIL
            print("  %1d        no device" % i)
        else:
            phlib.PH_GetErrorString(errorString, ct.c_int(retcode))
            print("  %1d        %s" % (i, errorString.value.decode("utf8")))

if len(dev) < 1:
    print("No device available.")
    closeDevices()
print("Using device #%1d" % dev[0])

# PicoHarp: initialize first PicoHarp device and retrieve information
print("\nInitializing the device...")
tryfunc(phlib.PH_Initialize(ct.c_int(dev[0]), ct.c_int(MODE_HIST)), "Initialize")
tryfunc(phlib.PH_GetHardwareInfo(dev[0], hwModel, hwPartno, hwVersion), "GetHardwareInfo")
print("Found Model %s Part no %s Version %s" % (hwModel.value.decode("utf-8"),
                                                hwPartno.value.decode("utf-8"),
                                                hwVersion.value.decode("utf-8")))

# PicoHarp: calibrate PicoHarp and set measurement parameters
print("\nCalibrating...")
tryfunc(phlib.PH_Calibrate(ct.c_int(dev[0])),
        "Calibrate")
tryfunc(phlib.PH_SetSyncDiv(ct.c_int(dev[0]),
                            ct.c_int(syncDivider)),
        "SetSyncDiv")
tryfunc(phlib.PH_SetInputCFD(ct.c_int(dev[0]),
                             ct.c_int(0),
                             ct.c_int(CFDLevel0),
                             ct.c_int(CFDZeroCross0)),
        "SetInputCFD")
tryfunc(phlib.PH_SetInputCFD(ct.c_int(dev[0]),
                             ct.c_int(1),
                             ct.c_int(CFDLevel1),
                             ct.c_int(CFDZeroCross1)),
        "SetInputCFD")
tryfunc(phlib.PH_SetBinning(ct.c_int(dev[0]),
                            ct.c_int(binning)),
        "SetBinning")
tryfunc(phlib.PH_SetOffset(ct.c_int(dev[0]),
                           ct.c_int(offset)),
        "SetOffset")
tryfunc(phlib.PH_GetResolution(ct.c_int(dev[0]),
                               byref(resolution)),
        "GetResolution")

# Note: after Init or SetSyncDiv you must allow 100 ms for valid count rate readings
time.sleep(0.2)

print("Resolution=%lf CFDLevel0=%dmV CFDLevel1=%dmV" % (resolution.value, CFDLevel0, CFDLevel1))

tryfunc(phlib.PH_SetStopOverflow(ct.c_int(dev[0]),
                                 ct.c_int(1),
                                 ct.c_int(65535)),
        "SetStopOverflow")


# ScontelControlUnit: define class and function
class MEASDATA(ct.Structure):
    _fields_ = [('I1', c_float),       # current value in the first channel in uA
                ('U1', c_float),       # voltage value in the first channel in mV
                ('I2', c_float),       # current value in the second channel in uA
                ('U2', c_float),       # voltage value in the second channel in mV
                ('P', c_float),        # Pressure value
                ('T', c_float),        # Temperature value
                ('R', c_float),        # Resistance value of the thermometer
                ('BATP', c_ushort),    # positive charge of the battery (to be multiplied by 10mV)
                ('BATN', c_ushort),    # negative charge of the battery (to be multiplied by 10 mV)
                ('HEATER', c_float),   # Voltage value of the Heater
                ('STATUS', c_ubyte),   # status byte (bits values are described below)
                ('BBERROR', c_ubyte)]  # byte errors (bits values are described below)


def get_CUvalues():
    measdata = MEASDATA()
    culib.bb_Value(ct.byref(measdata))
    # pass our point by ref ^^^^^
    # this lets GetCursorPos fill its x and y fields

    return measdata.I1, measdata.U1, measdata.I2, measdata.U2, measdata.P, measdata.T, measdata.R, \
        measdata.BATP, measdata.BATN, measdata.HEATER, measdata.STATUS, measdata.BBERROR


# ScontelControlUnit: initialization data exchange interface
init = culib.bb_Open()

# ScontelControlUnit: disable detector short
culib.bb_Short(0, 0)  # detector1: 0 – short-circuit mode disabled, 1 - short-circuit mode enabled
culib.bb_Short(1, 0)  # detector2: 0 – short-circuit mode disabled, 1 - short-circuit mode enabled

# ScontelControlUnit + PicoHarp: sweep current, read count rates and calculate time average
if Detector == 0:   # bias detector 0
    I0 = np.linspace(Istart, Istop, steps)
    I1 = [0]*steps  # set I1=0
else:               # bias detector 1
    I0 = [0]*steps  # set I0=0
    I1 = np.linspace(Istart, Istop, steps)

av_ctr0, av_ctr1 = [None]*steps, [None]*steps

for i in range(steps):
    start_time = time.time()
    culib.bb_Value(0, c_float(I0[i]))   # set current for detector 0
    culib.bb_Value(1, c_float(I1[i]))   # set current for detector 1
    time.sleep(0.05)
    n = 0
    accum_ctr0 = 0
    accum_ctr1 = 0
    while time.time()-start_time < average:
        tryfunc(phlib.PH_GetCountRate(ct.c_int(dev[0]),
                                      ct.c_int(0),
                                      byref(countRate0)),
                "GetCountRate")
        tryfunc(phlib.PH_GetCountRate(ct.c_int(dev[0]),
                                      ct.c_int(1),
                                      byref(countRate1)),
                "GetCountRate")
        n += 1
        accum_ctr0 = accum_ctr0+countRate0.value
        accum_ctr1 = accum_ctr1+countRate1.value
        time.sleep(0.105)
    av_ctr0[i] = accum_ctr0 / n
    av_ctr1[i] = accum_ctr1 / n
    print("I0=%5.3fuA I1=%5.3fuA av_countrate0=%d/s av_countrate1=%d/s n=%d" % (I0[i],
                                                                                I1[i],
                                                                                av_ctr0[i],
                                                                                av_ctr1[i],
                                                                                n))


# ScontelControlUnit: set current to zero
culib.bb_Value(0, c_float(0))  # set current I1 for detector 1
culib.bb_Value(1, c_float(0))  # set current I2 for detector 2

# ScontelControlUnit: enable detector short
culib.bb_Short(0, 1)  # detector1: 0 – short-circuit mode disabled, 1 - short-circuit mode enabled
culib.bb_Short(1, 1)  # detector2: 0 – short-circuit mode disabled, 1 - short-circuit mode enabled

# ScontelControlUnit: Closing the interface and stopping the data exchange
culib.bb_Close()


# Save count rate versus current data with metadata to remote file
DataOut = np.column_stack((I0, I1, av_ctr0, av_ctr1))
format = ('%5.3f', '%5.3f', '%6i', '%6i')
hdrtxt = 'Detector=%d CFDLevel0=%dmV CFDLevel1=%dmV \n' % (Detector, CFDLevel0, CFDLevel1)
hdrtxt += 'I0/uA I1/uA av_ctr_0/s av_ctr_1/s n \n'
filetime = time.strftime("%Y%m%d-%H%M")
filefolder = 'Z:/krupkegruppe/1 Geräte (Angebote,Bestellungen, Rechnungen,Reparatur,Unterlagen)/' +\
             'Scontel-Bluefors/SSPD performance/'
filename = filefolder + filetime + '_Det=%d_CFD0=%dmV_CFD1=%dmV.txt' % (Detector,
                                                                        CFDLevel0,
                                                                        CFDLevel1)
answer = input('Save data ? [y/n]')
if answer in ['y', 'Y']:
    np.savetxt(filename, DataOut, fmt=format, header=hdrtxt)
print('ok')

# z=culib.bb_GetData(ct.byref(MEASDATA()));
# z=get_CUvalues();
# culib.bb_Close()
