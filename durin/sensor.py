from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ByteString, Callable, Generic, Tuple, TypeVar
from network import UDPLink

import torch
import numpy as np
# import aestream


T = TypeVar("T")


@dataclass
class Observation:
    pass


class Sensor(ABC, Generic[T]):
    @abstractmethod
    def read(self) -> T:
        pass


# class DVSSensor(Sensor[torch.Tensor]):
#     def __init__(self, shape: Tuple[int, int], port: int):
#         self.source = aestream.UDPInput(shape, port)

#     def read(self) -> torch.Tensor:
#         return self.source.read()


class DurinSensor(Sensor[Observation]):
    def __init__(self, link: UDPLink):
        self.link = link
        self.tof = np.zeros((8,8*8))
        self.uwb = np.zeros((0,))
        self.charge = 0
        self.voltage = 0
        self.imu = np.zeros((3,3))

    def read(self) -> Observation:
        (sensor_id, data) = self.link.get()
        if sensor_id >= 128 and sensor_id <= 131:
            idx = sensor_id - 128
            self.tof[:,idx*16:idx*16+16] = data
        if sensor_id == 132:
            self.charge = data[0]
            self.voltage = data[1]
            self.imu = data[2]
        if sensor_id == 133:
            self.uwb = data

        return (self.tof, self.charge, self.voltage, self.imu, self.uwb)

