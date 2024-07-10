import argparse

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input, State, dash_table

from time import time

app = Dash()

plug_options = [{"label": str(item).split("\\")[-1], "value": str(item)} for item in Path("./measurements/").iterdir()
                if
                item.is_dir()]

with open("monitor_settings.json", "r") as monitor_settings_file:
    monitor_settings = json.load(monitor_settings_file)

report_button_selected_string_default = "Create report for selected experiments"
report_button_all_string_default = "Create report for all experiments"
cost_of_energy_string_default = "Select an experiment or file to calculate cost of energy."
carbon_footprint_string_default = "Select an experiment or file to calculate carbon footprint."

gco2e_per_kilometer_car = 108.1

app.layout = [
    html.Header(
        style={'background-color': '#333',
               'color': 'white',
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
                           'font-size': '32',
                           'font-weight': '300'},
                    children='PARSR: Power Consumption Monitor'),
        ]
    ),
    html.Div(
        style={
            'padding': '45px 20px',
            'background-color': '#f4f4f4',
            'min-height': '100vh',
            'text-align': 'center'},
        children=[
            html.Div(
                style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center',
                       'alignItems': 'center'},
                children=[
                    html.Div(
                        style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'stretch', 'width': '100%'},
                        children=[
                            html.Div(
                                style={
                                    'flex': '1', 'margin': '10px', 'padding': '20px', 'border': '1px solid #000',
                                    'fontSize': '24px', 'textAlign': 'center'
                                },
                                children=[
                                    html.Label(children='Select a plug', htmlFor='plug_dropdown',
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Dropdown(options=plug_options, value=plug_options[0]["value"],
                                                 id='plug_dropdown'),
                                    html.Hr(),
                                    html.Label(children='Select an experiment', htmlFor='experiment_dropdown',
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Dropdown(id='experiment_dropdown', multi=True),
                                    html.Hr(),
                                    html.Label(children='Select a file', htmlFor='file_dropdown',
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Dropdown(id='file_dropdown', multi=True),
                                ]
                            ),
                            html.Div(
                                style={
                                    'flex': '1', 'margin': '10px', 'padding': '20px', 'border': '1px solid #000',
                                    'fontSize': '24px', 'textAlign': 'center'
                                },
                                children=[
                                    html.Label(f'Cost of energy per kWh',
                                               htmlFor="cost_per_kwh",
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Input(id='cost_per_kwh', type='text', value=monitor_settings["cost_per_kwh"],
                                              style={'width': '40%', 'fontSize': '24px'},
                                              debounce=True),
                                    dcc.Input(id='currency', type='text', value=monitor_settings["currency"],
                                              style={'width': '10%', 'fontSize': '24px'},
                                              debounce=True),
                                    html.Hr(),
                                    html.Label('Carbon footprint per kWh in gCO2e', htmlFor="carbon_footprint",
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Input(id='carbon_footprint', type='text',
                                              value=monitor_settings["gco2e_per_kwh"],
                                              style={'width': '50%', 'fontSize': '24px'},
                                              debounce=True),
                                    html.Hr(),
                                    html.Button(children=report_button_selected_string_default,
                                                id='report_selected_button', n_clicks=0,
                                                style={'background-color': '#4CAF50',
                                                       'color': 'white',
                                                       'border': 'none',
                                                       'padding': '3px 3px',
                                                       'text-align': 'center',
                                                       'text-decoration': 'none',
                                                       'display': 'inline-block',
                                                       'font-size': '24px',
                                                       'margin': '2px 2px',
                                                       'cursor': 'pointer',
                                                       'border-radius': '12px',
                                                       'width': '100%'
                                                       }),
                                    html.Button(children=report_button_all_string_default,
                                                id='report_all_button', n_clicks=0,
                                                style={'background-color': '#4CAF50',
                                                       'color': 'white',
                                                       'border': 'none',
                                                       'padding': '3px 3px',
                                                       'text-align': 'center',
                                                       'text-decoration': 'none',
                                                       'display': 'inline-block',
                                                       'font-size': '24px',
                                                       'margin': '2px 2px',
                                                       'cursor': 'pointer',
                                                       'border-radius': '12px',
                                                       'width': '100%'
                                                       }),
                                ]
                            ),
                            html.Div(
                                style={
                                    'flex': '1', 'margin': '10px', 'padding': '20px', 'border': '1px solid #000',
                                    'fontSize': '24px', 'textAlign': 'center'
                                },
                                children=[
                                    html.Label('Graph Update Interval (ms)', htmlFor='graph_update_interval_input',
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Input(id='graph_update_interval_input', type='number', value=1000, min=1000,
                                              max=10000, step=1000, style={'width': '50%', 'fontSize': '24px'}),
                                    dcc.Checklist(id='graph_update_interval_toggle',
                                                  options=[{'label': 'Enable Graph Auto Update', 'value': 'ON'}],
                                                  labelStyle={'display': 'block', 'font-size': '24px',
                                                              'margin-bottom': '10px'},
                                                  inputStyle={'width': '24px', 'height': '24px',
                                                              'margin-right': '10px'}),
                                    html.Hr(),
                                    html.Label('Graph Smoothness Rolling Window', htmlFor='smoothness_input',
                                               style={'display': 'block', 'marginBottom': '10px'}),
                                    dcc.Input(id='smoothness_input', type='number', value=100, min=1,
                                              max=100000, step=1, style={'width': '50%', 'fontSize': '24px'},
                                              debounce=True),
                                    dcc.Checklist(id='graph_rolling_window_toggle',
                                                  options=[{'label': 'Enable Graph Rolling Window', 'value': 'ON'}],
                                                  labelStyle={'display': 'block', 'font-size': '24px',
                                                              'margin-bottom': '10px'},
                                                  inputStyle={'width': '24px', 'height': '24px',
                                                              'margin-right': '10px'}),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            html.Div(
                style={'width': '100%'},
                children=[
                    html.Div(
                        style={
                            'flex': '1', 'margin': '10px', 'padding': '20px', 'border': '1px solid #000',
                            'fontSize': '24px', 'textAlign': 'center'
                        },
                        children=[
                            dash_table.DataTable(id='experiment_data',
                                                 style_table={
                                                     'width': '100%',
                                                     'minWidth': '100%',
                                                     'overflowX': 'auto'
                                                 },
                                                 style_cell={'fontSize': 14})
                        ]
                    ),
                ]
            ),
            html.Div(
                children=[
                    html.Div(
                        style={
                            'flex': '1', 'margin': '10px', 'padding': '20px', 'border': '1px solid #000',
                            'fontSize': '24px', 'textAlign': 'center'
                        },
                        children=[
                            dcc.Graph(id='plot_current_draw'),
                            dcc.Graph(id='plot_total_draw'),
                            dcc.Interval(id='graph_update_interval', interval=1000, n_intervals=0, disabled=True),
                        ]
                    )
                ]
            )
        ]
    ),
]


@app.callback(
    Output(component_id='report_selected_button', component_property='children', allow_duplicate=True),
    Input(component_id='report_selected_button', component_property='n_clicks'),
    State(component_id='file_dropdown', component_property='value'),
    State(component_id='cost_per_kwh', component_property='value'),
    State(component_id='currency', component_property='value'),
    State(component_id='carbon_footprint', component_property='value'),
    State(component_id='smoothness_input', component_property='value'),
    Input(component_id='graph_rolling_window_toggle', component_property='value'),
    prevent_initial_call=True
)
def export_selected_experiments(n_clicks, files, cost_per_kwh, currency, carbon_footprint, smoothness,
                                smoothness_toggle):
    if n_clicks > 0:
        try:
            fig_cd, fig_td, information_df = make_graph(files, cost_per_kwh, currency, carbon_footprint, smoothness,
                                                        smoothness_toggle, False)
        except ValueError:
            return f"Invalid selection"

        timestamp = int(time())

        report_path = Path(f"./report/{timestamp}")
        report_path.mkdir(exist_ok=False)

        export_cd = Path(f"{report_path}/figure_current_draw.svg")
        export_td = Path(f"{report_path}/figure_total_draw.svg")
        fig_cd.write_image(export_cd, engine="kaleido")
        fig_td.write_image(export_td, engine="kaleido")

        information_table = information_df.to_html()

        html_string = '''
        <html>
            <head>
                <style>
                    body{ margin: 50; background:whitesmoke; }
                    table { width: 1800; border-collapse: collapse; margin-top: 50; }
                    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                    tr:hover { background-color: #f5f5f5; }
                    th { background-color: #f2f2f2; color: black; }
                </style>
            </head>
            <body>
                <h1>Power Consumption Monitor Report</h1>
                <iframe width="1800" height="600" frameborder="0" seamless="seamless" scrolling="no" \
                src="./figure_current_draw.svg"></iframe>
                <iframe width="1800" height="600" frameborder="0" seamless="seamless" scrolling="no" \
                src="./figure_total_draw.svg"></iframe>
                ''' + information_table + '''
            </body>
        </html>
        '''

        with open(f"./report/{timestamp}/report.html", "w") as file:
            file.write(html_string)

        return f"Figure exported to report folder"
    return report_button_selected_string_default


def read_file(item):
    data_file = pd.read_csv(item)
    if data_file.empty:
        return pd.DataFrame()
    else:
        return data_file


@app.callback(
    Output(component_id='report_all_button', component_property='children', allow_duplicate=True),
    Input(component_id='report_all_button', component_property='n_clicks'),
    State(component_id='cost_per_kwh', component_property='value'),
    State(component_id='currency', component_property='value'),
    State(component_id='carbon_footprint', component_property='value'),
    State(component_id='smoothness_input', component_property='value'),
    prevent_initial_call=True
)
def export_all_experiments(n_clicks, cost_per_kwh, currency, carbon_footprint, smoothness):
    if n_clicks > 0:
        full_data = {}
        for plug_folder in Path("./measurements").iterdir():
            for experiment_folder in Path(plug_folder).iterdir():
                with ThreadPoolExecutor() as executor:
                    full_data[experiment_folder] = pd.concat(
                        list(executor.map(read_file, [item for item in
                                                      Path(experiment_folder).iterdir() if
                                                      item.is_file()])))

        if not full_data:
            return "No data available"

        scatter_data = make_scatters(full_data, smoothness, False)

        full_information = []
        all_figures = []

        for scatters in scatter_data["scatters"]:
            fig_cd = go.Figure(data=[scatters["cd"], scatters["cds"]], layout=scatter_data["scatters_layout"]["cd"])
            fig_td = go.Figure(data=[scatters["td"], scatters["tds"]], layout=scatter_data["scatters_layout"]["cd"])

            fig_cd.update_layout(legend=scatter_data["scatters_layout"]["legend"])
            fig_td.update_layout(legend=scatter_data["scatters_layout"]["legend"])

            all_figures.append({"fig_cd": fig_cd, "fig_td": fig_td, "experiment": scatters["experiment"]})

        timestamp = int(time())

        report_folder = Path(f"./report/{timestamp}")
        report_folder.mkdir(exist_ok=False)

        figure_html = ""
        for ind, figure in enumerate(all_figures):
            export_cd = Path(f"{report_folder}/{ind}_figure_current_draw.svg")
            export_td = Path(f"{report_folder}/{ind}_figure_total_draw.svg")
            figure["fig_cd"].write_image(export_cd, engine="kaleido")
            figure["fig_td"].write_image(export_td, engine="kaleido")

            figure_html += f'''
                <h1>{figure["experiment"]}</h1>
                <iframe width="1800" height="600" frameborder="0" seamless="seamless" scrolling="no" \
                src="./''' + str(ind) + '''_figure_current_draw.svg"></iframe>
                <iframe width="1800" height="600" frameborder="0" seamless="seamless" scrolling="no" \
                src="./''' + str(ind) + '''_figure_total_draw.svg"></iframe>
            '''

        information_df = calculate_information(scatter_data["total_power"], scatter_data["power_by_experiment"],
                                               cost_per_kwh, currency, carbon_footprint)

        information_table = information_df.to_html()

        html_string = '''
                <html>
                    <head>
                        <style>
                            body{ margin: 50; background:whitesmoke; }
                            table { width: 1800; border-collapse: collapse; margin-top: 50; }
                            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                            tr:hover { background-color: #f5f5f5; }
                            th { background-color: #f2f2f2; color: black; }
                        </style>
                    </head>
                    <body>
                        <h1>Power Consumption Monitor Report</h1>
                        ''' + figure_html + information_table + '''
                        <h1>Our experiments consumed a total of ''' + str(scatter_data["total_power"]) + ''' kWh</h1>
                    </body>
                </html>
                '''

        with open(f"{report_folder}/{timestamp}_report.html", "w") as file:
            file.write(html_string)

        return f"Figure exported to report folder"
    else:
        return report_button_all_string_default


@callback(
    Output(component_id='graph_update_interval', component_property='disabled'),
    Input(component_id='graph_update_interval_toggle', component_property='value')
)
def update_interval_disabled(checkbox_value):
    if checkbox_value is None or len(checkbox_value) == 0:
        return True
    else:
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
    if len(plug) == 0:
        return [], None
    options = [{"label": str(item).split("\\")[-1], "value": str(item)} for item in Path(plug).iterdir() if
               item.is_dir()]
    if len(options) == 0:
        return [], None
    value = options[0]['value']
    return options, value


@callback(
    Output(component_id='file_dropdown', component_property='options'),
    Output(component_id='file_dropdown', component_property='value'),
    Output(component_id='report_selected_button', component_property='children'),
    Output(component_id='report_all_button', component_property='children'),
    Input(component_id='experiment_dropdown', component_property='value')
)
def update_file_dropdown(experiment):
    if experiment is None or len(experiment) == 0:
        return [], None, report_button_selected_string_default, report_button_all_string_default
    if not type(experiment) == list:
        experiment = [experiment]

    options = []
    all_value = ""
    for ex in experiment:
        if ex[0] == '!':
            ex = ex[1:]
        options += [{"label": str(item).split("\\")[-1], "value": str(item)} for item in Path(ex).iterdir() if
                    item.is_file()]
        all_value += f"!{ex}"

    options.insert(0, {"label": "All", "value": all_value})
    if len(options) == 0:
        return [], None, report_button_selected_string_default, report_button_all_string_default
    value = options[0]['value']
    return options, value, report_button_selected_string_default, report_button_all_string_default


def get_experiment_files(files):
    if files is None or len(files) == 0:
        raise ValueError
    if not type(files) == list:
        files = [files]

    files_to_read = {}
    for file in files:

        if file[0] == '!':
            folders = file.split("!")
            folders = list(filter(None, folders))

            for folder in folders:
                experiment = folder.split("\\")[-1]
                if not experiment in files_to_read:
                    files_to_read[experiment] = []

                files_to_read[experiment] += list(Path(folder).iterdir())
        else:
            experiment = file.split("\\")[-2]
            if not experiment in files_to_read:
                files_to_read[experiment] = []

            files_to_read[experiment].append(Path(file))

    if not files_to_read:
        raise ValueError

    full_data = {}
    for experiment in files_to_read.keys():
        with ThreadPoolExecutor() as executor:
            full_data[experiment] = pd.concat(
                list(executor.map(read_file, [item for item in files_to_read[experiment] if item.is_file()])))

    return full_data


def make_scatters(full_data, smoothness, autosize=False):
    scatters = []

    power_by_experiment = {}
    total_power = 0

    for experiment, readings in full_data.items():
        readings.sort_values(by="timestamp", inplace=True)
        readings["timestamp"] = readings["timestamp"] - readings["timestamp"].iloc[0]

        readings["current_draw_smooth"] = readings["current_draw"].rolling(window=smoothness).mean()
        readings["total_draw"] = readings["total_draw"] - readings["total_draw"].min()

        power_by_experiment[experiment] = readings["total_draw"].max()
        total_power += readings["total_draw"].max()

        readings["total_draw_smooth"] = readings["total_draw"].rolling(window=smoothness).mean()

        scatter_temp = {
            "experiment": experiment,
            "cd": (go.Scatter(x=readings["timestamp"], y=readings["current_draw"],
                              name=f'Raw Sensor Reading ({experiment})')),
            "cds": (go.Scatter(x=readings["timestamp"], y=readings["current_draw_smooth"],
                               name=f'Smoothed Sensor Reading ({experiment})')),
            "td": (go.Scatter(x=readings["timestamp"], y=readings["total_draw"],
                              name=f'Raw Sensor Reading ({experiment})')),
            "tds": (go.Scatter(x=readings["timestamp"], y=readings["total_draw_smooth"],
                               name=f'Smoothed Sensor Reading ({experiment})'))}

        scatters.append(scatter_temp)

    scatters_layout = {}

    if not autosize:
        scatters_layout["cd"] = go.Layout(title='Draw (W) Over Time (s)',
                                          xaxis={"title": 'Time (s)'},
                                          yaxis={"title": 'Draw (W)'},
                                          autosize=False,
                                          width=1800,
                                          height=600)
        scatters_layout["td"] = go.Layout(title='Consumption (kWh) oder Time (s)',
                                          xaxis={"title": 'Time (s)'},
                                          yaxis={"title": 'Consumption (kWH)', },
                                          autosize=False,
                                          width=1800,
                                          height=600)
    else:
        scatters_layout["cd"] = go.Layout(title='Draw (W) Over Time (s)',
                                          xaxis={"title": 'Time (s)'},
                                          yaxis={"title": 'Draw (W)'})

        scatters_layout["td"] = go.Layout(title='Consumption (kWh) oder Time (s)',
                                          xaxis={"title": 'Time (s)'},
                                          yaxis={"title": 'Consumption (kWH)', })

    scatters_layout["legend"] = {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1}

    scatter_data = {"scatters": scatters, "scatters_layout": scatters_layout, "total_power": total_power,
                    "power_by_experiment": power_by_experiment}

    return scatter_data


def calculate_cost(power, cost_per_kwh, currency, carbon_footprint):
    cost_of_experiment = power * float(cost_per_kwh)
    emission_of_experiment = power * float(carbon_footprint)
    equivalent_by_car = emission_of_experiment / gco2e_per_kilometer_car

    information_dict = {
        "Total Power (kWh)": round(power, 2),
        f"Cost of Experiment ({currency})": round(cost_of_experiment, 2),
        "Emission of Experiment (gCO2e)": round(emission_of_experiment, 2),
        "Equivalent Distance by Car (km)": round(equivalent_by_car, 2)
    }

    return information_dict


def calculate_information(total_power, power_by_experiment, cost_per_kwh, currency, carbon_footprint):
    information_dict = {}

    for experiment, power in power_by_experiment.items():
        information_dict[experiment] = calculate_cost(power, cost_per_kwh, currency, carbon_footprint)

    information_dict["Combined"] = calculate_cost(total_power, cost_per_kwh, currency, carbon_footprint)

    information_df = pd.DataFrame.from_dict(information_dict, orient="index")
    information_df.reset_index(inplace=True)
    information_df.rename(columns={"index": "Experiment"}, inplace=True)

    return information_df


def make_graph(files, cost_per_kwh, currency, carbon_footprint, smoothness, smoothness_toggle, autosize):
    full_data = get_experiment_files(files)

    scatter_data = make_scatters(full_data, smoothness, autosize)

    all_cd_scatters = [scatters["cd"] for scatters in scatter_data["scatters"]]
    all_cds_scatters = [scatters["cds"] for scatters in scatter_data["scatters"]]

    all_td_scatters = [scatters["td"] for scatters in scatter_data["scatters"]]
    all_tds_scatters = [scatters["tds"] for scatters in scatter_data["scatters"]]

    if smoothness_toggle is None or len(smoothness_toggle) == 0:
        fig_cd = go.Figure(data=all_cd_scatters, layout=scatter_data["scatters_layout"]["cd"])
        fig_td = go.Figure(data=all_td_scatters, layout=scatter_data["scatters_layout"]["td"])
    else:
        fig_cd = go.Figure(data=all_cd_scatters + all_cds_scatters, layout=scatter_data["scatters_layout"]["cd"])
        fig_td = go.Figure(data=all_td_scatters + all_tds_scatters, layout=scatter_data["scatters_layout"]["td"])

    fig_cd.update_layout(legend=scatter_data["scatters_layout"]["legend"])
    fig_td.update_layout(legend=scatter_data["scatters_layout"]["legend"])

    information_df = calculate_information(scatter_data["total_power"], scatter_data["power_by_experiment"],
                                           cost_per_kwh, currency, carbon_footprint)

    return fig_cd, fig_td, information_df


@callback(
    Output(component_id='plot_current_draw', component_property='figure'),
    Output(component_id='plot_total_draw', component_property='figure'),
    Output(component_id='experiment_data', component_property='data'),
    Output(component_id='experiment_data', component_property='columns'),
    Input(component_id='file_dropdown', component_property='value'),
    Input(component_id='graph_update_interval', component_property='n_intervals'),
    Input(component_id='cost_per_kwh', component_property='value'),
    Input(component_id='currency', component_property='value'),
    Input(component_id='carbon_footprint', component_property='value'),
    Input(component_id='smoothness_input', component_property='value'),
    Input(component_id='graph_rolling_window_toggle', component_property='value')
)
def update_graph(files, n_intervals, cost_per_kwh, currency, carbon_footprint, smoothness, smoothness_toggle):
    invalid_experiment = {}, {}, [], []
    try:
        fig_cd, fig_td, information_df = make_graph(files, cost_per_kwh, currency, carbon_footprint, smoothness,
                                                    smoothness_toggle, True)
    except ValueError:
        return invalid_experiment

    return fig_cd, fig_td, information_df.to_dict('records'), [{"name": i, "id": i} for i in information_df.columns]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run monitoring interface.')
    parser.add_argument('--ip', type=str, required=False, default="127.0.0.1")
    parser.add_argument('--port', type=int, required=False, default=5000)
    args = parser.parse_args()

    app.run(debug=True, host=args.ip, port=args.port)
