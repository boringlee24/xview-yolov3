import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np

# Initialize your Dash app
app = dash.Dash(__name__)

# Sample data for demonstration purposes
time_points = []
data1_values = []
data2_values = []

# Layout of the app
app.layout = html.Div(
    [html.H1('Live Demo Dashboard'),
     html.Div(id='live-data', children='Initial Data', style={'fontSize': '24px'}),  # Increase font size here
     dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
     dcc.Graph(id='live-plot1', style={'width': '80%', 'height': '300px'}),  # Adjust width and height here
     dcc.Graph(id='live-plot2', style={'width': '80%', 'height': '300px'})  # Adjust width and height here
    ]
)

# Update data1 and data2 values and the live plots
@app.callback(
    [Output('live-data', 'children'),
     Output('live-plot1', 'figure'),
     Output('live-plot2', 'figure')],
    Input('interval-component', 'n_intervals')
)
def update_data_and_plots(n):
    global time_points, data1_values, data2_values
    
    # Sample data update logic (replace with your actual data)
    time_points.append(n)
    data1_values.append(np.random.rand())  # Replace with your actual data source
    data2_values.append(np.random.rand())  # Replace with your actual data source
    
    # Ensure that only the last, e.g., 10 data points are displayed
    max_points_to_display = 10
    if len(time_points) > max_points_to_display:
        time_points = time_points[-max_points_to_display:]
        data1_values = data1_values[-max_points_to_display:]
        data2_values = data2_values[-max_points_to_display:]
    
    # Create live plots
    fig1 = px.line(x=time_points, y=data1_values, labels={'x': 'Time', 'y': 'Data1'})
    fig2 = px.line(x=time_points, y=data2_values, labels={'x': 'Time', 'y': 'Data2'})
    
    # Format data for display
    data1 = f"Data1: {data1_values[-1]}"  # Display the latest data point
    data2 = f"Data2: {data2_values[-1]}"  # Display the latest data point
    
    return html.Div([data1, html.Br(), data2]), fig1, fig2

if __name__ == '__main__':
    app.run_server(debug=True)
