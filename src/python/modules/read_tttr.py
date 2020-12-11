import struct


def gotOverflow(outputfile, recNum):
    outputfile.write(f'{recNum:07d}\tOFL\t*\n')


def gotMarker(outputfile, recNum, timeTag, markers):
    outputfile.write(f'{recNum:07d}\tMAR\t{markers:x}\t\t{timeTag:015d}\n')


def gotPhotonT2(outputfile, recNum, timeTag, channel, globRes=4.0e-12):
    trueTime = int(timeTag * globRes * 1.0e12)
    outputfile.write(f'{recNum:07d}\tCHN\t{channel:x}\t\t{timeTag:015d}\t{trueTime:015d}\n')


def gotPhotonT3(outputfile, recNum, timeTag, channel, dtime, globRes=4.0e-12):
    outputfile.write("%u CHN %1x %u %8.0lf %10u\n" % (recNum,
                                                      channel,
                                                      timeTag,
                                                      (timeTag * globRes * 1e9),
                                                      dtime))


def read_T2(inputfile, outputfile, oflcorrection=0):
    print("PicoHarp T2 data")
    outputfile.write("\n-----------------------\n")
    outputfile.write("PicoHarp T2 data\n")
    outputfile.write("\nrecord#\tchannel\tnsync\t\t\t\t\t\ttruetime/ps\n")

    T2WRAPAROUND = 210698240
    recNum = 0
    while (True):
        try:
            recordData = "{0:0{1}b}".format(struct.unpack("<I", inputfile.read(4))[0], 32)
        except Exception:
            print('Finished reading %s file containing %d records.' % (inputfile.name, recNum))
            exit(0)
        recNum += 1

        channel = int(recordData[0:4], base=2)
        dtime = int(recordData[4:32], base=2)
        if channel == 0xF:  # Special record
            # lower 4 bits of time are marker bits
            markers = int(recordData[28:32], base=2)
            if markers == 0:  # Not a marker, so overflow
                gotOverflow(outputfile, recNum)
                oflcorrection += T2WRAPAROUND
            else:
                # Actually, the lower 4 bits for the time aren't valid because
                # they belong to the marker. But the error caused by them is
                # so small that we can just ignore it.
                truetime = oflcorrection + dtime
                gotMarker(outputfile, recNum, truetime, markers)
        else:
            if channel > 4:  # Should not occur
                print("Illegal Channel:  #%1d %1u" % (recNum, channel))
                outputfile.write("\nIllegal channel ")
            truetime = oflcorrection + dtime
            gotPhotonT2(outputfile, recNum, truetime, channel)


def read_T3(inputfile, outputfile, oflcorrection=0, dlen=0):
    print("PicoHarp T3 data")
    outputfile.write("\n-----------------------\n")
    outputfile.write("PicoHarp T3 data\n")
    outputfile.write("\nrecord#\tchannel\tnsync\t\t\t\t\t\ttruetime/ns\tdtime\n")

    T3WRAPAROUND = 65536
    recNum = 0
    while (True):
        # The data is stored in 32 bits that need to be divided into smaller
        # groups of bits, with each group of bits representing a different
        # variable. In this case, channel, dtime and nsync. This can easily be
        # achieved by converting the 32 bits to a string, dividing the groups
        # with simple array slicing, and then converting back into the integers.
        try:
            recordData = "{0:0{1}b}".format(struct.unpack("<I", inputfile.read(4))[0], 32)
        except Exception:
            print('Finished reading %s file containing %d records.' % (inputfile.name, recNum))
            exit(0)
        recNum += 1

        dtime = int(recordData[4:16], base=2)
        channel = int(recordData[0:4], base=2)
        nsync = int(recordData[16:32], base=2)
        if channel == 0xF:  # Special record
            if dtime == 0:  # Not a marker, so overflow
                gotOverflow(outputfile, recNum)
                oflcorrection += T3WRAPAROUND
            else:
                truensync = oflcorrection + nsync
                gotMarker(outputfile, recNum, truensync, dtime)
        else:
            if channel == 0 or channel > 4:  # Should not occur
                print("Illegal Channel:  #%1d %1u" % (dlen, channel))
                outputfile.write("\nIllegal channel ")
            truensync = oflcorrection + nsync
            gotPhotonT3(outputfile, recNum, truensync, channel, dtime)
            dlen += 1
