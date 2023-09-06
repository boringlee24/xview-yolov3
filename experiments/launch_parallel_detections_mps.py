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

def launch(mps_config: str):

    Path('/scratch/li.baol/xview_logs').mkdir(parents=True, exist_ok=True)
    Path(f'logs/mps_config_{mps_config}/').mkdir(parents=True, exist_ok=True)
    procs = []
    num_slices = int(100 / int(args.mps_config))
    for i in range(num_slices):
        cmd = f'python detect.py \
                --epochs {args.epochs} --batch_size {args.batch_size} \
                --tc mps_config_{mps_config}/mps_{i} --mps_set --mps_pct {args.mps_config}'
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
    # parser.add_argument('--mps_config', type=str, default='0', help='configuration of MIG according to NVIDIA table, 0-17')    
    # parser.add_argument('--gpuid', type=int, default=0, help='GPU ID (0 or 1)')  
    # parser.add_argument('--weights', type=str, default='yolov5x6', help='model name: yolov5s, yolov5x, yolov5x6')
    # parser.add_argument('--term', action='store_true', help='terminate services', default=False)        
    parser.add_argument('--epochs', type=int, default=3, help='number of epochs')
    parser.add_argument('--batch_size', type=int, default=1, help='size of the batches')
    parser.add_argument('--mps_config', type=str, default="100", help='testcase')
    args = parser.parse_args()
    # args.imgsz *= 2 if len(args.imgsz) == 1 else 1  # expand
    print(args)
    return args    

if __name__ == '__main__':
    args = parse()
    hostname = socket.gethostname()
    time.sleep(5)
    launch(args.mps_config)

