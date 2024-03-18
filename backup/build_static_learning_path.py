#%%
import json
import pandas as pd
import hashlib

from user_stats_summary import LearningPathType

STATIC_LEARNING_PATH_ID = "3b4a4f82-f6c7-4ab2-a085-ed658a8bc599"
STATIC_ORGANIZATION_ID = "b2cc892d-12d6-4aab-a4d0-2bfa1bc723f0"

dim_learning_path = pd.read_csv("data/dim_learning_path.csv")

#%% "build" static learning path
static_content = json.loads(dim_learning_path[dim_learning_path["learning_path_id"] == STATIC_LEARNING_PATH_ID].reset_index().iloc[0]["content"])

lp = []

for item in static_content:
    skill_title = item["translations"]["de"]["title"]
    skill_id = hashlib.sha256(skill_title.encode('utf-8')).hexdigest()

    elements = []
    for elem in item["elements"]:
        if "materialId" in elem:
            elements.append({
                "skill_id": skill_id,
                "skill_title": skill_title,
                "element_id": elem["materialId"],
                "element_type": "material"
            })
        elif "quiz" in elem:
            for e in elem["quiz"]["elements"]:
                elements.append({
                    "skill_id": skill_id,
                    "skill_title": skill_title,
                    "element_id": e["questionId"],
                    "element_type": "question"
                })
        lp.extend(elements)

static_learning_path_detailed = pd.DataFrame(lp)
static_learning_path_detailed["learning_path_id"] = STATIC_LEARNING_PATH_ID

static_learning_path = static_learning_path_detailed[["skill_id", "skill_title"]].drop_duplicates().reset_index(drop=True)

# add more columns 
static_learning_path["learning_path_id"] = STATIC_LEARNING_PATH_ID
static_learning_path["position"] = range(1, len(static_learning_path) + 1)
static_learning_path["learning_path_title"] = "Microsoft Excel"
static_learning_path["learning_path_type"] = LearningPathType.STATIC.value
static_learning_path["organization_id"] = STATIC_ORGANIZATION_ID

static_learning_path = static_learning_path[[
    "learning_path_id", 
    "skill_id", 
    "position",
    "learning_path_title",
    "organization_id",
    "learning_path_type",
    "skill_title"
]]

# %%
static_learning_path_detailed.rename(columns={
    "element_id": "object_id", 
    "element_type": "object_type"
}, inplace=True)

# get position
static_learning_path_detailed = static_learning_path_detailed.merge(
    static_learning_path[["skill_id", "position"]],
    on="skill_id", 
    how="left"
).drop_duplicates().sort_values(["position", "object_type", "object_id"])
