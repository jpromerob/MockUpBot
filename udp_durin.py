
import socket
import sys
import time
from ctypes import *
from durin_common import *

""" This class defines a C-like struct """
class Payload(Structure):
    _fields_ = [("id", c_uint32),
                ("counter", c_uint32),
                ("temp", c_float)]




if __name__ == "__main__":

    ip_address = "172.16.222.31"
    port = 5000
    start_udp_streaming(ip_address, port)