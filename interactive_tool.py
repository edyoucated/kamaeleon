# %% 
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc

import warnings
warnings.filterwarnings('ignore')

from dash import html
from dash.dependencies import Input, Output, State
from datetime import date

from src.objects.learning_path import LearningPath
from src.objects.learning_plan import LearningPlan, LearningIndicator

# %% load learning path
learning_path_id = "9ffc6b57-f46d-4ca2-95e2-e1e90313717e" # Data Reporting
language = "en"

learning_path = LearningPath()
learning_path.initialize_from_id(id=learning_path_id, language=language)

learning_plan = LearningPlan(learning_path=learning_path)
learning_indicator = LearningIndicator(learning_plan=learning_plan)

# REMOVE AFTERWARDS
# learning_plan.current_date = "2020-01-01"
# learning_plan.end_date = "2023-01-02"
# learning_plan.start_date = "2022-12-02"


def get_learning_path_materials_options(learning_path: LearningPath) -> dict: 
    opts = []
    for material in learning_path.materials:
        opts.append({
            "label": material.title,
            "value": material.id,
            "disabled": True if material.is_finished or material.is_skipped else False
        })
    return opts

def get_learning_path_materials_values(learning_path: LearningPath) -> dict: 
    vals = []
    for material in learning_path.materials:
        if material.is_skipped or material.is_finished:
            vals.append(material.id)
    return vals

def split_message(msg: str) -> list:
    msg_split = msg.split("\n")
    output_msg = []
    for s in msg_split:
        output_msg.append(s)
        output_msg.append(html.Br())
    return output_msg


#%%
# ============================================== #
# the app itself
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
app.layout = html.Div([
    dcc.Store(id='job-title-db'),
    html.Div([
        dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H3("Learning path:"),
                    ]),
                    html.Div([
                        html.Div(id="learning-path"),
                        dcc.Checklist(
                            id="learning-path-checklist",
                            options=get_learning_path_materials_options(learning_path),
                            value=get_learning_path_materials_values(learning_path),
                            labelStyle = dict(display='block')
                            )
                    ])
                ]),
                dbc.Col(
                    html.Div([
                        html.H3("Settings"),
                        html.Div([
                            dcc.DatePickerSingle(
                                id='start-date-picker',
                                min_date_allowed=date(2000, 1, 1),
                                max_date_allowed=date(2025, 12, 31),
                                date=date(2022, 12, 2)
                            ),
                            dcc.DatePickerSingle(
                                id='end-date-picker',
                                min_date_allowed=date(2000, 1, 1),
                                max_date_allowed=date(2025, 12, 31),
                                date=date(2023, 1, 2)
                            ),
                            html.Button("Set deadline", id="deadline-button", n_clicks=0),
                            html.Div(id="deadline-div")
                        ]),
                        html.H3("Learning indicator"),
                        dcc.DatePickerSingle(
                                id='current-date-picker',
                                min_date_allowed=date(2000, 1, 1), # add current learning plan date here
                                max_date_allowed=date(2025, 12, 31),
                                date=date(2022, 12, 5)
                            ),
                        html.Button("Update", id="update-button", n_clicks=0),
                        html.Div(id="learning-indicator-output")
                    ])  
                )
            ]
        ),
        
    ])
])

# @app.callback(
#     [
#         Output('learning-path-checklist', 'options'),
#         Output('learning-path-checklist', 'value')
#     ],
#     Input('job-title-dropdown', 'value')
# )
# def update_output(value):
#     pass

@app.callback(
    Output("deadline-div", "children"),
    [
        State('start-date-picker', 'date'),
        State('end-date-picker', 'date')
    ],
    Input("deadline-button", "n_clicks")
)
def initialize_learning_plan(start_date, end_date, n_button_clicked):
    if n_button_clicked == 0:
        return ""
    else:
        learning_plan.initialize(start_date=start_date, end_date=end_date)
        return "Deadline set"
    

# @app.callback(
#     [
#         Input('start-date-picker', 'value'),
#         Input('end-date-picker', 'value')
#     ]

# )
# def print_learning_indicator(start_date, end_date):
#     print(start_date, end_date)



@app.callback(
    [
        Output("learning-indicator-output", "children"),
        Output("learning-path-checklist", "options"),
        Output("learning-path-checklist", "value")
    ],
    Input('update-button', 'n_clicks'),
    [
        State('current-date-picker', 'date'),
        State('learning-path-checklist', 'value')
    ]
)
def update_learning_plan_and_indicator(n_button_clicks, current_date, finished_material_ids):
    if n_button_clicks == 0:
        lpc_options = get_learning_path_materials_options(learning_path)
        lpc_values = get_learning_path_materials_values(learning_path)
        return "", lpc_options, lpc_values

    else:
        for material in learning_plan.learning_path.materials:
            if material.id in finished_material_ids and not (material.is_finished or material.is_skipped):
                material.finish()
        learning_plan.print_current_week()
        learning_plan.set_new_date(current_date)
        learning_plan.update()
        learning_plan.print_current_week()

        msg = learning_indicator.display()

        lpc_options = get_learning_path_materials_options(learning_path)
        lpc_values = get_learning_path_materials_values(learning_path)

        return split_message(msg), lpc_options, lpc_values



if __name__ == "__main__":
    app.run_server(debug=True)

# %%
