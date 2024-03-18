#%%
# Wie oft hat eine Person ein gesetztes Lernziel geändert oder gelöscht?
import pandas as pd
import os

from kamaeleon.analysis.analysis_helper import (
    transform_learning_goal_changes, 
    DATA_PATH_LEARNING_INDICATOR,
    SAVE_PATH_LEARNING_INDICATOR
)


path = os.path.join(DATA_PATH_LEARNING_INDICATOR, "fct_goal_activity.csv")
learning_goal_activity = pd.read_csv(path)
learning_goal_changes = transform_learning_goal_changes(path=path)
learning_goal_changes.to_csv(
    os.path.join(SAVE_PATH_LEARNING_INDICATOR, "learning_goal_changes.csv"),
    index=False
)
