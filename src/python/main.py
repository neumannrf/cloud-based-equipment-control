#!/usr/bin/env python -B

# Python standard libraries
import argparse
import logging
import signal
import sys
import time

# Internal modules (see src/python/modules/) and external libraries (see requirements.txt)
import wiotp.sdk.device
from modules.callback_function import myCommandCallback


def interruptHandler(signal, frame):
    client.disconnect()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interruptHandler)

    # Parse command-line options
    parser = argparse.ArgumentParser(description='Connect device to IBM Watson IoT Platform.')
    parser.add_argument('-o', '--organization', help='Organization ID.', required=True)
    parser.add_argument('-T', '--token', help='Authentication token.', required=True)
    parser.add_argument('-d', '--device', help='Device ID.', required=True)
    parser.add_argument('-t', '--type', help='Device Type.', required=True)
    arg = parser.parse_args()

    # Read device credentials
    try:
        options = {
            "identity": {"orgId": arg.organization, "typeId": arg.type, "deviceId": arg.device},
            "auth": {"token": arg.token},
        }
        client = wiotp.sdk.device.DeviceClient(options)
    except Exception as e:
        print("Caught exception connecting device: %s" % str(e))
        sys.exit()

    client.logger.setLevel(logging.DEBUG)
    client.commandCallback = myCommandCallback
    client.connect()

while True:
    time.sleep(1)
