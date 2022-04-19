
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
                
BUFFER_SIZE = 1024

def main():
    saddr = ("172.16.222.31", 5000)
    
    try:
        serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except serverSock.error as err: 
        print("ERROR: Socket creation failed with error %s" %(err))
    
    try:
        serverSock.bind(saddr)
    except:
        print("Error binding to Durin's sensory data stream")

    while True:
        buff, caddr = serverSock.recvfrom(sizeof(Payload))
        payload_in = Payload.from_buffer_copy(buff)
        print(f"Received message: {payload_in.id}, {payload_in.counter}, {payload_in.temp}")
        
        
    
    serverSock.close()

if __name__ == "__main__":
    main()