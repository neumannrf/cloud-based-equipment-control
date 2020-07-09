# import ctypes as ct


class PicoHarp:
    """Class that stores PicoHarp measurement parameters and functions."""

    # Standard parameters (phdefin.h) and libraries
    LIB_VERSION = "3.0"
    HISTCHAN = 65536
    MAXDEVNUM = 8
    MODE_HIST = 0
    FLAG_OVERFLOW = 0x0040
    # phlib = ct.CDLL("C:\\Windows\\SysWOW64\\phlib.dll")

    # Initialize class with parameter values
    def __init__(self, tacq, offset, binning, syncDivider, CFDLevel, CFDZeroCross):
        self.tacq = tacq
        self.offset = offset
        self.binning = binning
        self.CFDLevel = CFDLevel
        self.syncDivider = syncDivider
        self.CFDZeroCross = CFDZeroCross

    # Helper function for printing logs
    def __str__(self):
        string = '\n===================================\n' + \
                 'PicoHarp measurement parameters:\n' + \
                 'Acquisition time = {0} ms\n'.format(self.tacq) + \
                 'Offset time = {0} ns\n'.format(self.offset) + \
                 'Binning = {0}\n'.format(self.binning) + \
                 'SyncDivider = {0}\n'.format(self.syncDivider) + \
                 'CFDLevel = {0} mV\n'.format(self.CFDLevel) + \
                 'CFDZeroCross = {0} mV\n'.format(self.CFDZeroCross) + \
                 '===================================\n'
        return string
