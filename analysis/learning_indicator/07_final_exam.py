#%%
import pandas as pd
import json

#%% 
lp_exam = pd.read_csv("data/learning_path_exam.csv")

# %%
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
                tm["isSkipped"] 
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
        "is_skipped"
    ]
)

exam_results

# %%
exam_results[exam_results["learning_path_exam_id"] == "bbe0d4a2-64fc-477a-997e-f5c0c7ba8065"]
