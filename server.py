###
##
## This script reads DVS frames from a number of sockets, sends them to a GPU model and emits a pose estimate to a TCP server
##
###

import argparse
import io
import logging
import multiprocessing
import socket
import struct
import numpy as np
import time

import torch

import coordinates
from model_inference import ModelInference

from udpstream import UDPStream


CAMERA_SHAPE = (640, 480)


def sender(host, ports, queue):
    sockets = []
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        sockets.append(s)
    t = time.time()
    count = 0
    try:
        while True:
            tensors = queue.get()
            for i in range(len(sockets)):
                tensor = tensors[i]
                s = sockets[i]
                bytes = (
                    struct.pack("<f", tensor[0])
                    + struct.pack("<f", tensor[1])
                    + struct.pack("<f", tensor[2])
                )
                s.send(bytes)
            count += 1
            if time.time() >= t + 1:
                logging.debug(
                    f"Sending {count}/s - {tensor[0]},{tensor[1]},{tensor[2]}"
                )
                count = 0
                t = time.time()

    except Exception as e:
        logging.warn("Sender closing", e)
    finally:
        s.close()


def printer(host, port, queue):
    t = time.time()
    count = 0
    try:
        while True:
            tensor = queue.get()
            count += 1
            if time.time() >= t + 1:
                logging.debug(
                    f"Sending {count}/s - {tensor[0]},{tensor[1]},{tensor[2]}"
                )
                count = 0
                t = time.time()
    except Exception as e:
        logging.warn("Printer closing", e)


def predictor(checkpoint: str, queue_out: multiprocessing.Queue, interval: float):
    try:
        t_0 = time.time()
        t_l = time.time()
        c = 0
        c_total = 0

        model = ModelInference(checkpoint, "cuda")
        stream0 = UDPStream(2300, torch.Size((640, 480)), "cuda:0")
        stream1 = UDPStream(2301, torch.Size((640, 480)), "cuda:0")
        stream2 = UDPStream(2302, torch.Size((640, 480)), "cuda:0")
        c2w = coordinates.get_transmats(coordinates.set_cam_poses())

        logging.info(f"Listening with a {interval * 1000}ms interval")
        while True:
            t_1 = time.time()
            if t_1 >= t_0 + interval:
                t_0 = t_1
                tensor0 = stream0.read().view(CAMERA_SHAPE[0], CAMERA_SHAPE[1])
                tensor1 = stream1.read().view(CAMERA_SHAPE[0], CAMERA_SHAPE[1])
                tensor2 = stream2.read().view(CAMERA_SHAPE[0], CAMERA_SHAPE[1])
                tensor = torch.stack([tensor0, tensor1, tensor2]).view(
                    3, 1, CAMERA_SHAPE[0], CAMERA_SHAPE[1]
                )
                pose = model.predict_channel(tensor)
                # transformed = coordinates.camera_to_world(pose, c2w, index=1)
                # if np.any(np.isnan(transformed)):
                #     print("NAN!", transformed)
                # if np.any(transformed < -1000) or np.any(transformed > 1000):
                #     print("LARGE!", transformed)
                # transformed = np.nan_to_num(transformed, 0)
                if not queue_out.full():
                    queue_out.put(pose, block=False)

                c += 1
                c_total += 1
                # if c_total % 1000 == 0:
                # print(f"{pose[0]: 3f} {pose[1]: 3f} {pose[2]: 3f}")

            if time.time() >= t_l + 1:
                print(f"Receiving {c}/s")
                c = 0
                t_l = time.time()

    except Exception as e:
        logging.warn("Predictor closing", e)


def main(args):
    logging.getLogger().setLevel(args.logging)

    interval = args.interval / 1000  # ms to seconds

    # Sending process
    queue_out = multiprocessing.Queue(100)
    host, port = args.destination.split(":")
    ports = [3000, 3001, 3002]
    sending_process = multiprocessing.Process(
        target=sender, args=(host, ports, queue_out)
        # target=printer, args=(host, ports, queue_out),
    )

    # Predictor process
    predictor_process = multiprocessing.Process(
        target=predictor, args=(args.checkpoint, queue_out, interval)
    )

    sending_process.start()
    predictor_process.start()

    sending_process.join()
    predictor_process.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Start process for receiving events and emitting poses"
    )
    parser.add_argument(
        "destination", type=str, help="Destination for sending pose over TCP"
    )
    parser.add_argument(
        "checkpoint", type=str, help="Path for python model checkpoint file"
    )
    parser.add_argument("--device", type=str, default="cuda", help="PyTorch device")
    parser.add_argument(
        "--host", type=str, default="172.16.222.46", help="Host sending events"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=2,
        help="Time interval between predictions in ms",
    )
    parser.add_argument(
        "--visualize", action="store_true", default=False, help="Host sending events"
    )
    parser.add_argument("--logging", type=str, default="DEBUG", help="Log level")
    args = parser.parse_args()
    main(args)
