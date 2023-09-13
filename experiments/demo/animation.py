import dash
from dash import html, dcc
from dash.dependencies import Output, Input
import random
import threading
import zmq
import numpy as np
import argparse
import plotly.express as px

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
     html.Div(id='live-data', children='Initial Data', style={'fontSize': '24px'}),  # Increase font size here
     dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
     dcc.Graph(id='live-plot1', style={'width': '88%', 'height': '300px'}),  # Adjust width and height here
     dcc.Graph(id='live-plot2', style={'width': '80%', 'height': '300px'})  # Adjust width and height here
    ]
)

@app.callback(
    [Output('live-data', 'children'),
     Output('live-plot1', 'figure'),
     Output('live-plot2', 'figure')],
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

    global time_points, pwr_display, power_limit_display, throughput_display
    time_points.append(n)
    pwr_display.append(pwr)#power_meas[-1])
    power_limit_display.append(power_limit)
    throughput_display.append(throughput)

    if len(time_points) > history_limit:
        time_points = time_points[-history_limit:]
        pwr_display = pwr_display[-history_limit:]
        power_limit_display = power_limit_display[-history_limit:]
        throughput_display = throughput_display[-history_limit:]
    
    # create live plots
    fig1 = px.line(x=time_points, y=[pwr_display, power_limit_display], labels={'x': 'Time', 'y': 'Power (W)'})
    fig1.update_traces(line=dict(width=3.5), selector=dict(name='wide_variable_0'), line_color='coral', name='Power Consumption')
    fig1.update_traces(line=dict(width=3.5, dash='dash'), selector=dict(name='wide_variable_1'), line_color='darkorchid', name='Power Limit')
    fig1.update_yaxes(title_text='Power (W)', title_font=dict(size=18))
    fig1.update_xaxes(title_font=dict(size=18))
    fig2 = px.line(x=time_points, y=throughput_display, labels={'x': 'Time', 'y': 'Throughput (RPS)'})
    fig2.update_traces(line_color='darkolivegreen', line=dict(width=3.5))
    fig2.update_xaxes(title_font=dict(size=18))

    return html.Div([data3, html.Br(), data2, html.Br(), data1, html.Br(), data4]), fig1, fig2  # Use html.Div to format the content with line breaks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Demo")
    parser.add_argument("--ip", type=str, help="Producer machine IP", default="10.99.103.101")
    args = parser.parse_args()

    power_meas, lat_meas = [], []
    power_limit = 250
    num_ins = 0
    history_limit = 30
    time_points, pwr_display, power_limit_display, throughput_display = [], [], [], []

    x1 = threading.Thread(target=get_power, daemon=True)
    x2 = threading.Thread(target=get_power_limit, daemon=True)
    x3 = threading.Thread(target=get_throughput, daemon=True)
    x1.start()
    x2.start()
    x3.start()
    app.run_server(debug=False, port=8080)
