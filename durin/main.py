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
                # pdb.set_trace()
                reply = durin(StreamOn('127.0.0.1', 4300, 2000))
                time.sleep(10)
                reply = durin(StreamOff())
                reply = durin(Request('power_off'))
                time.sleep(0.1)
                reply = durin(MoveRobcentric(-1,2,3))
                time.sleep(0.1)
                reply = durin(PollSensor(128))
                time.sleep(0.1)
                reply = durin(PollSensor(129))
                time.sleep(0.1)
                reply = durin(PollSensor(130))
                time.sleep(0.1)
                reply = durin(PollSensor(131))
                time.sleep(0.1)
                reply = durin(PollSensor(132))
                time.sleep(0.1)
                reply = durin(PollSensor(133))
                time.sleep(0.1)
                reply = durin(StreamOn('127.0.0.1', 4700, 500))
                time.sleep(10)
                reply = durin(StreamOff())

                pdb.set_trace()
                # obs = durin.sense()
                # ... # do some processing ... 
                # durin.actuate(move_rc(1,1,1))
                # during.actuate(move_4w(1,2,3,4))
            else:
                print("Wrong Mode")
                break

