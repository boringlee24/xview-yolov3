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
data3_values = []
data4_values = []

# Layout of the app
app.layout = html.Div(
    [html.H1('Live Demo Dashboard'),
     html.Div([
         html.Div([
             html.Span(id='data1', style={'fontSize': '18px', 'color': 'red'}),
             html.Span(id='data2', style={'fontSize': '18px', 'color': 'green'})
         ], style={'display': 'inline-block'}),
         html.Br(),  # Add a line break
         html.Div([
             html.Span(id='data3', style={'fontSize': '18px', 'color': 'blue'}),
             html.Span(id='data4', style={'fontSize': '18px', 'color': 'purple'})
         ], style={'display': 'inline-block'})
     ]),
     dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
    ]
)

# Update data values and the live plots
@app.callback(
    [Output('data1', 'children'),
     Output('data2', 'children'),
     Output('data3', 'children'),
     Output('data4', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_data(n):
    global time_points, data1_values, data2_values, data3_values, data4_values
    
    # Sample data update logic (replace with your actual data)
    time_points.append(n)
    data1_values.append(np.random.rand())  # Replace with your actual data source
    data2_values.append(np.random.rand())  # Replace with your actual data source
    data3_values.append(np.random.rand())  # Replace with your actual data source
    data4_values.append(np.random.rand())  # Replace with your actual data source
    
    # Ensure that only the last, e.g., 10 data points are displayed
    max_points_to_display = 10
    if len(time_points) > max_points_to_display:
        time_points = time_points[-max_points_to_display:]
        data1_values = data1_values[-max_points_to_display:]
        data2_values = data2_values[-max_points_to_display:]
        data3_values = data3_values[-max_points_to_display:]
        data4_values = data4_values[-max_points_to_display:]
    
    # Format data for display with custom text color
    data1 = f"Data1: {data1_values[-1]}"
    data2 = f"Data2: {data2_values[-1]}"
    data3 = f"Data3: {data3_values[-1]}"
    data4 = f"Data4: {data4_values[-1]}"
        
    return data1, data2, data3, data4

if __name__ == '__main__':
    app.run_server(debug=True)
