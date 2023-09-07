import time
import pynvml
import zmq
import numpy as np

# Function to read GPU power usage using pynvml
def read_gpu_power():
    try:
        pynvml.nvmlInit()
        power_usage = []

        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        for i in range(10):
            power_info = pynvml.nvmlDeviceGetPowerUsage(handle)
            power_usage.append(power_info / 1000.0)  # Convert to watts
            time.sleep(0.1)

        pynvml.nvmlShutdown()
        return round(np.mean(power_usage),2)
    except pynvml.NVMLError as e:
        return None

# Function to send GPU power usage to another process
def send_power_data(data, producer):
    # Replace this part with your preferred method for sending data to another process
    # For simplicity, we print the data here
    # for i, power in enumerate(data):
    #     print(f"GPU {i} Power Usage: {power} Watts")
    producer.send_string(str(data))

if __name__ == '__main__':
    context = zmq.Context()
    #  Socket to talk to server
    print("Starting GPU measurement")
    producer = context.socket(zmq.PUSH)
    # producer.bind("tcp://127.0.0.1:5555")
    producer.bind("tcp://0.0.0.0:5555")

    while True:
        power_usage = read_gpu_power()
        if power_usage is not None:
            send_power_data(power_usage, producer)