from typing import Tuple
from actuator import DurinActuator
from sensor import DurinSensor, Observation, Sensor #DVSSensor
from network import TCPLink, UDPLink
from common import *
from cli import *

import torch


# class Durin(Actuator[Action], Sensor[Tuple[Observation, torch.Tensor]]): @TODO: uncomment
class Durin():    

    def __init__(self, host, port_tcp, port_udp):
        self.tcp_link = TCPLink(host, port_tcp)
        self.udp_link = UDPLink(host, port_udp)
        self.sensor = DurinSensor(self.udp_link)
        self.actuator = DurinActuator(self.tcp_link, self.udp_link) 
        # self.dvs = DVSSensor((128, 128), port + 1) @TODO: uncomment

    def __enter__(self):
        self.tcp_link.start_com()
        return self

    def __exit__(self, e, b, t):
        self.tcp_link.stop_com()

    # For Polling Commands
    def request(self, line):
        command, isvalid = parse_line(line)
        if isvalid:
            if line == "start_stream":
                self.udp_link.start_com()
            if line == "stop_stream":
                self.udp_link.stop_com()
            self.tcp_link.send(command)

    def __call__(self, command):
        reply_bytes = self.actuator(command)
        return reply_bytes

    def sense(self) -> Tuple[Observation, torch.Tensor]:
        durin = self.sensor.read()
        dvs = 1 # self.dvs.read() @TODO: uncomment
        return (durin, dvs)


