from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ByteString, Callable, Generic, TypeVar
from network import TCPLink, UDPLink
import struct


T = TypeVar("T")


@dataclass
class Command:
    pass

    @abstractmethod
    def encode() -> ByteString:
        pass

class MoveRobcentric(Command):

    def __init__(self, vel_x, vel_y, rot):
        self.cmd_id = 2
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.rot = rot

    def encode(self):
        data = bytearray([0] * 8)
        data[0] = self.cmd_id
        data[1] = 6 # id + byte_count + 3*2
        data[2:4] = bytearray(struct.pack("<h", self.vel_x)) #short (int16) little endian
        data[4:6] = bytearray(struct.pack("<h", self.vel_y)) #short (int16) little endian
        data[6:8] = bytearray(struct.pack("<h", self.rot)) #short (int16) little endian
        
        return data


class MoveWheels(Command):

    def __init__(self, m1, m2, m3, m4):
        self.cmd_id = 3
        self.m1 = m1
        self.m2 = m2
        self.m3 = m3
        self.m4 = m4

    def encode(self):
        data = bytearray([0] * 10)
        data[0] = self.cmd_id
        data[1] = 8 # id + byte_count + 4*2
        data[2:4] = bytearray(struct.pack("<h", self.m1)) #short (int16) little endian
        data[4:6] = bytearray(struct.pack("<h", self.m2)) #short (int16) little endian
        data[6:8] = bytearray(struct.pack("<h", self.m3)) #short (int16) little endian
        data[8:10] = bytearray(struct.pack("<h", self.m4)) #short (int16) little endian
        
        return data


class PollAll(Command):

    def __init__(self):
        self.cmd_id = 16

    def encode(self):
        data = bytearray([0] * 2)
        data[0] = self.cmd_id
        data[1] = 1 # id + byte_count
        
        return data

class PollSensor(Command):

    def __init__(self, sensor_id):
        self.cmd_id = 17
        self.sensor_id = sensor_id # @TODO: 

    def encode(self):
        data = bytearray([0] * 3)
        data[0] = self.cmd_id
        data[1] = 3 # id + byte_count + 4*2
        data[2:3] = bytearray(struct.pack("<b", self.sensor_id)) # integer (uint8) little endian
        
        return data

class StreamOn(Command):

    def __init__(self):
        self.cmd_id = 18

    def encode(self):
        data = bytearray([0] * 2)
        data[0] = self.cmd_id
        data[1] = 1 # id + byte_count
        
        return data

class StreamOff(Command):

    def __init__(self):
        self.cmd_id = 19

    def encode(self):
        data = bytearray([0] * 2)
        data[0] = self.cmd_id
        data[1] = 1 # id + byte_count
        
        return data

class DurinActuator():
    def __init__(self, tcp_link: TCPLink, udp_link: UDPLink):
        self.tcp_link = tcp_link
        self.udp_link = udp_link

    def __call__(self, action: Command):
        command_bytes = action.encode()
        if command_bytes[0] == 18:
            print("This means stream on")
            self.udp_link.start_com()
        if command_bytes[0] == 19:
            print("This means stream off")
            self.udp_link.stop_com()
        self.tcp_link.send(command_bytes)

    def write(self, action):
        self.tcp_link.send(action)
