
import socket
import sys
import time
from ctypes import *

""" This class defines a C-like struct """
class Payload(Structure):
    _fields_ = [("id", c_uint32),
                ("counter", c_uint32),
                ("temp", c_float)]



def start_streaming(ip_address, port):

    saddr = (ip_address, port)
    
    try:
        clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except clientSock.error as err: 
        print("ERROR: Socket creation failed with error %s" %(err))

    count = 0
    while True:
        count += 1
        payload_out = Payload(1,2,count*1.1)
        print(f"Sent message: {payload_out.id}, {payload_out.counter}, {payload_out.temp}")
        
        csent = clientSock.sendto(payload_out, saddr)
        time.sleep(1)
    clientSock.close()

if __name__ == "__main__":

    ip_address = "172.16.222.31"
    port = 5000
    start_streaming(ip_address, port)