import time
import pynvml
import zmq
import numpy as np
import json

# Function to read GPU power usage using pynvml
def read_gpu_power(measurement_dict):
    try:
        pynvml.nvmlInit()
        power_usage = []
        temperatures = []
        sm_utilizations = []
        memory_utilizations = []
        memory_usages = [] 

        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        for i in range(10):
            power_info = pynvml.nvmlDeviceGetPowerUsage(handle)
            power_usage.append(power_info / 1000.0)  # Convert to watts

            # Temperature
            temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            temperatures.append(temperature)

            # SM utilization and memory utilization
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            sm_utilizations.append(utilization.gpu)
            memory_utilizations.append(utilization.memory)

            # GPU memory usage in MB
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            memory_usages.append((memory_info.used) / (1024**2))  # Convert to MB

            time.sleep(0.1)

        pynvml.nvmlShutdown()
        measurement_dict['power'] = round(np.mean(power_usage),2)
        measurement_dict['temp'] = round(np.mean(temperatures),2)
        measurement_dict['sm'] = round(np.mean(sm_utilizations),2)
        measurement_dict['mem'] = round(np.mean(memory_utilizations),2)
        measurement_dict['mem_usage'] = round(np.mean(memory_usages))  # Add memory usage to the dict

        return measurement_dict
    except pynvml.NVMLError as e:
        return None

# Function to send GPU power usage to another process
def send_meas_data(data, producer):
    # serialize the data in json format
    json_serialized_data = json.dumps(data)
    producer.send_string(json_serialized_data)

if __name__ == '__main__':
    context = zmq.Context()
    #  Socket to talk to server
    print("Starting GPU measurement")
    producer = context.socket(zmq.PUSH)
    # producer.bind("tcp://127.0.0.1:5555")
    producer.bind("tcp://0.0.0.0:5555")

    measurement_dict = {}

    while True:
        measurements = read_gpu_power(measurement_dict)
        if measurements is not None:
            send_meas_data(measurements, producer)