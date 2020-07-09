from PicoHarp import PicoHarp
from ScontelControlUnit import ScontelControlUnit


def myCommandCallback(cmd):
    print("Command received!")
    print("\tData: %s" % cmd.data)
    print("\tTimestamp: %s" % cmd.timestamp)
    print("\tCommandID: %s" % cmd.commandId)
    print("\tFormat: %s" % cmd.format)

    # PicoHarp: load measurement parameters
    ph = PicoHarp(cmd.data['tacq'],                                         # in ms
                  cmd.data['offset'],                                       # in ns
                  cmd.data['binning'],                                      #
                  cmd.data['syncDivider'],                                  #
                  [cmd.data['CFDLevel0'], cmd.data['CFDLevel1']],           # in mV
                  [cmd.data['CFDZeroCross0'], cmd.data['CFDZeroCross1']])   # in mV
    print(ph)

    # ScontelControlUnit: load measurement parameters
    scu = ScontelControlUnit(cmd.data['detector'],  # select detector 0 or 1
                             cmd.data['Istart'],    # in uA
                             cmd.data['Istop'],     # in uA
                             cmd.data['Istep'],     # in uA
                             cmd.data['average'])   # time average in s
    print(scu)
