#%%
# Wie oft hat eine Person ein gesetztes Lernziel geändert oder gelöscht?
import pandas as pd

from helper import transform_learning_goal_changes


path = "data/goal_activity.csv"

#%% 
learning_goal_activity = pd.read_csv(path)
learning_goal_changes = transform_learning_goal_changes(path=path)
learning_goal_changes
