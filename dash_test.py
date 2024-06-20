import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate

app = Dash()

plugs = [str(item) for item in Path("./measurements/").iterdir() if item.is_dir()]

with open("monitor_settings.json", "r") as file:
    monitor_settings = json.load(file)

update_lock = threading.Lock()

app.layout = [
    html.Header(
        style={'background-color': '#333',
               'color': 'white',
               'padding': '20px 0',
               'text-align': 'center',
               'position': 'fixed',
               'width': '100%',
               'top': '0',
               'left': '0',
               'z-index': '1000',
               'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'},
        children=
        [
            html.H1(style={'margin': '0',
                           'font-size': '2.5em',
                           'font-weight': '300'},
                    children='Power Consumption Monitor'),
        ]
    ),
    html.Div(
        style={
            'padding': '100px 20px',
            'background-color': '#f4f4f4',
            'min-height': '100vh',
            'text-align': 'center'},
        children=[
            html.Div(
                style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center',
                       'alignItems': 'center'},
                children=[
                    html.Div(
                        style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'width': '100%'},
                        children=[
                            html.Div(
                                style={
                                    'flex': '1', 'margin': '10px', 'padding': '20px', 'border': '2px solid #000',
                                    'fontSize': '24px', 'textAlign': 'center'
                                },
                                children=[
                                    html.Label(children='Select a plug', htmlFor='plug_dropdown',
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Dropdown(options=plugs, value=plugs[0], id='plug_dropdown'),
                                ]
                            ),
                            html.Div(
                                style={
                                    'flex': '1', 'margin': '10px', 'padding': '20px', 'border': '2px solid #000',
                                    'fontSize': '24px', 'textAlign': 'center'
                                },
                                children=[
                                    html.Label(children='Select an experiment', htmlFor='experiment_dropdown',
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Dropdown(id='experiment_dropdown'),
                                ]
                            ),
                            html.Div(
                                style={
                                    'flex': '1', 'margin': '10px', 'padding': '20px', 'border': '2px solid #000',
                                    'fontSize': '24px', 'textAlign': 'center'
                                },
                                children=[
                                    html.Label(children='Select a file', htmlFor='file_dropdown',
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Dropdown(id='file_dropdown'),
                                ]
                            ),
                        ]
                    ),

                ]
            ),
            html.Hr(),
            html.Div(
                style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center',
                       'alignItems': 'center'},
                children=[
                    html.Div(
                        style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'width': '100%'},
                        children=[
                            html.Div(
                                style={
                                    'flex': '1', 'margin': '10px', 'padding': '20px', 'border': '2px solid #000',
                                    'fontSize': '24px', 'textAlign': 'center'
                                },
                                children=[
                                    html.Label('Cost of energy per kWh', htmlFor="cost_per_kwh",
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Input(id='cost_per_kwh', type='text', value=monitor_settings["cost_per_kwh"],
                                              style={'width': '50%', 'fontSize': '24px'}),
                                    html.Hr(),
                                    html.Div('Cost of energy for the selected experiment.', id='cost_of_experiment')
                                ]
                            ),
                            html.Div(
                                style={
                                    'flex': '1', 'margin': '10px', 'padding': '20px', 'border': '2px solid #000',
                                    'fontSize': '24px', 'textAlign': 'center'
                                },
                                children=[
                                    html.Label('Carbon footprint per kWh', htmlFor="carbon_footprint",
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Input(id='carbon_footprint', type='text',
                                              value=monitor_settings["gco2e_per_kwh"],
                                              style={'width': '50%', 'fontSize': '24px'}),
                                    html.Hr(),
                                    html.Div('Emitted gCO2e for the selected experiment.', id='emission_of_experiment')
                                ]
                            )
                        ]
                    )
                ]
            ),
            html.Hr(),
            html.Div(
                [
                    dcc.Graph(id='plot_current_draw'),
                    dcc.Graph(id='plot_total_draw'),
                    dcc.Interval(id='graph_update_interval', interval=1000, n_intervals=0, disabled=True),

                ]
            ),
            html.Div(
                style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center',
                       'alignItems': 'center'},
                children=[
                    html.Div(
                        style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'width': '100%'},
                        children=[
                            html.Div(
                                style={
                                    'flex': '1', 'margin': '10px', 'padding': '20px', 'border': '2px solid #000',
                                    'fontSize': '24px', 'textAlign': 'center'
                                },
                                children=[
                                    html.Label('Update Interval (ms)', htmlFor='graph_update_interval_input',
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Input(id='graph_update_interval_input', type='number', value=1000, min=1000,
                                              max=10000, step=1000, style={'width': '33%', 'fontSize': '24px'}),
                                    html.Hr(),
                                    dcc.Checklist(id='graph_update_interval_toggle',
                                                  options=[{'label': 'Enable Auto Update', 'value': 'ON'}],
                                                  value=['Off'],
                                                  labelStyle={'display': 'block', 'font-size': '24px',
                                                              'margin-bottom': '10px'},
                                                  inputStyle={'width': '24px', 'height': '24px',
                                                              'margin-right': '10px'}),
                                ]
                            )
                        ]
                    )
                ]
            ),
        ]
    ),
]


@callback(
    Output('graph_update_interval', 'disabled'),
    Input('graph_update_interval_toggle', 'value')
)
def update_interval_disabled(checkbox_value):
    if 'ON' in checkbox_value:
        return False
    return True


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
    Output(component_id='plot_current_draw', component_property='figure'),
    Output(component_id='plot_total_draw', component_property='figure'),
    Output(component_id='cost_of_experiment', component_property='children'),
    Output(component_id='emission_of_experiment', component_property='children'),
    Input(component_id='file_dropdown', component_property='value'),
    Input(component_id='graph_update_interval', component_property='n_intervals'),
    Input(component_id='cost_per_kwh', component_property='value'),
    Input(component_id='carbon_footprint', component_property='value')
)
def update_graph(file, n_intervals, cost_per_kwh, carbon_footprint):
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
                data_file = pd.read_csv(item)
                if data_file.empty:
                    return pd.DataFrame()
                else:
                    return data_file

            with ThreadPoolExecutor() as executor:
                data = pd.concat(list(executor.map(read_file, [item for item in files if item.is_file()])))

            data["current_draw_smooth"] = data["current_draw"].rolling(window=100).mean()

            fig_cd = go.Figure(data=[go.Scatter(x=data["timestamp"], y=data["current_draw"], name='draw'),
                                     go.Scatter(x=data["timestamp"], y=data["current_draw_smooth"],
                                                name='draw_smooth')],
                               layout=go.Layout(title='Power Consumption', xaxis={"title": 'timestamp'},
                                                yaxis={"title": 'draw'}))

            fig_td = go.Figure(data=[go.Scatter(x=data["timestamp"], y=data["total_draw"], name='total')],
                               layout=go.Layout(title='Total Power Consumption', xaxis={"title": 'timestamp'},
                                                yaxis={"title": 'total'}))

            total_power = data["total_draw"].iloc[-1] - data["total_draw"].iloc[0]
            cost_of_experiment = total_power * float(cost_per_kwh)
            emission_of_experiment = total_power * float(carbon_footprint)

            gco2e_per_kilometer_car = 108.1
            cost_of_experiment_string = f"Cost of experiment: {cost_of_experiment:.2f} €"
            emission_of_experiment_string = (f"Emitted CO2: {emission_of_experiment:.2f} gCO2e"
                                             f" - equivalent to {emission_of_experiment / gco2e_per_kilometer_car:.2f}"
                                             f" km by car")

            return fig_cd, fig_td, cost_of_experiment_string, emission_of_experiment_string



        else:
            if not Path(file).is_file():
                return px.line()
            data = pd.read_csv(file)
            return px.line(data, x='timestamp', y='draw', title='Power Consumption')
    finally:
        update_lock.release()


if __name__ == '__main__':
    app.run(debug=True, host="192.168.178.44", port=5000)
