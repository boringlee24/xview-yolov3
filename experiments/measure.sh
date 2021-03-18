#!/bin/bash
#echo "run nvidia-smi command to monitor gpu power"

TYPE=$1

./pwr_meas.sh ${TYPE} & python detect.py -tc ${TYPE}

