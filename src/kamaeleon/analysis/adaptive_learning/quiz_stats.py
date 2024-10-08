import os
import pandas as pd
from user_stats import user_stats

from kamaeleon.analysis.analysis_helper import (
    DATA_PATH_ADAPTIVE_LEARNING, 
    SAVE_PATH_ADAPTIVE_LEARNING
)

learning_content_progress = pd.read_csv(os.path.join(DATA_PATH_ADAPTIVE_LEARNING, "fct_learning_content_progress.csv"))
learning_content_activity = pd.read_csv(os.path.join(DATA_PATH_ADAPTIVE_LEARNING, "fct_learning_content_activity.csv"))

user_ids = user_stats["user_id"].unique().tolist()

quiz_activities = []

for user_id in user_ids:
    user_activity = learning_content_activity[learning_content_activity["user_id"] == user_id].sort_values("performed_at")

    user_question_activity: pd.DataFrame = user_activity[user_activity["object_type"] == "Question"][[
        "learning_content_activity_id",
        "performed_at",
        "action",
        "object_id",
        "object_type"
    ]]

    user_question_activity_counts = user_question_activity.groupby(["object_id", "action"])["learning_content_activity_id"].count().reset_index()

    user_question_activity_counts.columns = ["question_id", "action", "count"]
    user_question_activity_counts[user_question_activity_counts["action"].isin(["completed", "failed"])]

    relevant_actions = ["opened", "started", "failed", "completed"]

    user_question_activity_counts = user_question_activity_counts[user_question_activity_counts["action"].isin(relevant_actions)]

    user_question_activity_counts["action"] = pd.Categorical(
        user_question_activity_counts["action"], 
        relevant_actions
    )

    user_question_activity_counts_pivot = user_question_activity_counts.pivot(
        index="question_id", 
        columns="action", 
        values="count"
    ).reset_index()
    user_question_activity_counts_pivot["user_id"] = user_id

    quiz_activities.append(user_question_activity_counts_pivot)


quiz_activities_df = pd.concat(objs=quiz_activities)
quiz_activities_df = quiz_activities_df[[
    "user_id", 
    "question_id", 
    "opened", 
    "started", 
    "failed", 
    "completed"
]]
quiz_activities_df.fillna(value=0, inplace=True)

quiz_activities_df.to_csv(
    os.path.join(SAVE_PATH_ADAPTIVE_LEARNING, "quiz_activities.csv"), 
    index=False
)

quiz_stats = quiz_activities_df.rename(columns={"question_id": "object_id"})
