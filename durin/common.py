
from ctypes import *
import numpy as np


BRAIN_IP = '127.0.0.1'
DURIN_IP = '127.0.0.1'
PORT_TCP = 2300
PORT_UDP = 5000


def available_cmds():
    
    cmdlist = []

    # List of available commands
    filepath = 'commands.txt'

    with open(filepath) as fp:
        while True:
            line = fp.readline()
            if not line:
                break
            line = line.split()

            cmdlist.append(line)

    return cmdlist


def available_sensors():
    
    sensorsdict = {}

    # List of available commands
    filepath = 'sensors.txt'

    with open(filepath) as fp:
        while True:
            line = fp.readline()
            if not line:
                break
            line = line.split()
            sensorsdict.update({line[1]: int(line[0])})

    return sensorsdict

SENSORS = available_sensors()

#@TODO: replace hardcoded sensor_id ... use dict or something alike
def decode(buffer):

    reply = "No reply expected"
    sensor_id = buffer[0]

    # Decoding ToF Sensors
    if int(sensor_id) >= SENSORS["tof_a"] and int(sensor_id) <= SENSORS["tof_d"]:
        tof = np.zeros((8,16))
        tof[:,0:8] = np.frombuffer(buffer, dtype='<h', offset=1, count=64).reshape((8,8))
        tof[:,8:16] = np.frombuffer(buffer, dtype='<h', offset=1+64*2, count=64).reshape((8,8))
        reply = tof

    # Decoding Miscelaneous Sensors
    if int(sensor_id) == SENSORS["misc"]:
        charge = int.from_bytes(buffer[1:2], "little")
        voltage = int.from_bytes(buffer[2:4], "little")
        imu =np.frombuffer(buffer, dtype='<f', offset=4, count=9).reshape((3,3))
        reply = (charge, voltage, imu)

    # Decoding UWB Sensors
    if int(sensor_id) == SENSORS["uwb"]:
        nb_beacons = int.from_bytes(buffer[1:2], "little")
        uwb = np.frombuffer(buffer, dtype='<f', offset=2, count=nb_beacons)
        reply = uwb
        
    return sensor_id, reply