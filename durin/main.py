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
        while True:

            if args.mode == "cli":
                cli_command = input()
                reply = durin(Request(cli_command))
                

            elif args.mode == "brain":
                
                pdb.set_trace()
                
                # Activating/deactivating continuous streaming of sensory data on UDP
                reply = durin(StreamOn('127.0.0.1', 4300, 2000))
                time.sleep(10)
                reply = durin(StreamOff())

                # Powering durin off
                reply = durin(Request('power_off'))
                time.sleep(0.1)

                # Move Durin using robcentric command
                reply = durin(MoveRobcentric(-1,2,3))
                time.sleep(0.1)

                # Get sensory data from sensor 128
                reply = durin(PollSensor(128))
                time.sleep(0.1)

                # Get sensory data from sensor 129
                reply = durin(PollSensor(129))
                time.sleep(0.1)

                # Get sensory data from sensor 130
                reply = durin(PollSensor(130))
                time.sleep(0.1)

                # Get sensory data from sensor 131
                reply = durin(PollSensor(131))
                time.sleep(0.1)

                # Get sensory data from sensor 132
                reply = durin(PollSensor(132))
                time.sleep(0.1)

                # Get sensory data from sensor 133
                reply = durin(PollSensor(133))
                time.sleep(0.1)

                # Activating/deactivating continuous streaming of sensory data on UDP
                reply = durin(StreamOn('127.0.0.1', 4700, 500))
                time.sleep(10)
                reply = durin(StreamOff())

                pdb.set_trace()
                
            else:
                print("Wrong Mode")
                break

