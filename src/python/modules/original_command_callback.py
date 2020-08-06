# Access to Scontel Control Unit via PicoHarp 300 Hardware via PHLIB.DLL v 3.0.
# Ralph Krupke, KIT, May 2020

import os
import json
import time
import ctypes as ct
import numpy as np
from ctypes import byref, c_float

# PicoHarp: from phdefin.h
LIB_VERSION = "3.0"
HISTCHAN = 65536
MAXDEVNUM = 8
MODE_HIST = 0
FLAG_OVERFLOW = 0x0040
phlib = ct.CDLL("C:\\Windows\\SysWOW64\\phlib.dll")
culib = ct.WinDLL("C:\\ControlUnit Toolset\\biasbox.dll")


def closeDevices():
    for i in range(MAXDEVNUM):
        phlib.PH_CloseDevice(ct.c_int(i))
    exit(0)


def tryfunc(funcName, retcode):
    if retcode < 0:
        errorString = ct.create_string_buffer(b"", 40)
        phlib.PH_GetErrorString(errorString, ct.c_int(retcode))
        print("PH_%s error %d (%s)!" % (funcName, retcode, errorString.value.decode("utf-8")))
        closeDevices()


def originalCommandCallback(cmd):
    # PicoHarp: define measurement parameters
    binning = cmd.data['binning']               # you can change this
    offset = cmd.data['offset']
    syncDivider = cmd.data['syncDivider']       # you can change this
    CFDZeroCross0 = cmd.data['CFDZeroCross0']   # you can change this (in mV)
    CFDLevel0 = cmd.data['CFDLevel0']           # you can change this (in mV)
    CFDZeroCross1 = cmd.data['CFDZeroCross1']   # you can change this (in mV)
    CFDLevel1 = cmd.data['CFDLevel1']           # you can change this (in mV)

    # ScontelControlUnit: define measurement parameters
    detector = cmd.data['detector']     # select detector 0 or 1
    Istart = cmd.data['Istart']         # in uA
    Istop = cmd.data['Istop']           # in uA
    Istep = cmd.data['Istep']           # in uA
    average = cmd.data['average']       # time average in s
    steps = int((Istop-Istart)/Istep)+1

    # PicoHarp: variables to store information read from PicoHarp DLL
    dev = []
    libVersion = ct.create_string_buffer(b"", 8)
    hwSerial = ct.create_string_buffer(b"", 8)
    hwPartno = ct.create_string_buffer(b"", 8)
    hwVersion = ct.create_string_buffer(b"", 8)
    hwModel = ct.create_string_buffer(b"", 16)
    errorString = ct.create_string_buffer(b"", 40)
    resolution = ct.c_double()
    countRate0 = ct.c_int()
    countRate1 = ct.c_int()

    # PicoHarp: get library version
    phlib.PH_GetLibraryVersion(libVersion)
    print("Library version is %s" % libVersion.value.decode("utf-8"))
    if libVersion.value.decode("utf-8") != LIB_VERSION:
        print("Warning: The application was built for version %s" % LIB_VERSION)

    # PicoHarp: search for PicoHarp devices and use first one
    print("\nSearching for PicoHarp devices...")
    print("Devidx     Status")
    for i in range(MAXDEVNUM):
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
    tryfunc("Initialize", phlib.PH_Initialize(ct.c_int(dev[0]), ct.c_int(MODE_HIST)))
    tryfunc("GetHardwareInfo", phlib.PH_GetHardwareInfo(dev[0], hwModel, hwPartno, hwVersion))
    print("Found Model %s Part no %s Version %s" % (hwModel.value.decode("utf-8"),
                                                    hwPartno.value.decode("utf-8"),
                                                    hwVersion.value.decode("utf-8")))

    # PicoHarp: calibrate PicoHarp and set measurement parameters
    print("\nCalibrating...")
    tryfunc("Calibrate", phlib.PH_Calibrate(ct.c_int(dev[0])))
    tryfunc("SetSyncDiv", phlib.PH_SetSyncDiv(ct.c_int(dev[0]),
                                              ct.c_int(syncDivider)))
    tryfunc("SetInputCFD", phlib.PH_SetInputCFD(ct.c_int(dev[0]),
                                                ct.c_int(0),
                                                ct.c_int(CFDLevel0),
                                                ct.c_int(CFDZeroCross0)))
    tryfunc("SetInputCFD", phlib.PH_SetInputCFD(ct.c_int(dev[0]),
                                                ct.c_int(1),
                                                ct.c_int(CFDLevel1),
                                                ct.c_int(CFDZeroCross1)))
    tryfunc("SetBinning", phlib.PH_SetBinning(ct.c_int(dev[0]),
                                              ct.c_int(binning)))
    tryfunc("SetOffset", phlib.PH_SetOffset(ct.c_int(dev[0]),
                                            ct.c_int(offset)))
    tryfunc("GetResolution", phlib.PH_GetResolution(ct.c_int(dev[0]),
                                                    byref(resolution)))

    print("Resolution=%lf CFDLevel0=%dmV CFDLevel1=%dmV" % (resolution.value, CFDLevel0, CFDLevel1))

    # Note: after Init or SetSyncDiv you must allow 100 ms for valid count rate readings
    time.sleep(0.2)

    tryfunc("SetStopOverflow", phlib.PH_SetStopOverflow(ct.c_int(dev[0]),
                                                        ct.c_int(1),
                                                        ct.c_int(65535)))

    # ScontelControlUnit: initialization data exchange interface
    culib.bb_Open()

    # ScontelControlUnit: disable detector short
    culib.bb_Short(0, 0)  # detector1: 0 (short-circuit disabled), 1 (short-circuit enabled)
    culib.bb_Short(1, 0)  # detector2: 0 (short-circuit disabled), 1 (short-circuit enabled)

    # ScontelControlUnit + PicoHarp: sweep current, read count rates and calculate time average
    if detector == 0:   # bias detector 0
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
            tryfunc("GetCountRate", phlib.PH_GetCountRate(ct.c_int(dev[0]),
                                                          ct.c_int(0),
                                                          byref(countRate0)))
            tryfunc("GetCountRate", phlib.PH_GetCountRate(ct.c_int(dev[0]),
                                                          ct.c_int(1),
                                                          byref(countRate1)))
            n += 1
            accum_ctr0 = accum_ctr0 + countRate0.value
            accum_ctr1 = accum_ctr1 + countRate1.value
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
    culib.bb_Short(0, 1)  # detector1: 0 (short-circuit disabled), 1 (short-circuit enabled)
    culib.bb_Short(1, 1)  # detector2: 0 (short-circuit disabled), 1 (short-circuit enabled)

    # ScontelControlUnit: Closing the interface and stopping the data exchange
    culib.bb_Close()

    # Save count rate versus current data with metadata to remote file
    output = np.column_stack((I0, I1, av_ctr0, av_ctr1))
    fmt = ('%5.3f', '%5.3f', '%6i', '%6i')
    hdrtxt = 'Detector=%d CFDLevel0=%dmV CFDLevel1=%dmV \n' % (detector, CFDLevel0, CFDLevel1)
    hdrtxt += 'I0/uA I1/uA av_ctr_0/s av_ctr_1/s n \n'
    filetime = time.strftime("%Y%m%d-%H%M")
    filefolder = os.getcwd() + '/logs/'
    filename = filefolder + filetime + '_Det=%d_CFD0=%dmV_CFD1=%dmV.txt' % (detector,
                                                                            CFDLevel0,
                                                                            CFDLevel1)
    np.savetxt(filename, output, fmt=fmt, header=hdrtxt)

    # Build response JSON object
    response_json = [{
        'series': ['Detector {0}'.format(detector)],
        'data': [
            [{'x': 1000 * output[i, detector], 'y': output[i, 2 + detector]} for i in range(steps)]
        ],
        'labels': ['']
    }]

    with open(os.getcwd() + '/../logs/response.json', 'w', encoding='utf-8') as f:
        json.dump(response_json, f, ensure_ascii=False, sort_keys=True)
