import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
from dash.exceptions import PreventUpdate

app = Dash()

plugs = [str(item) for item in Path("./measurements/").iterdir() if item.is_dir()]

update_lock = threading.Lock()

app.layout = [
    html.Div(
        [
            html.H4(children='Power Consumption Data'),
        ]
    ),
    html.Hr(),
    html.Div(
        [
            html.H4(children='Select a plug'),
            dcc.Dropdown(options=plugs, value=plugs[0], id='plug_dropdown'),
        ]
    ),
    html.Div(
        [
            html.H4(children='Select an experiment'),
            dcc.Dropdown(id='experiment_dropdown'),
        ]
    ),
    html.Div(
        [
            html.H4(children='Select a file'),
            dcc.Dropdown(id='file_dropdown'),
        ]
    ),
    html.Hr(),
    html.Div(
        [
            html.H4(children='Power Consumption'),
            dcc.Graph(figure=px.line(), id='plot_power'),
            dcc.Interval(id='graph_update_interval', interval=1000, n_intervals=0, disabled=True),

        ]
    ),
    html.Div([
        html.Label('Update Interval (ms)', htmlFor='graph_update_interval_input'),
        dcc.Input(id='graph_update_interval_input', type='number', value=1000, min=1000, max=10000, step=1000),
        dcc.Checklist(id='graph_update_interval_toggle', options=[{'label': 'Disable Auto Update', 'value': 'ON'}],
                      value=['ON']),
    ]),
]


@callback(
    Output('graph_update_interval', 'disabled'),
    Input('graph_update_interval_toggle', 'value')
)
def update_interval_disabled(checkbox_value):
    if 'ON' in checkbox_value:
        return True
    return False


@callback(
    Output(component_id='graph_update_interval', component_property='interval'),
    Input(component_id='graph_update_interval_input', component_property='value')
)
def update_interval(value):
    return value


@callback(
    Output(component_id='experiment_dropdown', component_property='options'),
    Output(component_id='experiment_dropdown', component_property='value'),
    Input(component_id='plug_dropdown', component_property='value')
)
def update_experiment_dropdown(plug):
    if plug is None:
        return [], None
    options = [{"label": str(item), "value": str(item)} for item in Path(plug).iterdir() if item.is_dir()]
    options.insert(0, {"label": "All", "value": f"!{plug}"})
    if len(options) == 0:
        return [], None
    value = options[0]['value']
    return options, value


@callback(
    Output(component_id='file_dropdown', component_property='options'),
    Output(component_id='file_dropdown', component_property='value'),
    Input(component_id='experiment_dropdown', component_property='value')
)
def update_file_dropdown(experiment):
    if experiment is None:
        return [], None
    if experiment[0] == '!':
        experiment = experiment[1:]
    options = [{"label": str(item), "value": str(item)} for item in Path(experiment).iterdir() if item.is_file()]
    options.insert(0, {"label": "All", "value": f"!{experiment}"})
    if len(options) == 0:
        return {}
    value = options[0]['value']
    return options, value


@callback(
    Output(component_id='plot_power', component_property='figure'),
    Input(component_id='file_dropdown', component_property='value'),
    Input(component_id='graph_update_interval', component_property='n_intervals')
)
def update_graph(file, n_intervals):
    if not update_lock.acquire(blocking=False):
        raise PreventUpdate
    try:
        if file is None:
            return px.line()
        elif file[0] == '!':

            files = list(Path(file[1:]).iterdir())
            if not any([item.is_file() for item in files]):
                return px.line()

            def read_file(item):
                return pd.read_csv(item)

            with ThreadPoolExecutor() as executor:
                data = pd.concat(list(executor.map(read_file, [item for item in files if item.is_file()])))
            return px.line(data, x='timestamp', y='draw', title='Power Consumption')

        else:
            if not Path(file).is_file():
                return px.line()
            data = pd.read_csv(file)
            return px.line(data, x='timestamp', y='draw', title='Power Consumption')
    finally:
        update_lock.release()


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
