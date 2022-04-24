#!/usr/bin/env python3

import socket
import struct
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



def get_tof(sensorid):
    tof_a = np.random.randint(0,64,(8,8))
    tof_b = np.random.randint(0,64,(8,8))
    print("\n\ntof_a:")
    print(tof_a)
    print("\n\ntof_b:")
    print(tof_b)
    reply = bytearray([0]*(1+2*2*64)) # 1 bytes for sensorid + (2 bytes per int16, 2 tof sensors, 64 values per sensor)
    reply[0:1] = sensorid.to_bytes(1, 'little')
    idx = 1
    for i in range(tof_a.shape[0]):
        for j in range(tof_a.shape[1]):
            reply[idx:idx+2] = bytearray(struct.pack("<h", tof_a[i][j]))
            idx += 2

    for i in range(tof_b.shape[0]):
        for j in range(tof_b.shape[1]):
            reply[idx:idx+2] = bytearray(struct.pack("<h", tof_b[i][j]))
            idx += 2

    return reply

def get_misc(sensorid):
    charge = random.randint(0,100)
    voltage = random.randint(0,2**16-1)
    imu = np.random.random((3,3))*2**12
    print(f"charge data:\n{charge}")
    print(f"voltage data:\n{voltage}")
    print(f"IMU data:\n{imu}")
    reply = bytearray([0]*(1+1+2+9*4)) # 1 bytes for sensorid + 1 byte for charge% + 2 bytes for battery voltage + 4 bytes per IMU reading for 9 readings
    reply[0:1] = sensorid.to_bytes(1, 'little')
    reply[1:2] = charge.to_bytes(1, 'little')
    reply[2:4] = bytearray(struct.pack("<H", voltage)) # unsigned short (uint_16) little endian
    idx = 4
    for i in range(imu.shape[0]):
        for j in range(imu.shape[1]):
            reply[idx:idx+4] = bytearray(struct.pack("<f", imu[i][j]))
            idx += 4
    return reply

def get_uwb(sensorid):
    nb_beacons = random.randint(1, 8)
    uwb = np.random.random((nb_beacons))*10
    print(f"UWB data:\n{uwb}")
    reply = bytearray([0]*(1+1+4*nb_beacons)) # 1 bytes for sensorid + 1 byte for # of beacons + 4 bytes beacon
    reply[0:1] = sensorid.to_bytes(1, 'little')
    reply[1:2] = nb_beacons.to_bytes(1, 'little')
    idx = 2
    for i in range(uwb.shape[0]):
        reply[idx:idx+4] = bytearray(struct.pack("<f", uwb[i]))
        idx += 4
    return reply

def prepare_reply(cmd_id, issensor=False, sensorid=0):
    if issensor:
        if sensorid >=128 and sensorid <= 131:
            # ToF sensors 
            print("Tof Sensors")
            reply = get_tof(sensorid)
            return reply
        if sensorid == 132:
            # Battery + IMU
            print("Bat + IMU")
            reply = get_misc(sensorid)
            return reply
        if sensorid == 133:
            # UWB sensors
            print("UWB Sensors")
            reply = get_uwb(sensorid)
            return reply

    reply = bytearray([0]*1)
    return reply
        

def buff_decode(buff):
    global stream_on, udp_stream

    cmd_id = buff[0]
    byte_count = buff[1]

    reply = []

    if cmd_id == 1:
        print("Power Off")
        reply.append(prepare_reply(cmd_id))

    if cmd_id == 2:
        print("Move RobCentric")
        vel_x = int.from_bytes(buff[2:4], "little", signed=True)
        vel_y = int.from_bytes(buff[4:6], "little", signed=True)
        rot = int.from_bytes(buff[6:8], "little", signed=True)
        print(f"x: {vel_x}, y:{vel_y}, r:{rot}")
        reply.append(prepare_reply(cmd_id))

    if cmd_id == 3:
        print("Move Wheels")
        m1 = int.from_bytes(buff[2:4], "little", signed=True)
        m2 = int.from_bytes(buff[4:6], "little", signed=True)
        m3 = int.from_bytes(buff[6:8], "little", signed=True)
        m4 = int.from_bytes(buff[8:10], "little", signed=True)
        print(f"m1: {m1}, m2:{m2}, m3:{m3}, m4:{m4}")
        reply.append(prepare_reply(cmd_id))

    if cmd_id == 16:
        print("Poll All")
        reply = []
        for sensor_id in range(128,133+1,1):
            reply.append(prepare_reply(cmd_id, True, sensor_id))
            print(f"len(reply) : {len(reply)}")

    if cmd_id == 17:
        print(f"Poll Sensor X")
        sensor_id = int.from_bytes(buff[2:3], "little", signed=False)
        reply.append(prepare_reply(cmd_id, True, sensor_id))

    if cmd_id == 18:
        print("Start Streaming")
        a = int.from_bytes(buff[2:3], "little", signed=False)
        b = int.from_bytes(buff[3:4], "little", signed=False)
        c = int.from_bytes(buff[4:5], "little", signed=False)
        d = int.from_bytes(buff[5:6], "little", signed=False)
        host = str(a)+'.'+str(b)+'.'+str(c)+'.'+str(d)
        port = int.from_bytes(buff[6:8], "little", signed=True)
        period = int.from_bytes(buff[8:10], "little", signed=True)
        print(f"Set to {host} : {port} every {period}[ms]")

        udp_stream.host = host
        udp_stream.port_udp = port
        udp_stream.period = period

        stream_on.value = 1
        reply.append(prepare_reply(cmd_id))

    if cmd_id == 19:
        print("Stop Streaming")
        stream_on.value = 0
        reply.append(prepare_reply(cmd_id))

    

    return reply



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
                buff = csock.recv(1024)
                reply = buff_decode(buff)
                print("Sending reply back.\n")  
                for r in reply:
                    print(r)
                    nsent = csock.send(r)
            except:
                print("Connection Lost")
                break

        print("Closing socket")
        print("----------------------------")
        time.sleep(1)
        csock.close()
        connection_on.value = 0    
    ssock.close()


def move():
    global connection_on
    print("Moving somehow")
    while True:

        if connection_on.value == 1:
            print("Moving ... ")

        time.sleep(5)



def feel(udp_ssock):
    global stream_on, udp_stream
    print("Feeling something")

    count = 0
    while True:

        if stream_on.value == 1:
            count += 1
            for sensor_id in range(128,133+1,1):
                print(sensor_id)
                payload_out = prepare_reply(0, True, sensor_id)
                print(payload_out)
                csent = udp_ssock.sendto(payload_out, (udp_stream.host, udp_stream.port_udp))                
            time.sleep(udp_stream.period/1000)

def old_feel(udp_ssock):
    global stream_on, udp_stream
    print("Feeling something")

    count = 0
    while True:

        if stream_on.value == 1:
            count += 1
            payload_out = Sensor(1,2,count*1.1)
            print(f"Sending to {udp_stream.host}:{udp_stream.port_udp}")
            print(f"Sensor data sent: {payload_out.a}, {payload_out.b}, {payload_out.c}")            
            csent = udp_ssock.sendto(payload_out, (udp_stream.host, udp_stream.port_udp))                
            time.sleep(udp_stream.period/1000)



if __name__ == "__main__":
    
    global connection_on, stream_on, udp_stream

    tcp_ssock, udp_ssock, ready = open_sockets()

    if ready:

        manager = multiprocessing.Manager()
        connection_on = manager.Value('i', 0)
        stream_on = manager.Value('i', 0)
        udp_stream = manager.Namespace()
        udp_stream.host = BRAIN_IP
        udp_stream.port_udp = PORT_UDP
        udp_stream.period = 1000 # 1[s] = 1000 [ms]


        p_sensors = multiprocessing.Process(target=feel, args=(udp_ssock, ))

        # p_actuators.start()
        p_sensors.start()

        process_request(tcp_ssock)


    
        try:
            print("Closing sockets")
            tcp_ssock.close()
            udp_ssock.close()
            
        except:
            pass
            
            