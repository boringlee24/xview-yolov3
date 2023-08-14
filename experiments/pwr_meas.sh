#!/bin/bash
#echo "run nvidia-smi command to monitor gpu power"

GPU="0"
TYPE=$1
DATA_PATH="logs"
RUNTIME=60
mkdir -p ${DATA_PATH}/mig_config_${TYPE}

sleep 30
timeout ${RUNTIME} nvidia-smi -i ${GPU} --query-gpu=index,timestamp,power.draw,memory.used,utilization.memory,utilization.gpu,temperature.gpu --format=csv,nounits -lms 50 --filename=${DATA_PATH}/mig_config_${TYPE}/power.csv 

#sleep 305 && python gpu_pwr.py $JOB

#mv ${DATA_PATH}${JOB}.csv ${DATA_PATH}${JOB}_finish.csv

#while [ $SAMPLE -lt $NUM_SAMPLES ]
#do
#    timeout ${RUN_TIME} nvidia-smi -i 0 --query-gpu=index,timestamp,power.draw,memory.used,utilization.memory,utilization.gpu,temperature.gpu --format=csv,nounits -lms 10 --filename=${DATA_PATH}${JOB}/sample_${SAMPLE}.csv
#    sleep $SAMPLING_INTERVAL
#    ((SAMPLE++))
#done
