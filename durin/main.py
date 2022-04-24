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
    

    with Durin(args.host, args.tcp, args.udp) as durin:
        while True:

            if args.mode == "cli":
                cli_command = input()
                reply = durin(Request(cli_command))

            elif args.mode == "brain":
                pdb.set_trace()
                # obs = durin.sense()
                # ... # do some processing ... 
                # durin.actuate(move_rc(1,1,1))
                # during.actuate(move_4w(1,2,3,4))
                pass
            else:
                print("Wrong Mode")
                break

