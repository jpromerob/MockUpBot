import time
import pdb

from dataclasses import dataclass
from typing import List, Optional
from durin import Durin
from common import *
from actuator import *
from cli import *



if __name__ == "__main__":

    args = parse_args()
    

    with Durin(args.host, args.tcp) as durin:

        if args.mode == "cli":
            while True:
                cli_command = input()
                reply = durin(Request(cli_command))
            

        elif args.mode == "brain":

            # # Powering durin off
            # reply = durin(Request('power_off'))
            # time.sleep(0.1)

            # # Move Durin using robcentric command
            # reply = durin(MoveRobcentric(-1,2,3))
            # time.sleep(0.1)

            # # Get sensory data from sensor 128
            # reply = durin(PollSensor(128))
            # time.sleep(0.1)

            # # Get sensory data from sensor 129
            # reply = durin(PollSensor(129))
            # time.sleep(0.1)

            # # Get sensory data from sensor 130
            # reply = durin(PollSensor(130))
            # time.sleep(0.1)

            # # Get sensory data from sensor 131
            # reply = durin(PollSensor(131))
            # time.sleep(0.1)

            # # Get sensory data from sensor 132
            # reply = durin(PollSensor(132))
            # time.sleep(0.1)

            # # Get sensory data from sensor 133
            # reply = durin(PollSensor(133))
            # time.sleep(0.1)

        
            # Activating/deactivating continuous streaming of sensory data on UDP
            reply = durin(StreamOn('127.0.0.1', 4300, 2000))
            time.sleep(2.5)
            reply = durin(StreamOff())
            count = 0
            while count < 10:
                
                data = durin.sense()
                print("ToF Sensors:")
                print(data[0][0])
                print("Charge:")
                print(data[0][1])
                print("Voltage:")
                print(data[0][2])
                print("IMU:")
                print(data[0][3])
                print("UWB:")
                print(data[0][4])
                count += 1
                time.sleep(0.1)
                print("\n\n\n")


            print("Waiting some time ... ")
            time.sleep(5)


            # Activating/deactivating continuous streaming of sensory data on UDP
            reply = durin(StreamOn('127.0.0.1', 4700, 500))
            count = 0
            while count < 10:
                
                pdb.set_trace()

                data = durin.sense()
                count += 1
                time.sleep(0.1)

            reply = durin(StreamOff())

                
        else:
            print("Wrong Mode")

