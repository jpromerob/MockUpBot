from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ByteString, Callable, Generic, Tuple, TypeVar
from network import UDPLink

import torch
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

    def read(self) -> Observation:
        return self.link.get()


# class MockSensor(Sensor[...]):
#     pass
