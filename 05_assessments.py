#%% 
import pandas as pd

# %%
user_skill_history = pd.read_csv("data/user_skill_history.csv")

#%% pick a random user 
USER_ID: str = user_skill_history.sample(1)["user_id"].iloc[0]

ush = user_skill_history[user_skill_history["user_id"] == USER_ID]
ush

#%% stats
ush.groupby(["origin_validation", "is_mastered"])["skill_id"].count()
