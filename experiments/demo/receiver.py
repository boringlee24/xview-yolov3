import zmq
import time
import dash
from dash import html, dcc
from dash.dependencies import Output, Input
import random
import threading
import numpy as np


def receiver_thread():
    global power_meas
    context = zmq.Context()

    # Consumer
    consumer = context.socket(zmq.PULL)
    consumer.connect("tcp://127.0.0.1:5555")

    # Receiving data
    received_data = consumer.recv_string()
    print(f"Received: {received_data}")
    power_meas.append(float(received_data))

    consumer.close()
    context.term()

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
    pwr = 0 if len(power_meas) == 0 else np.mean(power_meas)
    data2 = f"Power Consumption: {pwr}"
    return html.Div([data1, html.Br(), data2])  # Use html.Div to format the content with line breaks

if __name__ == '__main__':
    power_meas = []
    x = threading.Thread(target=receiver_thread, daemon=True)
    x.start()
    app.run_server(debug=False, port=8080)

    # while True:
    #     time.sleep(1)
    #     print('waiting')