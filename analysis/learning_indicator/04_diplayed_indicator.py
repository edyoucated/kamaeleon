#%% In welcher Woche wird welcher Person welches Feedback angezeigt?
import pandas as pd
import json

from typing import List
from helper import camel_to_snake

ADMIN_USER_IDS = [
    "12936f74042d2af32db00b891475056db7db2625",
    "2697173034fb619d6d1a32721d7c26471dba5e47",
    "beda4e21494f048c31c6e97929d95b12c3ea9975",
    "4a5757db49c9782e62fbc5c01f0f5902cd744bfb",
    "4a126d34da7287b1147c6be2a83511c0f9c754d2"
]

#%% 
event = pd.read_csv("data/event.csv")

#%% 
sample = event.sample(1)

#%% derived_tstamp, event_id, user_id


result_raw: List[pd.DataFrame] = []

for i, row in event.iterrows():
    temp = pd.DataFrame(
        json.loads(row["direct_object"])["data"],
        index=[i]
    )
    temp["derived_tstamp"] = row["derived_tstamp"]
    temp["event_id"] = row["event_id"]
    temp["user_id"] = row["user_id"]

    temp.columns = [camel_to_snake(x) for x in temp.columns]

    result_raw.append(
        temp
    )

result = pd.concat(result_raw).sort_values(["user_id", "derived_tstamp"]).reset_index()

result = result[[
    'user_id',
    'derived_tstamp',
    'days_left_until_deadline', 
    'percentage_of_completion',
    'remaining_duration_minutes',
    'progress_indicator_status', 
    'progress_indicator_text',
    'progress_motivation_emoji', 
    'progress_motivation_quote',
    'progress_motivation_status', 
    'event_id',
    'language'
]]

#%% 
result = result[~result["user_id"].isin(ADMIN_USER_IDS)]

#%% 
result[result["user_id"] == "2c0b6950168866c172900ee2c1005d26371fc7c8"]

# %%
