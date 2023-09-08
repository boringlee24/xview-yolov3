import dash
from dash import html, dcc
from dash.dependencies import Output, Input
import random
import threading
import zmq
import numpy as np
import argparse

def get_throughput():
    global lat_meas
    context = zmq.Context()

    consumer = context.socket(zmq.PULL)
    consumer.connect(f"tcp://{args.ip}:5556")

    print('connected to throughput socket')
    while True:
        message = consumer.recv_string()
        if message == "STOP":
            break
        lat_meas.append(float(message))
        if len(lat_meas) > 1000:
            lat_meas.pop(0)

def get_power_limit():
    global power_limit, lat_meas, num_ins
    context = zmq.Context()

    consumer = context.socket(zmq.PULL)
    consumer.connect(f"tcp://{args.ip}:5557")
    print('connected to power limit socket')
    while True:
        message = consumer.recv_string()
        if message == "STOP":
            break
        lat_meas = []
        power_limit, num_ins = (int(k) for k in message.split(','))

# Define the receiver thread function
def get_power():
    global power_meas
    context = zmq.Context()

    consumer = context.socket(zmq.PULL)
    consumer.connect(f"tcp://{args.ip}:5555")

    print('connected to power socket')
    while True:
        message = consumer.recv_string()
        if message == "STOP":
            break
        power_meas.append(float(message))
        if len(power_meas) > 10:
            power_meas.pop(0)

app = dash.Dash(__name__)

app.layout = html.Div(
    [html.H1('Live Demo Dashboard'),
     html.Div(id='live-data', children='Initial Data'),
     dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # Trigger every 1 second (1000 milliseconds)
    ]
)

@app.callback(
    Output('live-data', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_data(n):
    # global power_meas, power_limit, lat_meas
    pwr = 0 if len(power_meas) == 0 else round(np.mean(power_meas),3)
    if len(lat_meas) == 0:
        throughput = 0
    else:
        throughput = round(num_ins * 1000 / np.mean(lat_meas),4)

    data1 = f"Throughput: {throughput} requests/sec"
    data2 = f"Power Consumption: {pwr} Watt"
    data3 = f"Power Limit: {power_limit} Watt"
    data4 = f"Number of Inference Instances: {num_ins}"
    return html.Div([data3, html.Br(), data2, html.Br(), data1, html.Br(), data4])  # Use html.Div to format the content with line breaks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Demo")
    parser.add_argument("--ip", type=str, help="Producer machine IP", default="10.99.103.101")
    args = parser.parse_args()

    power_meas, lat_meas = [], []
    power_limit = 250
    num_ins = 1
    latency = []
    x1 = threading.Thread(target=get_power, daemon=True)
    x2 = threading.Thread(target=get_power_limit, daemon=True)
    x3 = threading.Thread(target=get_throughput, daemon=True)
    x1.start()
    x2.start()
    x3.start()
    app.run_server(debug=False, port=8080)
