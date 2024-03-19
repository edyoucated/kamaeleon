import os
import json
import pandas as pd 

from user_stats import user_stats, org_info
from build_static_learning_path import static_learning_path

from kamaeleon.analysis.analysis_helper import (
    resolve_assessment,
    DATA_PATH_ADAPTIVE_LEARNING, 
    SAVE_PATH_ADAPTIVE_LEARNING
)

EXCLUDE_LEARNING_PATH_ID = "2853587d-9655-48f8-b83c-be05944fe90b"
STATIC_LEARNING_PATH_ID = "3b4a4f82-f6c7-4ab2-a085-ed658a8bc599"


# GET GENERIC LEARNING PATHS
dim_learning_path = pd.read_csv(os.path.join(DATA_PATH_ADAPTIVE_LEARNING, "dim_learning_path.csv"))
dim_learning_path = dim_learning_path[dim_learning_path["learning_path_id"] != EXCLUDE_LEARNING_PATH_ID].reset_index()

dim_learning_path = dim_learning_path[[
    "learning_path_id", 
    "title_de", 
    "owner_organization_id", 
]].rename(columns={
    "title_de": "learning_path_title",
    "owner_organization_id": "organization_id"
}).merge(
    org_info[["organization_id", "learning_path_type"]],
    on="organization_id",
    how="left"
)

bri_learning_path_skill = pd.read_csv(os.path.join(DATA_PATH_ADAPTIVE_LEARNING, "bri_learning_path_skill.csv"))
bri_learning_path_skill = bri_learning_path_skill[bri_learning_path_skill["learning_path_id"] != EXCLUDE_LEARNING_PATH_ID]
dim_skill = pd.read_csv(os.path.join(DATA_PATH_ADAPTIVE_LEARNING, "dim_skill.csv"))

generic_learning_paths = bri_learning_path_skill.merge(
    dim_learning_path,
    on="learning_path_id",
    how="left"
).merge(
    dim_skill[["skill_id", "title_de"]].rename(columns={"title_de": "skill_title"}),
    on="skill_id",
    how="left"
)

generic_learning_paths = pd.concat([generic_learning_paths, static_learning_path]).reset_index(drop=True)


# resolve assessments
personalized_learning_path = pd.read_csv(os.path.join(DATA_PATH_ADAPTIVE_LEARNING, "dim_personalized_learning_path.csv"))

resolved_assessments = []
for i, row in personalized_learning_path.iterrows():
    if row["assessments"] is not None:
        assessment = json.loads(row["assessments"])
        if len(assessment) > 0:
            resolved_assessment = resolve_assessment(
                assessment=assessment
            )
            resolved_assessment["user_id"] = row["user_id"]
            resolved_assessments.append(resolved_assessment)

resolved_assessments_df = pd.concat(resolved_assessments)


#
assessment_stats = user_stats.merge(
    generic_learning_paths, 
    on=["learning_path_id", "organization_id", "learning_path_type"],
    how="left"
).merge(
    resolved_assessments_df,
    on=["skill_id", "user_id"],
    how="left"
)

#add user skills
user_skill_history = pd.read_csv(os.path.join(DATA_PATH_ADAPTIVE_LEARNING, "fct_user_skill_history.csv"))
user_skill_history = user_skill_history[user_skill_history["user_id"].isin(user_stats["user_id"].unique().tolist())]
ush = user_skill_history[[
    "user_id", 
    "skill_id",
    "is_mastered", 
    "origin_validation"
]]

learning_results = ush[ush["origin_validation"] == "LearningContentCompletion"]
learning_results["has_learned"] = True
learning_results = learning_results[[
    "user_id", 
    "skill_id", 
    "has_learned"
]]

assessment_stats = assessment_stats.merge(
    learning_results,
    on=["user_id", "skill_id"],
    how="left"
)


# write results 
assessment_stats.to_csv(
    os.path.join(SAVE_PATH_ADAPTIVE_LEARNING, "adaptive_assessments.csv"), 
    index=False
)
