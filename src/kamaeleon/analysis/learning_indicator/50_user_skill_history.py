#%% 
import os
import pandas as pd

from kamaeleon.analysis.analysis_helper import (
    DATA_PATH_LEARNING_INDICATOR, 
    SAVE_PATH_LEARNING_INDICATOR
)

user_skill_history = pd.read_csv(os.path.join(DATA_PATH_LEARNING_INDICATOR, "fct_user_skill_history.csv"))

user_skill_history.to_csv(
    os.path.join(
        SAVE_PATH_LEARNING_INDICATOR,
        "user_skill_history.csv"
    ),
    index=False
)

#%% Example: pick a random user 
USER_ID: str = user_skill_history.sample(1)["user_id"].iloc[0]

ush = user_skill_history[user_skill_history["user_id"] == USER_ID]
ush

#%% stats
ush.groupby(["origin_validation", "is_mastered"])["skill_id"].count()
