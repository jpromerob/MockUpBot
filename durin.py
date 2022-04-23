#!/usr/bin/env python3

import socket
import sys
import signal
import random
import time
from ctypes import *
from durin_common import *
import multiprocessing 


BUFFER_SIZE = 1024

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')




def open_sockets():
    
    tcp_ssock = udp_ssock = []
    ready = False
    

    try:
        tcp_ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("TCP Socket created")

        # bind the server socket and listen
        tcp_ssock.bind((DURIN_IP, PORT_TCP))
        print("Bind done")
        tcp_ssock.listen(3)
        print("Server listening on port {:d}".format(PORT_TCP))


        udp_ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("UDP Socket created")
        ready = True

    except:
        print("Problem opening sockets")
    
    return tcp_ssock, udp_ssock, ready

'''
process requests
'''
def process_request(ssock):
    global connection_on, stream_on

    while True:
        csock, client_address = ssock.accept()
        print("Accepted connection from {:s}".format(client_address[0]))
        connection_on.value = 1

        while True:

            try:
                buff = csock.recv(sizeof(Command))
                payload_in = Command.from_buffer_copy(buff)
                print(f"Received command id:{payload_in.id}")
                if payload_in.id == 18:
                    print("Start Streaming")
                    stream_on.value = 1
                if payload_in.id == 19:
                    print("Stop Streaming")
                    stream_on.value = 0



                print("Sending reply back.\n")
                payload_out = Reply(0,1)
                nsent = csock.send(payload_out)
            except:
                print("Connection Lost")
                break

        print("Closing socket")
        print("----------------------------")
        time.sleep(1)
        csock.close()
        connection_on.value = 0


def move():
    global connection_on
    print("Moving somehow")
    while True:

        if connection_on.value == 1:
            print("Moving ... ")

        time.sleep(5)



def feel(udp_ssock):
    global stream_on
    print("Feeling something")

    count = 0
    while True:

        if stream_on.value == 1:
            count += 1
            payload_out = Sensor(1,2,count*1.1)
            print(f"Sensor data sent: {payload_out.a}, {payload_out.b}, {payload_out.c}")            
            csent = udp_ssock.sendto(payload_out, (BRAIN_IP, PORT_UDP))                
            time.sleep(1)



if __name__ == "__main__":
    
    global connection_on, stream_on

    tcp_ssock, udp_ssock, ready = open_sockets()

    if ready:

        manager = multiprocessing.Manager()
        connection_on = manager.Value('i', 0)
        stream_on = manager.Value('i', 0)

        actuator_q = multiprocessing.Queue() # events
        sensor_q = multiprocessing.Queue() # commands


        p_actuators = multiprocessing.Process(target=move, args=())
        p_sensors = multiprocessing.Process(target=feel, args=(udp_ssock, ))
        p_brain = multiprocessing.Process(target=process_request, args=(tcp_ssock,))

        # p_actuators.start()
        p_sensors.start()
        p_brain.start()

        
        signal.signal(signal.SIGINT, signal_handler)
        print('Press Ctrl+C')
        signal.pause()
            
        # p_actuators.join()
        p_sensors.join()
        p_brain.join()

    
        try:
            print("Closing sockets")
            tcp_ssock.close()
            udp_ssock.close()
            
        except:
            pass
            
            