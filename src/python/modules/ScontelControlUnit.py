# import ctypes as ct


class ScontelControlUnit:
    """Class that stores ScontelControlUnit measurement parameters and functions."""

    # Standard library
    # culib = ct.WinDLL("C:\\ControlUnit Toolset\\biasbox.dll")

    @classmethod
    def initializeDevice(cls):
        pass

    @classmethod
    def disableDetectorShort(cls):
        pass

    @classmethod
    def setCurrentToZero(cls):
        pass

    @classmethod
    def enableDetectorShort(cls):
        pass

    @classmethod
    def closeDevice(cls):
        pass

    # Initialize class with parameter values
    def __init__(self, detector, Istart, Istop, Istep, average):
        self.Istep = Istep
        self.Istop = Istop
        self.Istart = Istart
        self.average = average
        self.detector = detector
        self.steps = int((Istop - Istart) / Istep) + 1

    # Helper function for printing logs
    def __str__(self):
        string = '\n==========================================\n' + \
                 'ScontelControlUnit measurement parameters:\n' + \
                 'Detector = {0}\n'.format(self.detector) + \
                 'Initial current = {0} uA\n'.format(self.Istart) + \
                 'Final current = {0} uA\n'.format(self.Istop) + \
                 'Current step = {0} uA\n'.format(self.Istep) + \
                 'Time average = {0} s\n'.format(self.average) + \
                 'Number of steps = {0}\n'.format(self.steps) + \
                 '==========================================\n'
        return string

    def performMeasurement(self):
        pass
