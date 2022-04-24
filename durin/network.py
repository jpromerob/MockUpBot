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
        return self.socket.recv(1024)


    def stop_com(self):
        print(f"TCP communication stopped with {self.address}")
        self.socket.close()
        
class UDPLink:
    """
    An UDPBuffer that silently buffers messages received over UDP into a queue.
    """

    def __init__(self, package_size: int = 1024, buffer_size: int = 1024):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.is_buffering = False 
        self.package_size = package_size
        self.buffer = multiprocessing.Queue(buffer_size)
        self.thread = multiprocessing.Process(target=self._loop_buffer)

    def start_com(self, address):
        print("Start UDP reception")
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(address)
        self.thread.start()
        self.is_buffering = True

    def _loop_buffer(self):
        count = 0

        while True:
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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.thread = multiprocessing.Process(target=self._loop_buffer)


