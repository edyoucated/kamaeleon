#%% In welcher Woche wird welcher Person welches Feedback angezeigt?
import json
import os
import pandas as pd

from typing import List

from kamaeleon.analysis.analysis_helper import (
    camel_to_snake,
    DATA_PATH_LEARNING_INDICATOR, 
    SAVE_PATH_LEARNING_INDICATOR
)

ADMIN_USER_IDS = [
    "12936f74042d2af32db00b891475056db7db2625",
    "2697173034fb619d6d1a32721d7c26471dba5e47",
    "beda4e21494f048c31c6e97929d95b12c3ea9975",
    "4a5757db49c9782e62fbc5c01f0f5902cd744bfb",
    "4a126d34da7287b1147c6be2a83511c0f9c754d2"
]

event = pd.read_csv(os.path.join(DATA_PATH_LEARNING_INDICATOR, "fct_event.csv"))

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

displayed_indicator = pd.concat(result_raw).sort_values(["user_id", "derived_tstamp"]).reset_index()

displayed_indicator = displayed_indicator[[
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

displayed_indicator = displayed_indicator[~displayed_indicator["user_id"].isin(ADMIN_USER_IDS)]
displayed_indicator.to_csv(
    os.path.join(
        SAVE_PATH_LEARNING_INDICATOR,
        "displayed_indicator.csv"
    ),
    index=False
)
