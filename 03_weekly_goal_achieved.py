# %% Wie oft hat eine Person ein wöchentliches Ziel (nicht) erreicht?

import pandas as pd
import numpy as np
import json


periodic_workload = pd.read_csv("data/periodic_workload.csv")

# %%
final_workload_per_week = periodic_workload.sort_values(
    ["goal_id", "period_identifier", "revision"], 
    ascending=[True, True, True]
).groupby(["goal_id", "period_identifier"]).last().reset_index()


#%% transform minutes properly
final_workload_per_week["planned_learning_duration_minutes"] = final_workload_per_week["planned"].map(lambda x: json.loads(x)["learningDurationMinutes"])
final_workload_per_week["actual_learning_duration_minutes"] = final_workload_per_week["actual"].map(lambda x: json.loads(x)["learningDurationMinutes"])

final_workload_per_week["workload_finished"] = final_workload_per_week["actual_learning_duration_minutes"] >= final_workload_per_week["planned_learning_duration_minutes"]


#%% filter columns 
final_workload_per_week = final_workload_per_week[[
    "goal_id", 
    "periodic_workload_id",
    "period_identifier",
    "period_starts_on",
    "period_ends_on",
    "computed_as",
    "planned_learning_duration_minutes",
    "actual_learning_duration_minutes",
    "workload_finished",
    "related_entity_id", 
    "user_id"
]].rename(columns={"related_entity_id": "learning_path_id"})


#%% Example:
final_workload_per_week[final_workload_per_week["goal_id"] == "053f073b-87cd-4726-8bb2-a8012fd5ed65"]

#%% all at once
finished_workloads = final_workload_per_week.groupby(["user_id", "goal_id"])["workload_finished"].agg([sum, "count", np.mean]).reset_index().rename(columns={
    "sum": "finished_workloads",
    "count": "total_workloads",
    "mean": "ratio"
})
finished_workloads

# %%
