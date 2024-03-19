import os
import pandas as pd

from kamaeleon.analysis.analysis_helper import (
    DATA_PATH_ADAPTIVE_LEARNING, 
    SAVE_PATH_ADAPTIVE_LEARNING
)


learning_content_progress = pd.read_csv(os.path.join(DATA_PATH_ADAPTIVE_LEARNING, "fct_learning_content_progress.csv"))
materials = pd.read_csv(os.path.join(DATA_PATH_ADAPTIVE_LEARNING, "dim_material.csv"))


lcp = learning_content_progress[learning_content_progress["object_type"] == "Material"]
lcp = lcp[[
    "user_id", 
    "object_id", 
    "is_completed", 
    "first_started_at_derived", 
    "first_completed_at"
]]

lcp["first_started_at_derived"] = pd.to_datetime(lcp["first_started_at_derived"])
lcp["first_completed_at"] = pd.to_datetime(lcp["first_completed_at"])
lcp["actual_duration_minutes"] = (lcp["first_completed_at"] - lcp["first_started_at_derived"]).dt.total_seconds()/60
lcp["actual_duration_minutes"] = lcp["actual_duration_minutes"].apply(lambda x: round(x, 2))
lcp.rename(columns={"object_id": "material_id"}, inplace=True)
lcp = lcp.merge(
    materials[[
        "material_id",
        "duration_minutes",
        "empirical_duration_minutes"
    ]],
    on="material_id",
    how="left"
)
lcp["has_processed"] = (lcp["actual_duration_minutes"] >= 0.25 * lcp["empirical_duration_minutes"])

lcp.to_csv(
    os.path.join(SAVE_PATH_ADAPTIVE_LEARNING, "materials_activities.csv"), 
    index=False
)


material_stats = lcp.rename(columns={"material_id": "object_id"})
