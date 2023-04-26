#%%
import pandas as pd 

# %%
lc_progress = pd.read_csv("data/learning_content_progress.csv")
material = pd.read_csv("data/material.csv")

# %%
material_progress = lc_progress[lc_progress["object_type"] == "Material"]
material_progress = material_progress[~pd.isna(material_progress["first_completed_at"])]

material_progress = material_progress[[
    "object_id",
    "user_id", 
    "first_started_at_derived",
    "first_completed_at",
    "context_organization_id",
]].rename(
    columns={"object_id": "material_id"}
).merge(
    material[["material_id", "duration_minutes", "empirical_duration_minutes"]],
    on="material_id",
    how="left"
)

material_progress["empirical_duration_minutes"] = material_progress["empirical_duration_minutes"].fillna(material_progress["duration_minutes"])

#%% 
material_progress["first_started_at_derived"] = pd.to_datetime(material_progress["first_started_at_derived"])
material_progress["first_completed_at"] = pd.to_datetime(material_progress["first_completed_at"])
material_progress["actual_time_approx"] = (material_progress["first_completed_at"] - material_progress["first_started_at_derived"]).dt.total_seconds()/60

# %%
