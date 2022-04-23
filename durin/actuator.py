from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ByteString, Callable, Generic, TypeVar
from network import TCPLink
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
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.rot = rot

    def encode(self):
        data = bytearray([0] * 7)
        data[0] = 2
        data[1] = 8 # id + byte_count + 3*2
        data[2:4] = bytearray(struct.pack("<h", self.vel_x)) #short (int16) little endian
        data[4:6] = bytearray(struct.pack("<h", self.vel_y)) #short (int16) little endian
        data[6:8] = bytearray(struct.pack("<h", self.rot)) #short (int16) little endian
        print(data)
        return data


class DurinActuator():
    def __init__(self, link: TCPLink):
        self.link = link

    def __call__(self, action: Command):
        command_bytes = action.encode()
        self.link.send(command_bytes)

    def write(self, action):
        self.link.send(action)
