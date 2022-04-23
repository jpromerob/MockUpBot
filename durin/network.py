import socket
import multiprocessing
from typing import ByteString
from common import *

class TCPLink:
    """
    
    """
    def __init__(self, host: str, port: str):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = (host, int(port))

    def start_com(self):
        print(f"TCP communication started with {self.address}")
        self.socket.connect(self.address)

    # Send Command to Durin and wait for response
    def send(self, command: ByteString):
        self.socket.send(command)
        # buff = self.socket.recv(sizeof(Reply))
        # payload_in = Reply.from_buffer_copy(buff)
        # print(f"Reply: {payload_in.id}")

    def stop_com(self):
        print(f"TCP communication stopped with {self.address}")
        self.socket.close()
        
class UDPLink:
    """
    An UDPBuffer that silently buffers messages received over UDP into a queue.
    """

    def __init__(self, host: str, port: str, package_size: int = 1024, buffer_size: int = 1024):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = (host, int(port))
        self.is_buffering = False 
        self.package_size = package_size
        self.buffer = multiprocessing.Queue(buffer_size)
        self.thread = multiprocessing.Process(target=self._loop_buffer)

    def start_com(self):
        print("Start UDP reception")
        self.socket.bind(self.address)
        self.thread.start()
        self.is_buffering = True

    def _loop_buffer(self):
        count = 0

        while True:
            # data = self.socket.recv(self.package_size)
            try:
                buff, _ = self.socket.recvfrom(sizeof(Sensor))
                payload_in = Sensor.from_buffer_copy(buff)
                print(f"Received message: {payload_in.a}, {payload_in.b}, {payload_in.c}")
            except:
                print("Problem receiving sensory data")
                break
            count += 1
            self.buffer.put([4,5,count], block=False)

    # get data from buffer
    def get(self):
        if self.is_buffering:
            return self.buffer.get(block=True)
        else:
            print("Please start streaming on UDP")
            return False

    def stop_com(self):
        self.is_buffering = False
        self.socket.close()
        self.thread.terminate()
        self.thread.join()


# class UDPBuffer:
#     """
#     An UDPBuffer that silently buffers messages received over UDP into a queue.
#     """

#     def __init__(
#         self, host: str, port: str, package_size: int = 1024, buffer_size: int = 10
#     ):
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.address = (host, int(port))
#         self.package_size = package_size
#         self.thread = None
#         self.buffer = multiprocessing.Queue(buffer_size)
#         self.thread = multiprocessing.Process(target=self._loop_buffer)

#     def start_buffering(self):
#         self.socket.bind(self.address)
#         self.thread.start()

#     def _loop_buffer(self):
#         while True:
#             data = self.socket.recv(self.package_size)
#             self.buffer.put(data, block=False)

#     def get(self):
#         return self.buffer.get(block=True)

#     def send(self, data: ByteString):
#         self.socket.send(data)

#     def stop_buffering(self):
#         self.thread.terminate()
#         self.thread.join()
