import os
import pandas as pd 

from kamaeleon.analysis.analysis_helper import (
    SAVE_PATH_ADAPTIVE_LEARNING, 
    ADAPTIVE_SA_LEARNING_PATH_ID,
    ADAPTIVE_QA_LEARNING_PATH_ID
)

from user_stats import user_stats
from material_stats import material_stats
from quiz_stats import quiz_stats

from build_static_learning_path import static_learning_path_detailed as static_learning_path
from build_full_learning_path import get_full_learning_path


adaptive_sa_learning_path = get_full_learning_path(learning_path_id=ADAPTIVE_SA_LEARNING_PATH_ID)
adaptive_qa_learning_path = get_full_learning_path(learning_path_id=ADAPTIVE_QA_LEARNING_PATH_ID)

all_paths = pd.concat(
    [
        static_learning_path,
        adaptive_qa_learning_path,
        adaptive_sa_learning_path
    ]
)

#give one path to each user 
user_paths = user_stats.merge(
    all_paths, 
    on="learning_path_id", 
    how="left"
)

#merge with user performance
stats = pd.concat([
    material_stats, 
    quiz_stats
])

final = user_paths.merge(
    stats,
    on=["user_id", "object_id"],
    how="left"
)

final.to_csv(
    os.path.join(SAVE_PATH_ADAPTIVE_LEARNING, "user_learning_paths.csv"), 
    index=False
)
