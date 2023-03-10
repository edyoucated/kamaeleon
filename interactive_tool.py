# %% 
import dash
from dash import dcc
import dash_bootstrap_components as dbc

import warnings
warnings.filterwarnings('ignore')

from dash import html
from dash.dependencies import Input, Output, State
from datetime import date

from src.objects.learning_path import LearningPath
from src.objects.learning_plan import LearningPlan, LearningIndicator

# %% load learning path
# learning_path_id = "9ffc6b57-f46d-4ca2-95e2-e1e90313717e" # Data Reporting
# language = "en"

learning_path_id = "b42c3732-4baf-4e60-957e-beffbb9ea314" # Grundlagen agiles Management
language = "de"

# learning_path_id = "9f545cd2-cc08-4f95-9f0a-e7fd0fbf9909" # Führung in der Praxis
# language = "de"


learning_path = LearningPath()
learning_path.initialize_from_id(id=learning_path_id, language=language)

learning_plan = LearningPlan(learning_path=learning_path)
learning_plan.round_base = 5
learning_plan.round_mode = "best"


learning_indicator = LearningIndicator(learning_plan=learning_plan)


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
    dcc.Store(id='update-store'),
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
                        html.Div([
                            html.H3("Settings"),
                            # html.Button("Reset", id="reset-button", n_clicks=0),
                        ]),
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
                        html.Div(id="learning-indicator-output"),
                        html.Div(id="learning-plan-summary"),
                        html.Div(id="learning-plan-output")
                    ])  
                )
            ]
        ),
        
    ])
])

@app.callback(
    Output('update-store', 'data'),
    Input('update-button', 'n_clicks'),
    State('current-date-picker', 'date')
)
def update_output(n_clicks, date):
    if n_clicks > 0:
        learning_plan.set_new_date(date)

    return "Trigger"

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
    

@app.callback(
    [
        Output("learning-indicator-output", "children"),
        Output("learning-plan-summary", "children"),
        Output("learning-plan-output", "children"),
        Output("learning-path-checklist", "options"),
        Output("learning-path-checklist", "value")
    ],
    [
        Input('learning-path-checklist', 'value'),
        Input('update-store', 'data')
    ]
    
)
def update_learning_plan_and_indicator(finished_material_ids, trigger):
    if learning_plan.start_date is None:
        lpc_options = get_learning_path_materials_options(learning_path)
        lpc_values = get_learning_path_materials_values(learning_path)
        return "", "", "", lpc_options, lpc_values

    else:
        for material in learning_plan.learning_path.materials:
            if material.id in finished_material_ids and not (material.is_finished or material.is_skipped):
                learning_plan.make_progress_by_material_id(material_id=material.id)

        msg = learning_indicator.display()
        lpc_options = get_learning_path_materials_options(learning_path)
        lpc_values = get_learning_path_materials_values(learning_path)

        return split_message(msg),  split_message(learning_plan.summary_msg()), split_message(learning_plan.current_week_workload.__str__()), lpc_options, lpc_values



if __name__ == "__main__":
    app.run(debug=True)

# %%
