from mig import mig_helper
import json
from pathlib import Path
import subprocess
import argparse
import socket
import time
from typing import List
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
MIG_DIR = f'{str(ROOT)}/mig'

def config_gpu(gpuid, mig_config: str):
    # reset the GPU
    mig_helper.reset_mig(gpuid)

    # partition to desired config
    with open(f'{MIG_DIR}/partition_code.json') as f:
        partition = json.load(f)
    mig_helper.do_partition(gpuid, partition[mig_config])

def launch(mig_config: str):
    with open(f'{MIG_DIR}/partition_code.json') as f:
        partition = json.load(f)
    num_slices = len(partition[mig_config])
    with open(f'{MIG_DIR}/mig_device_autogen.json') as f:
        device_json = json.load(f)

    Path('/scratch/li.baol/xview_logs').mkdir(parents=True, exist_ok=True)
    Path(f'logs/mig_config_{mig_config}/').mkdir(parents=True, exist_ok=True)
    mig_list = device_json[hostname][f'gpu0'][mig_config]
    procs = []
    for i in range(num_slices):
        device = mig_list[i]
        cmd = f'CUDA_VISIBLE_DEVICES={device} python detect.py \
                --epochs {args.epochs} --batch_size {args.batch_size} \
                --tc mig_config_{mig_config}/mig_{i}' 
        print(cmd)
        out_file = f'/scratch/li.baol/xview_logs/yolo{i}.out'
        err_file = f'/scratch/li.baol/xview_logs/yolo{i}.err'
        with open(out_file, 'w+') as out, open(err_file, 'w+') as err:
            proc = subprocess.Popen([cmd], shell=True, stdout=out, stderr=err)
            procs.append(proc)
        time.sleep(0.1)
    for proc in procs:
        proc.wait()

def parse():
    parser = argparse.ArgumentParser()
    # parser.add_argument('--mig_config', type=str, default='0', help='configuration of MIG according to NVIDIA table, 0-17')    
    # parser.add_argument('--gpuid', type=int, default=0, help='GPU ID (0 or 1)')  
    # parser.add_argument('--weights', type=str, default='yolov5x6', help='model name: yolov5s, yolov5x, yolov5x6')
    # parser.add_argument('--term', action='store_true', help='terminate services', default=False)        
    parser.add_argument('--epochs', type=int, default=3, help='number of epochs')
    parser.add_argument('--batch_size', type=int, default=1, help='size of the batches')
    parser.add_argument('--mig_config', type=str, default="0", help='testcase')
    args = parser.parse_args()
    # args.imgsz *= 2 if len(args.imgsz) == 1 else 1  # expand
    print(args)
    return args    

if __name__ == '__main__':
    args = parse()
    hostname = socket.gethostname()
    config_gpu(0, args.mig_config)
    time.sleep(5)
    launch(args.mig_config)

