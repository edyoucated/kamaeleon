#%% Was für ein Ziel haben sich die Lernenden gesetzt (d.h. welche Deadline) und wann?
import os
import pandas as pd 

from kamaeleon.analysis.analysis_helper import load_users
from kamaeleon.analysis.analysis_helper import (
    DATA_PATH_LEARNING_INDICATOR,
    SAVE_PATH_LEARNING_INDICATOR
)

ORGANIZATION_IDS = [
    "a1460275-3c3e-44ee-b522-9dfb59efffb7", # EIF 
    "0c30cde3-7b25-4765-9db8-60696a8fb5a0", # KAMAELEON-A
    "adad2008-bbf3-40f5-b292-7920fd9bc188", # KAMAELEON-B 
]

learning_goal = pd.read_csv(os.path.join(DATA_PATH_LEARNING_INDICATOR, "fct_goal.csv"))
users = load_users(
    path=os.path.join(DATA_PATH_LEARNING_INDICATOR, "dim_membership.csv"),
    organization_ids=ORGANIZATION_IDS
)
learning_path = pd.read_csv(os.path.join(DATA_PATH_LEARNING_INDICATOR, "dim_learning_path.csv"))

# %% filter learning goals for organization and users in that organization
learning_goal = learning_goal[learning_goal["organization_id"].isin(ORGANIZATION_IDS)]
learning_goal = learning_goal[learning_goal["user_id"].isin(users["user_id"].unique())]
learning_goal.reset_index(drop=True, inplace=True)

#%% What kind of goal is it? -> LearningPath + Deadline
learning_goal = learning_goal.rename(
    columns={"related_entity_id": "learning_path_id"}
).merge(
    learning_path[["learning_path_id", "title_de", "title_en"]], 
    on="learning_path_id", 
    how="left"
).merge(
    users[["user_id", "research_id"]],
    on="user_id",
    how="left"
)

# take only relevant columns 
learning_goal = learning_goal[[
    "goal_id", 
    "user_id",
    "research_id",
    "started_at", 
    "completed_at", 
    "abandoned_at", 
    "due_on", 
    "learning_path_id",
    "title_en", 
    "title_de"
]]

# %% save to file 
learning_goal.to_csv(
    os.path.join(SAVE_PATH_LEARNING_INDICATOR, "learning_goals.csv"), 
    index=False
)
