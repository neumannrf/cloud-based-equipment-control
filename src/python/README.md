# Connect device to IBM Watson IoT Platform

## Installation

The main dependency of the `main.py` script is the [`wiotp-sdk`](https://github.com/ibm-watson-iot/iot-python) library.
All dependencies are listed in the `requirements.txt` file.

```Shell
> pip install -r src/python/requirements.txt
```

## Usage

The `main.py` file is responsible for parsing the connection credentials that are passed as command-line options.

* **Organization ID:** ID of the IBM Watson IoT Platform (WIoTP) organization that hosts the MQTT broker.
* **Authentication token:** Authentication token provided when registering the device on WIoTP.
* **Device Type:** Device type provided when the device was registered on WIoTP.
* **Device ID:** Device ID provided when the device was registered on WIoTP.

```Shell
> python src/python/main.py -o ORG_ID -d DEV_ID -t DEV_TYPE -T AUTH_TOKEN
```

## Customization

The `src/python/modules/command_callback.py` contains the `myCommandCallback()` function that can be customized. This function is called from `main.py` every time an MQTT command is issued.
