
import socket 
from ctypes import *
import numpy as np
import pdb


class Ip_Port(Structure):
    _fields_ = [("ip", c_wchar_p),
                ("b", c_uint16)]

class ToF(Structure):
    _fields_ = [("matrix", c_float * 64)]

class AllSensors(Structure):
    _fields_ = [("tof_array", ToF * 8)]

class Sensor(Structure):
    _fields_ = [("a", c_uint8),
                ("b", c_uint8),
                ("c", c_float)]

class Command(Structure):
    _fields_ = [("id", c_uint8),
                ("count", c_int16),
                ("arg_1", c_float),
                ("arg_2", c_float),
                ("arg_3", c_float)]

class Reply(Structure):
    _fields_ = [("id", c_uint8),
                ("arg_1", c_uint8)]

commandlist = ['whatever', 'something', 'anything']


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
    
    sensorslist = []

    # List of available commands
    filepath = 'sensors.txt'

    with open(filepath) as fp:
        while True:
            line = fp.readline()
            if not line:
                break
            line = line.split()

            sensorslist.append(line)

    return sensorslist


def decode(buffer):
    
    try:
        reply = "no reply :) "
        sensor_id = buffer[0]
    except:
        reply = "error ,try again "
        return reply

    # Decoding ToF Sensors
    if int(sensor_id) >= 128 and int(sensor_id) <= 131:
        tof = np.zeros((8,16))
        tof[:,0:8] = np.frombuffer(buffer, dtype='<h', offset=1, count=64).reshape((8,8))
        tof[:,8:16] = np.frombuffer(buffer, dtype='<h', offset=1+64*2, count=64).reshape((8,8))
        reply = tof

    # Decoding Miscelaneous Sensors
    if int(sensor_id) == 132:
        charge = int.from_bytes(buffer[1:2], "little")
        voltage = int.from_bytes(buffer[2:4], "little")
        # voltage = np.frombuffer(buffer, dtype='<H', offset=2, count=1)
        print(voltage)
        imu =np.frombuffer(buffer, dtype='<f', offset=4, count=9).reshape((3,3))
        reply = (charge, voltage, imu)
        reply = 1

    # Decoding UWB Sensors
    if int(sensor_id) == 133:
        nb_beacons = int.from_bytes(buffer[1:2], "little")
        uwb = np.frombuffer(buffer, dtype='<f', offset=2, count=nb_beacons)
        reply = uwb
        
    return reply