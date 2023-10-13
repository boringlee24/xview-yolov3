# How to run the demo

-----

## Setup

One CPU machine for the dashboard, one GPU machine with single A100 GPU for the backend execution.

## Run

Start the dashboard application on the CPU machine

Go to the demo dir 

```
cd demo
```
```
python animation.py --ip GPU_NODE_IP_ADDR
```

Enable MPS on GPU

```
cd mps
./enable_mps.sh 0
cd ../
```

Start the inference on the GPU machine

```
cd demo
```
```
python measure_power.py
```
Change the power limit to see different inference configurations.
```
# cancel the process in between the difference launches
python launch_parallel_detections_mps.py --power_limit 200
python launch_parallel_detections_mps.py --power_limit 230
python launch_parallel_detections_mps.py --power_limit 240
python launch_parallel_detections_mps.py --power_limit 250
python launch_parallel_detections_mps.py --power_limit 250 --disable
```

