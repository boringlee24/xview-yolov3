import dash
from dash import html, dcc
from dash.dependencies import Output, Input
import random

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
    data1 = f"Updated Data: {random.random()}"
    data2 = f"Another Row: {random.random()}"
    return html.Div([data1, html.Br(), data2])  # Use html.Div to format the content with line breaks

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
