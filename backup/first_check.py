#%%
import pandas as pd
import json
from pprint import pprint
from helper import get_research_id_by_user_id, get_user_id_by_research_id

#%% this needs to be verified
ADMIN_USER_IDS = [
    "12936f74042d2af32db00b891475056db7db2625",
    "2697173034fb619d6d1a32721d7c26471dba5e47",
    "beda4e21494f048c31c6e97929d95b12c3ea9975",
    "4a5757db49c9782e62fbc5c01f0f5902cd744bfb",
    "4a126d34da7287b1147c6be2a83511c0f9c754d2"
]

CREATED_AFTER = "2023-03-30"

#%%
learning_path = pd.read_csv("data/learning_path.csv")

goal = pd.read_csv("data/goal.csv")
goal_activity = pd.read_csv("data/goal_activity.csv")

periodic_workload = pd.read_csv("data/periodic_workload.csv")
periodic_workload_trigger = pd.read_csv("data/periodic_workload_trigger.csv")

event = pd.read_csv("data/event.csv")

# %% 
goal = goal.merge(
    learning_path, 
    left_on="related_entity_id",
    right_on="learning_path_id", 
    how="left"
)
goal = goal[~goal["user_id"].isin(ADMIN_USER_IDS)]
goal = goal[goal["created_at"] > CREATED_AFTER]
GOAL_IDS = goal["goal_id"].unique().tolist()

goal_activity = goal_activity[goal_activity["new_goal_id"].isin(GOAL_IDS)]

#%% try and filter out admins 
# goal.groupby(["user_id"])["goal_id"].count().sort_values(ascending=False)

#%% How many (unique) users have set a goal? 
goal["user_id"].nunique()

#%% How many users have completed a goal?
goal[~pd.isna(goal["completed_at"])]
goal[~pd.isna(goal["completed_at"])]["goal_id"].count()


#%% Goal activity: modifications per goal 
goal_activity.groupby(["new_goal_id"])["goal_activity_id"].count().sort_values(ascending=False)


#%% check periodic workloads 
# SPECIFIC_GOAL_ID = "ecca8205-560c-4d5d-978d-ce985d9f53ea" # finished with bad exam
# SPECIFIC_GOAL_ID = "4ff4f270-ad03-410c-9918-2529ab44883a" finished EIF
# SPECIFIC_GOAL_ID = "053f073b-87cd-4726-8bb2-a8012fd5ed65"
# SPECIFIC_GOAL_ID = "3449e8c0-a48e-4cd8-8c74-4f44d9865f94"
SPECIFIC_GOAL_ID = "7d225ef1-5057-4fec-aab1-ea3c2bfe6fc4"


goal[goal["goal_id"] == SPECIFIC_GOAL_ID]
#%% 


workload = periodic_workload[periodic_workload["goal_id"] == SPECIFIC_GOAL_ID].sort_values(["period_starts_on", "revision"]).reset_index(drop=True)
last_workload = workload.groupby("period_starts_on").last().reset_index()

workload.sort_values("computed_at")

# x = json.loads(last_workload.iloc[0]["planned"])
# y = json.loads(last_workload.iloc[0]["actual"])

# pprint(x)
# pprint(y)
# a = 7

# x = json.loads(workload.iloc[a]["planned"])
# y = json.loads(workload.iloc[a]["actual"])

# pprint(x)
# pprint(y)

#%%
goal_activity[goal_activity["new_goal_id"] == SPECIFIC_GOAL_ID]

# %%
periodic_workload_trigger[periodic_workload_trigger["goal_id"] == SPECIFIC_GOAL_ID]

#%% events 
# Can I link this to the LP via page url? -> Yes
# b = json.loads(event.iloc[0]["direct_object"])
# c = json.loads(event.iloc[0]["subject"])
# c


#%% put together one set of workloads into one table 

workload["computed_at"] = pd.to_datetime(workload["computed_at"])
workload.sort_values("computed_at", inplace=True)

def get_learning_duration(x) -> int:
    return json.loads(x)["learningDurationMinutes"]

def get_week_stamp(timestamp: pd.Timestamp) -> str:
    timestamp = timestamp.to_pydatetime()
    year, week_num, _ = timestamp.isocalendar()
    return f"{year}-W{week_num:02d}"



# table 
# time_stamp, computed_in_period, computed_for_period, revision, current_week_planned, current_week_actual, next_week_planned, next_week_actual
timeline = []

for i, row in workload.iterrows():
    weekstamp = get_week_stamp(row["computed_at"])
    is_current_week = (weekstamp == row["period_identifier"])


    timeline.append((
        row["computed_at"],
        weekstamp,
        row["period_identifier"],
        row["revision"], 
        get_learning_duration(row["planned"]) if is_current_week else None,
        get_learning_duration(row["actual"]) if is_current_week else None,
        get_learning_duration(row["planned"]) if not is_current_week else None,
        get_learning_duration(row["actual"]) if not is_current_week else None,
        row["related_entity_id"]
    ))

timeline = pd.DataFrame(
    timeline, 
    columns=[
        "timestamp", 
        "computed_in_period", 
        "computed_for_period",
        "revision", 
        "current_week_planned", 
        "current_week_actual",
        "next_week_planned",
        "next_week_actual", 
        "related_entity_id"
    ]
)

timeline
