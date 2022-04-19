
import socket 
from ctypes import *



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
                ("arg_1", c_float),
                ("arg_2", c_float),
                ("arg_3", c_float)]

class Reply(Structure):
    _fields_ = [("id", c_uint8),
                ("arg_1", c_uint8)]

commandlist = ['whatever', 'something', 'anything']


BRAIN_IP = '172.16.222.31'
DURIN_IP = '172.16.222.31'
PORT_TCP = 2300
PORT_UDP = 5000



