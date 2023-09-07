import dash
from dash import html, dcc
from dash.dependencies import Output, Input
import random
import threading
import zmq
import numpy as np
import argparse

# Define the receiver thread function
def receiver_thread():
    global power_meas
    context = zmq.Context()

    consumer = context.socket(zmq.PULL)
    consumer.connect(f"tcp://{args.ip}:5555")

    print('connected')
    while True:
        message = consumer.recv_string()
        if message == "STOP":
            break
        power_meas.append(float(message))
        if len(power_meas) > 10:
            power_meas.pop(0)

app = dash.Dash(__name__)

app.layout = html.Div(
    [html.H1('Live Data Example'),
     html.Div(id='live-data', children='Initial Data'),
     dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # Trigger every 1 second (1000 milliseconds)
    ]
)

@app.callback(
    Output('live-data', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_data(n):
    global power_meas
    data1 = f"Updated Data: {random.random()}"
    pwr = 0 if len(power_meas) == 0 else round(np.mean(power_meas),3)
    data2 = f"Power Consumption: {pwr}W"
    return html.Div([data1, html.Br(), data2])  # Use html.Div to format the content with line breaks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Demo")
    parser.add_argument("--ip", type=str, help="Producer machine IP", default="10.99.103.101")
    args = parser.parse_args()

    power_meas = []
    x = threading.Thread(target=receiver_thread, daemon=True)
    x.start()
    app.run_server(debug=False, port=8080)
