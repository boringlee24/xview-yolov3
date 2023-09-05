#!/bin/bash
#echo "run nvidia-smi command to monitor gpu power"

TYPE=$1
MODE="mps"

./pwr_meas.sh ${TYPE} & python launch_parallel_detections_${MODE}.py --${MODE}_config ${TYPE}

