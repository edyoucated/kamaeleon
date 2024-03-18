#%% 
import pandas as pd 

from adaptive_learning_helper import load_users, load_users_without_research_id
from adaptive_learning_helper import ORGANIZATION_IDS_LEARNING_INDICATOR as ORGANIZATION_IDS
from adaptive_learning_helper import LearningPathType

#%%
org_info = pd.DataFrame({
    "organization_id": ORGANIZATION_IDS,
    "organization_name": [f"KAMAELEON-{x}" for x in ["A", "B"]],
    "learning_path_type": [
        LearningPathType.SELF_ASSESSMENT.value,
        LearningPathType.SELF_ASSESSMENT.value
    ]
})

users = load_users(
    path="data/membership.csv",
    organization_ids=ORGANIZATION_IDS, 
    resolve_rid=False # CHANGE HERE IFF NECESSARY
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
    on=["user_id"],
    how="left"
)

general_stats.to_excel("export/stats_summary_kamA_kamB_with_wrong_RID.xlsx", index=False)


#%% users with wrong ID
users[users["research_id"].apply(lambda x: (len(str(x).strip()) != 5) if x is not None else True)].to_excel("export/users_with_wrong_id.xlsx", index=False)

#%% 
users_with_wrong_id = users[users["research_id"].apply(lambda x: (len(x) != 5) if x is not None else True)]["user_id"].to_list()

