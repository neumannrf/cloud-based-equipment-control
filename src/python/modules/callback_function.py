def myCommandCallback(cmd):
    print("Command received!")
    print("\tData: %s" % cmd.data)
    print("\tTimestamp: %s" % cmd.timestamp)
    print("\tCommandID: %s" % cmd.commandId)
    print("\tFormat: %s" % cmd.format)

    # PicoHarp: define measurement parameters
    binning = cmd.data['binning']               # you can change this
    offset = cmd.data['offset']
    tacq = cmd.data['tacq']                     # Measurement time in millisec, you can change this
    syncDivider = cmd.data['syncDivider']       # you can change this
    CFDZeroCross0 = cmd.data['CFDZeroCross0']   # you can change this (in mV)
    CFDZeroCross1 = cmd.data['CFDZeroCross1']   # you can change this (in mV)
    CFDLevel0 = cmd.data['CFDLevel0']           # you can change this (in mV)
    CFDLevel1 = cmd.data['CFDLevel1']           # you can change this (in mV)

    # ScontelControlUnit: define measurement parameters
    detector = cmd.data['detector']     # select detector 0 or 1
    Istart = cmd.data['Istart']         # in uA
    Istop = cmd.data['Istop']           # in uA
    Istep = cmd.data['Istep']           # in uA
    average = cmd.data['average']       # time average in s
    steps = int((Istop - Istart) / Istep) + 1

    # Print measurement parameters
    print('\n===================================')
    print('Measurement parameters')
    print('binning', binning)
    print('offset', offset)
    print('tacq', tacq)
    print('syncDivider', syncDivider)
    print('CFDZeroCross0', CFDZeroCross0)
    print('CFDZeroCross1', CFDZeroCross1)
    print('CFDLevel0', CFDLevel0)
    print('CFDLevel1', CFDLevel1)
    print('detector', detector)
    print('Istart', Istart)
    print('Istop', Istop)
    print('Istep', Istep)
    print('average', average)
    print('steps', steps)
    print('===================================\n')
