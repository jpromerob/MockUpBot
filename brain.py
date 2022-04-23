#!/usr/bin/env python3


import socket
import sys
import numpy as np
import time
import random
import multiprocessing 
from ctypes import *
from durin_common import *


def connect_and_bind():

    tcp_ssock = udp_ssock = []
    ready = False

    try:
        tcp_ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # ✓
        tcp_ssock.connect((DURIN_IP, PORT_TCP)) # ✓
        print(f"TCP connection to {DURIN_IP}")

        udp_ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ✓
        udp_ssock.bind((DURIN_IP, PORT_UDP)) # ✓
        print(f"UDP bind to {DURIN_IP}")

        ready = True

    except:
        print("Problem connecting/binding sockets")
        
    return tcp_ssock, udp_ssock, ready



def read_command_file():
    filepath = 'commands.txt'
    with open(filepath) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            print("cmd_id: {} --> command: {}".format(cnt, line.strip()))
            line = fp.readline()
            cnt += 1

def parse_command(command):
    
    arg_array = np.zeros(4)

    command = command.split()
    arg_nb = len(command)-1

    filepath = 'commands.txt'
    count = 0
    cmd_id = -1


    if command[0] == "list":
        read_command_file()
        cmd_id = 0
    else:
        with open(filepath) as fp:
            line = True
            while line:
                line = fp.readline()
                words = line.split()
                if command[0] in words:
                    if len(words) == len(command):
                        cmd_id = count+1
                        break
                    else:
                        print("Check command: " + line)
                count +=1




    for i in range(arg_nb):
        arg_array[i] = command[i+1]

    return cmd_id, arg_array


'''
'''
def send_request(tcp_ssock):
    
    while True:

        reply_expected = False
        try:
            # Get command (through command line)
            command = input()
        except KeyboardInterrupt:
            print("\rKeyboard interrupt (user)")
            break


        if len(command)>0:
            cmd_id, arg_array = parse_command(command)
            payload_out = Command(cmd_id, arg_array[0], arg_array[3], arg_array[2])

            if cmd_id > 0:    
                print(f"Sending command: {cmd_id} with args: {arg_array}")
                nsent = tcp_ssock.send(payload_out)
                reply_expected = True
            elif cmd_id<0:
                print(f"Check command and arguments")

        if reply_expected:
            buff = tcp_ssock.recv(sizeof(Reply))
            payload_in = Reply.from_buffer_copy(buff)
            print(f"Reply: {payload_in.id}")




def udp_reception(udp_ssock):
    
    while True:

        try:
            buff, caddr = udp_ssock.recvfrom(sizeof(Sensor))
            payload_in = Sensor.from_buffer_copy(buff)
            # print(f"Received message: {payload_in.a}, {payload_in.b}, {payload_in.c}")
        except:
            print("Problem receiving sensory data")
            break




if __name__ == "__main__":
    
    # read_command_file()
    # time.sleep(20)

    global connection_on


    tcp_ssock, udp_ssock, ready = connect_and_bind()
    
    if ready:

        manager = multiprocessing.Manager()
        connection_on = manager.Value('i', 0)

        p_sensors = multiprocessing.Process(target=udp_reception, args=(udp_ssock,))
        # p_commands = multiprocessing.Process(target=send_request, args=(tcp_ssock,))

        p_sensors.start()
        # p_commands.start()

        send_request(tcp_ssock)


        # p_commands.join()
        p_sensors.join()

        print("Closing sockets")
        tcp_ssock.close()
        udp_ssock.close()
