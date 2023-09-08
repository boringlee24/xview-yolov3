# How to run the demo

-----

## Setup

One CPU machine for the dashboard, one GPU machine with single A100 GPU for the backend execution.

## Run

Go to the demo dir 

```
cd demo
```

Start the dashboard application on the CPU machine

```
python animation.py --ip GPU_NODE_IP_ADDR
```

Start the inference on the GPU machine

```
python launch_parallel_detections_mps.py --power_limit 180
```

Change the power limit to see different inference configurations.