

import argparse
import numpy as np

from common import *

def parse_args():
    parser = argparse.ArgumentParser(description='Connect to Durin and exert control')

    parser.add_argument('mode', type= str, help="Operating Mode: 'cli' or 'brain'", default="cli")
    parser.add_argument('--host', type= str, help="Durin's IP address", default="127.0.0.1")
    parser.add_argument('--tcp', type= str, help="Durin's TCP port", default=2300)
    parser.add_argument('--udp', type= str, help="Durin's UDP port", default=5000)

    return parser.parse_args()

def show_content(filepath):
    with open(filepath) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            print(f"cmd {line.strip()}")
            line = fp.readline()
            cnt += 1


def parse_line(line):
    
    cmd_id = 0
    arg_nb = 0
    arg_array = []
    isvalid = False

    # List of available commands
    filepath = 'commands.txt'

    # Ignore 'enter'
    if len(line)>0:

        # Break line into 'words' (i.e. command + arguments) and count arguments
        line = line.split()
        command = line[0]
        arg_nb = len(line)-1
        arg_array = line[1:arg_nb+1]

        # Check if line command matches any available command
        if command == "list":
            show_content(filepath)
        else:
            with open(filepath) as fp:
                while True:
                    line = fp.readline()
                    if not line:
                        break
                    line = line.split()

                    # Check if requested command matches current available one 
                    if command == line[1]:
                        # Check if #args makes sense
                        if len(line) == 2+len(arg_array):
                            cmd_id = int(line[0])
                            isvalid = True
                            break
            if cmd_id == 0:
                print("Wrong Command/Arguments ... ")

    while len(arg_array) < 3:
        arg_array.append("0")
    arg_array=np.array(arg_array, dtype=float)

    command = Command(cmd_id, arg_nb, arg_array[0], arg_array[1], arg_array[2])
    # print("\n")
    return command, isvalid
