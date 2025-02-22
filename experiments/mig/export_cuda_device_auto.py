import json
import mig_helper
import os
user = os.environ.get('USER')
import sys
import subprocess
import io
import numpy as np
import socket

node = socket.gethostname()
with open(f'partition_code.json') as f:
    partition_code = json.load(f)
    if os.path.exists('mig_device_autogen.json'):
        with open('mig_device_autogen.json') as f:
            export = json.load(f)
    else:
        export = {}

def correct_order(device_ids, partition):
    result = []
    for p in partition:
        xg = f'{p}g.'
        for d in device_ids:
            if xg in d[0]:
                result.append(d[1])
                device_ids.remove(d)
                break
    if len(device_ids) > 0:
        raise RuntimeError('correct order fault')
    return result

def read_cuda_device(gpuid, partition):
    num_slices = len(partition)
    cmd = 'nvidia-smi -L'
    p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
    p.wait()
    read = p.stdout.read().decode("utf-8")
    buf = io.StringIO(read)
    start = False
    line_cnt = 0
    device_ids = []
    while True:
        line = buf.readline()
        if line_cnt >= num_slices:
            device_ids = correct_order(device_ids, partition)
            return device_ids            
        if start:
            if 'UUID: ' not in line:
                raise RuntimeError('UUID not found')
            mig_str = line.split('UUID: ')[1]
            mig_str = mig_str.strip(')\n')
            slice_str = line.split(' ')[3]
            device_ids.append((slice_str, mig_str))
            line_cnt += 1
        if f'GPU {gpuid}: NVIDIA' in line:
            start = True

#mig_helper.init_mig()
export[node] = {}
num_to_str = {7: '7g.40gb', 4: '4g.20gb', 3: '3g.20gb', 2: '2g.10gb', 1: '1g.5gb'}

for gpuid in range(2):
    export[node][f'gpu{gpuid}'] = {}
    for code in partition_code:
        mig_helper.reset_mig(gpuid)
        export[node][f'gpu{gpuid}'][code] = []
        partition = partition_code[code] # [2,2,2,1]

        for p in partition:
            sliceid = num_to_str[p]
            mig_helper.create_ins(gpuid, sliceid)
        device_ids = read_cuda_device(gpuid, partition)
        export[node][f'gpu{gpuid}'][code] = device_ids[:]


with open('mig_device_autogen.json', 'w') as f:
    json.dump(export, f, indent=4)


