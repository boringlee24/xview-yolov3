import dash
from dash import html, dcc
from dash.dependencies import Output, Input
import random
import threading
import zmq
import numpy as np
import argparse
import plotly.express as px
import json

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
def get_measurements():
    global power_meas, temp_meas, sm_meas, mem_meas, mem_usage_meas
    context = zmq.Context()

    consumer = context.socket(zmq.PULL)
    consumer.connect(f"tcp://{args.ip}:5555")

    print('connected to power socket')
    while True:
        message = consumer.recv_string()
        if message == "STOP":
            break
        metrics = json.loads(message)
        power_meas.append(float(metrics['power']))
        temp_meas.append(float(metrics['temp']))
        sm_meas.append(float(metrics['sm']))
        mem_meas.append(float(metrics['mem']))
        mem_usage_meas.append(float(metrics['mem_usage']))
        
        if len(power_meas) > 10:
            power_meas.pop(0)
            temp_meas.pop(0)
            sm_meas.pop(0)
            mem_meas.pop(0)
            mem_usage_meas.pop(0)

app = dash.Dash(__name__)

app.layout = html.Div(
    [html.H1('Live Demo Dashboard'),
     html.Div(id='live-data', children='Initial Data', style={'fontSize': '24px', 'display': 'flex'}),  # Increase font size here
     dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
     dcc.Graph(id='live-plot1', style={'width': '88%', 'height': '300px', 'margin': '0'}), # Adjust width and height here
     dcc.Graph(id='live-plot2', style={'width': '80%', 'height': '300px', 'margin': '0'})  # Adjust width and height here
    ]
)

@app.callback(
    [Output('live-data', 'children'),
     Output('live-plot1', 'figure'),
     Output('live-plot2', 'figure')],
    Input('interval-component', 'n_intervals')
)
def update_data(n):
    global time_points, pwr_display, power_limit_display, throughput_display
    global temp_meas, sm_meas, mem_meas, mem_usage_meas

    # global power_meas, power_limit, lat_meas
    pwr = 0 if len(power_meas) == 0 else round(np.mean(power_meas),3)
    temp = 0 if len(temp_meas) == 0 else round(np.mean(temp_meas),3)
    sm = 0 if len(sm_meas) == 0 else round(np.mean(sm_meas),3)
    mem = 0 if len(mem_meas) == 0 else round(np.mean(mem_meas),3)
    mem_usage = 0 if len(mem_usage_meas) == 0 else round(np.mean(mem_usage_meas))

    if len(lat_meas) == 0 and len(throughput_display) == 0:
        throughput = 0
    elif len(lat_meas) == 0:
        throughput = throughput_display[-1]
    else:
        throughput = round(num_ins * 1000 / np.mean(lat_meas),4)

    # data1 = f"Throughput: {throughput} requests/sec"
    # data2 = f"Power Consumption: {pwr} Watt"
    # data3 = f"Power Limit: {power_limit} Watt"
    # data4 = f"Number of Inference Instances: {num_ins}"

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
    fig1.update_traces(line=dict(width=3.5, dash='dash'), selector=dict(name='wide_variable_1'), line_color='dodgerblue', name='Power Limit')
    fig1.update_yaxes(title_text='Power (W)', title_font=dict(size=18), range=[150, 260])
    fig1.update_xaxes(title_font=dict(size=17))
    fig1.update_layout(title='Inference Power', title_font=dict(size=22))

    fig2 = px.line(x=time_points, y=throughput_display, labels={'x': 'Time', 'y': 'Throughput (RPS)'})
    fig2.update_traces(line_color='darkolivegreen', line=dict(width=3.5))
    fig2.update_xaxes(title_font=dict(size=17))
    fig2.update_yaxes(title_text='Throughput (RPS)', title_font=dict(size=18), range=[3.5, 7.5])
    fig2.update_layout(title='Inference Throughput', title_font=dict(size=22))

    box_style = {'border': '5px solid #ccc', 'padding': '5px', 'margin-right': '10px', 'width': '240px', 'height': '80px'}
    text_style = {'font-size': '20px', 'text-align': 'center'}
    subtext_style = {'fontSize': '19px', 'color': 'red', 'text-align': 'center', 'margin-top': '-20px'}
    # Create two boxes for data display
    from copy import deepcopy
    
    new_style = deepcopy(subtext_style)
    new_style['color'] = 'coral'
    data_box1 = html.Div([
        html.Div([html.H3('Power Consumption', style=text_style), html.P(f'{pwr} Watt', style=new_style)]),
    ], style=box_style)

    new_style = deepcopy(subtext_style)
    new_style['color'] = 'dodgerblue'
    data_box2 = html.Div([
        html.Div([html.H3('Power Limit', style=text_style), html.P(f'{power_limit} Watt', style=new_style)]),
    ], style=box_style)

    new_style = deepcopy(subtext_style)
    new_style['color'] = 'darkolivegreen'
    data_box3 = html.Div([
        html.Div([html.H3('Throughput', style=text_style), html.P(f'{throughput} Requests/Sec', style=new_style)]),
    ], style=box_style)

    new_style = deepcopy(subtext_style)
    new_style['color'] = 'black'
    data_box4 = html.Div([
        html.Div([html.H3('Number of Instances', style=text_style), html.P(f'{num_ins}', style=new_style)]),
    ], style=box_style)

    new_style = deepcopy(subtext_style)
    new_style['color'] = 'goldenrod'
    data_box5 = html.Div([
        html.Div([html.H3('Temperature', style=text_style), html.P(f'{temp} degC', style=new_style)]),
    ], style=box_style)

    # New boxes for temperature, SM utilization, and memory utilization
    new_style = deepcopy(subtext_style)
    new_style['color'] = 'purple'
    data_box6 = html.Div([
        html.Div([html.H3('SM Utilization', style=text_style), html.P(f'{sm}% Utilized', style=new_style)]),
    ], style=box_style)

    new_style = deepcopy(subtext_style)
    new_style['color'] = 'green'
    data_box7 = html.Div([
        html.Div([html.H3('Memory Utilization', style=text_style), html.P(f'{mem}% Utilized', style=new_style)]),
    ], style=box_style)

    new_style = deepcopy(subtext_style)
    new_style['color'] = 'blue'
    data_box8 = html.Div([
        html.Div([html.H3('Memory Usage', style=text_style), html.P(f'{mem_usage} MB/40960 MB', style=new_style)]),
    ], style=box_style)


    # Return updated set of boxes and plots
    top_row_boxes = html.Div([data_box1, data_box2, data_box3, data_box4], style={'display': 'flex'})
    bottom_row_boxes = html.Div([data_box5, data_box6, data_box7, data_box8], style={'display': 'flex', 'marginTop': '20px'})
    return [html.Div([top_row_boxes, bottom_row_boxes]), fig1, fig2]

    # return [data_box1, data_box2, data_box3, data_box4], fig1, fig2

    # return html.Div([data3, html.Br(), data2, html.Br(), data1, html.Br(), data4]), fig1, fig2  # Use html.Div to format the content with line breaks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Demo")
    parser.add_argument("--ip", type=str, help="Producer machine IP", default="10.99.103.101")
    args = parser.parse_args()

    power_meas, lat_meas = [], []
    temp_meas, sm_meas, mem_meas, mem_usage_meas = [], [], [], []
    power_limit = 250
    num_ins = 0
    history_limit = 60
    time_points, pwr_display, power_limit_display, throughput_display = [], [], [], []

    x1 = threading.Thread(target=get_measurements, daemon=True)
    x2 = threading.Thread(target=get_power_limit, daemon=True)
    x3 = threading.Thread(target=get_throughput, daemon=True)
    x1.start()
    x2.start()
    x3.start()
    app.run_server(debug=False, port=8080)
