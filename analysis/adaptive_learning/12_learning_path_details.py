#%%
import json
import pandas as pd 

from analysis.analysis_helper import resolve_assessment
from user_stats_summary import user_stats, org_info

from build_static_learning_path import static_learning_path_detailed as static_learning_path
from build_full_learning_path import get_full_learning_path

from material_stats import material_stats
from quiz_stats import quiz_stats

EXCLUDE_LEARNING_PATH_ID = "2853587d-9655-48f8-b83c-be05944fe90b"

STATIC_LEARNING_PATH_ID = "3b4a4f82-f6c7-4ab2-a085-ed658a8bc599"
ADAPTIVE_QA_LEARNING_PATH_ID = "d62c5dbe-7e5e-4cc9-929c-2112641cd7a2"
ADAPTIVE_SA_LEARNING_PATH_ID = "50bf8f86-68f1-4fc5-b83e-f7c5834e4f5d"


#%%
adaptive_sa_learning_path = get_full_learning_path(learning_path_id=ADAPTIVE_SA_LEARNING_PATH_ID)
adaptive_qa_learning_path = get_full_learning_path(learning_path_id=ADAPTIVE_QA_LEARNING_PATH_ID)
static_learning_path

all_paths = pd.concat(
    [
        static_learning_path,
        adaptive_qa_learning_path,
        adaptive_sa_learning_path
    ]
)

#%% give one path to each user 
user_paths = user_stats.merge(
    all_paths, 
    on="learning_path_id", 
    how="left"
)

#%% merge with user performance
stats = pd.concat([
    material_stats, 
    quiz_stats
])

final = user_paths.merge(
    stats,
    on=["user_id", "object_id"],
    how="left"
)

#%% 
final.to_excel("export/user_learning_paths.xlsx", index=False)
