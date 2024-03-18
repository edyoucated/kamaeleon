#%% 
import pandas as pd 

from analysis.analysis_helper import load_users, load_users_without_research_id
from analysis.analysis_helper import ORGANIZATION_IDS_ADAPTIVE_LEARNING as ORGANIZATION_IDS
from analysis.analysis_helper import LearningPathType


#%%
org_info = pd.DataFrame({
    "organization_id": ORGANIZATION_IDS,
    "organization_name": [f"KAMAELEON-{x}" for x in ["C", "D", "E"]],
    "learning_path_type": [
        LearningPathType.STATIC.value, 
        LearningPathType.SELF_ASSESSMENT.value,
        LearningPathType.QUIZ_ASSESSMENT.value
    ], 
    "learning_path_id": [
        "3b4a4f82-f6c7-4ab2-a085-ed658a8bc599",
        "50bf8f86-68f1-4fc5-b83e-f7c5834e4f5d",
        "d62c5dbe-7e5e-4cc9-929c-2112641cd7a2"

    ]
})

users = load_users(
    path="data/membership.csv",
    organization_ids=ORGANIZATION_IDS
)
users.drop(columns=["role"], inplace=True)
print(f"Number of users with RESEARCH ID: {len(users)}")

users_without_research_id = load_users_without_research_id(
    path="data/membership.csv",
    organization_ids=ORGANIZATION_IDS
)
print(f"Number of users without RESEARCH ID: {len(users_without_research_id)}")


#%% 
user_stats = users.merge(
    org_info, 
    on="organization_id",
    how="left"
)

for i, row in user_stats.groupby("learning_path_type")["user_id"].count().reset_index().iterrows():
    print("Number of users with learning path type {}: {}".format(
        row["learning_path_type"], 
        row["user_id"]
    ))

# %% build general stats 
personalized_learning_path = pd.read_csv("data/dim_personalized_learning_path.csv")



general_stats = user_stats.merge(
    personalized_learning_path[[
        "origin_id",
        "user_id",
        'first_started_at_derived',
        'has_completed_content',
        'has_completed_content_at',
        'material_count_completed',
        'material_count_total',
        'material_count_completed_percentage',
        'skill_count_mastered',
        'skill_count_total',
        'skill_count_mastered_percentage'

    ]].rename(columns={"origin_id": "learning_path_id"}),
    on=["user_id", "learning_path_id"],
    how="left"
)

general_stats.to_excel("export/stats_summary.xlsx", index=False)
