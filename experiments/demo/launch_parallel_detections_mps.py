from pathlib import Path
import subprocess
import argparse
import socket
import time
from typing import List
FILE = Path(__file__).resolve()
import os
os.chdir('../')
import zmq

def get_mps_config(power_limit: int):
    if power_limit >= 245:
        return '20'
    elif power_limit >= 240:
        return '25'
    elif power_limit >= 215:
        return '50'
    else:
        return 100
    
def launch(power_limit: int):
    mps_config = get_mps_config(power_limit)
    Path('/scratch/li.baol/xview_logs').mkdir(parents=True, exist_ok=True)
    procs = []
    num_slices = int(100 / int(mps_config))
    producer.send_string(f'{power_limit},{num_slices}')
    for i in range(num_slices):
        new_option = '--send_zmq' if i == 0 else ''
        cmd = f'python detect_and_send.py \
                --epochs {args.epochs} --batch_size {args.batch_size} \
                --tc mps_config_{mps_config}/mps_{i} --mps_set --mps_pct {mps_config} {new_option}'
        print(cmd)
        out_file = f'/scratch/li.baol/xview_logs/yolo{i}.out'
        err_file = f'/scratch/li.baol/xview_logs/yolo{i}.err'
        with open(out_file, 'w+') as out, open(err_file, 'w+') as err:
            proc = subprocess.Popen([cmd], shell=True, stdout=out, stderr=err)
            procs.append(proc)
        time.sleep(0.1)
    for proc in procs:
        proc.wait()

def launch_disabled(power_limit: int):
    mps_config = 100
    Path('/scratch/li.baol/xview_logs').mkdir(parents=True, exist_ok=True)
    procs = []
    num_slices = 1
    producer.send_string(f'{power_limit},{num_slices}')
    new_option = '--send_zmq'
    cmd = f'python detect_and_send.py \
            --epochs {args.epochs} --batch_size {args.batch_size} \
            --tc mps_config_{mps_config}/mps_0 --mps_set --mps_pct {mps_config} {new_option}'
    print(cmd)
    out_file = f'/scratch/li.baol/xview_logs/yolo0.out'
    err_file = f'/scratch/li.baol/xview_logs/yolo0.err'
    with open(out_file, 'w+') as out, open(err_file, 'w+') as err:
        proc = subprocess.Popen([cmd], shell=True, stdout=out, stderr=err)
        procs.append(proc)
    time.sleep(0.1)
    for proc in procs:
        proc.wait()

def parse():
    parser = argparse.ArgumentParser()
    # parser.add_argument('--mps_config', type=str, default='0', help='configuration of MIG according to NVIDIA table, 0-17')    
    # parser.add_argument('--gpuid', type=int, default=0, help='GPU ID (0 or 1)')  
    # parser.add_argument('--weights', type=str, default='yolov5x6', help='model name: yolov5s, yolov5x, yolov5x6')
    # parser.add_argument('--term', action='store_true', help='terminate services', default=False)        
    parser.add_argument('--epochs', type=int, default=20, help='number of epochs')
    parser.add_argument('--batch_size', type=int, default=1, help='size of the batches')
    parser.add_argument('--power_limit', type=int, default=250, help='power limit in W')
    parser.add_argument('--disable', action='store_true', help='disable automatic MPS spawn', default=False)
    args = parser.parse_args()
    # args.imgsz *= 2 if len(args.imgsz) == 1 else 1  # expand
    print(args)
    return args    

if __name__ == '__main__':
    args = parse()
    hostname = socket.gethostname()
    context = zmq.Context()
    producer = context.socket(zmq.PUSH)
    producer.bind("tcp://0.0.0.0:5557")

    if args.disable:
        launch_disabled(args.power_limit)
    else:
        launch(args.power_limit)

