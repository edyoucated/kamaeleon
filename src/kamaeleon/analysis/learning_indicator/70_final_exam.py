#%%
import os
import json
import pandas as pd

from kamaeleon.analysis.analysis_helper import (
    DATA_PATH_LEARNING_INDICATOR, 
    SAVE_PATH_LEARNING_INDICATOR
)

#%% 
lp_exam = pd.read_csv(os.path.join(DATA_PATH_LEARNING_INDICATOR, "fct_learning_path_exam.csv"))

exam_results_raw = []
for i, row in lp_exam.iterrows():
    temp = json.loads(row["exam_results"])

    for i, tm in enumerate(temp):
        exam_results_raw.append(
            (   
                row["learning_path_exam_id"],
                i,
                tm["questionId"],
                tm["questionTitle"],
                tm["connectedSkillId"],
                tm["isCorrect"], 
                tm["isSkipped"], 
                row["origin_id"]
            )
        )

exam_results = pd.DataFrame(
    exam_results_raw, 
    columns=[
        "learning_path_exam_id", 
        "question_order",
        "question_id",
        "question_title",
        "connected_skill_id",
        "is_correct",
        "is_skipped",
        "learning_path_id"
    ]
)

exam_results.to_csv(
    os.path.join(SAVE_PATH_LEARNING_INDICATOR, "learning_path_exam_results.csv"),
    index=False
)
