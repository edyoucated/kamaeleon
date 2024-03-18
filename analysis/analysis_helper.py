#%%
import pandas as pd
import json 
import re

from typing import List, Tuple
from enum import Enum


ORGANIZATION_IDS_LEARNING_INDICATOR = [
    "a1460275-3c3e-44ee-b522-9dfb59efffb7", # EIF 
    "0c30cde3-7b25-4765-9db8-60696a8fb5a0", # KAMAELEON-A
    "adad2008-bbf3-40f5-b292-7920fd9bc188", # KAMAELEON-B 
]

ORGANIZATION_IDS_ADAPTIVE_LEARNING = [
    "b2cc892d-12d6-4aab-a4d0-2bfa1bc723f0", # KAMAELEON-C
    "9d257b52-f84a-4813-97f5-3b0d63dc6e67", # KAMAELEON-D
    "cb4225bf-6fea-4fa8-8a98-8272cb0b139b" # KAMAELEON-E
]


class LearningPathType(Enum):
    STATIC = "STATIC"
    SELF_ASSESSMENT = "SELF_ASSESSMENT"
    QUIZ_ASSESSMENT = "QUIZ_ASSESSMENT"


def resolve_research_id(x: str) -> None: 
    result = None
    x = json.loads(x)
    if x["name"] == "RESEARCH-ID":
        if re.search(r"[a-zA-Z]\d{2}[a-zA-Z]\d", x["value"]):
            result = x["value"].upper() 
    return result

def load_users(
        organization_ids: List[str],
        path: str="data/membership.csv") -> pd.DataFrame:
    membership = pd.read_csv(path)
    membership = membership[membership["role"] == "Member"]
    membership["research_id"] = membership["reference_data_attribute_1"].apply(lambda x: resolve_research_id(x) if not pd.isna(x) else None)
    membership.drop(columns=["reference_data_attribute_1"], inplace=True)
    membership = membership[~pd.isna(membership["research_id"])]
    membership = membership[membership["organization_id"].isin(organization_ids)]
    return membership


def load_users_without_research_id(
        organization_ids: List[str],
        path: str="data/membership.csv") -> pd.DataFrame:
    membership = pd.read_csv(path)
    membership = membership[membership["role"] == "Member"]
    membership["research_id"] = membership["reference_data_attribute_1"].apply(lambda x: resolve_research_id(x) if not pd.isna(x) else None)
    membership.drop(columns=["reference_data_attribute_1"], inplace=True)
    membership = membership[pd.isna(membership["research_id"])]
    membership = membership[membership["organization_id"].isin(organization_ids)]
    return membership


def get_research_id_by_user_id(
        user_id: str, 
        organization_ids: list,
        path: str="data/membership.csv") -> str:
    users = load_users(
        organization_ids=organization_ids,
        path=path
    )
    users.set_index("user_id", drop=True, inplace=True)
    try:
        research_id = users.loc[user_id]["research_id"]
    except KeyError:
        research_id = None
    return research_id


def get_user_id_by_research_id(research_id: str, path: str="data/membership.csv") -> str:
    users = load_users(path=path)
    users.set_index("user_id", drop=True, inplace=True)
    try: 
        user_id = users.loc[users["research_id"] == research_id].index[0]
    except IndexError:
        user_id = None
    return user_id


def transform_learning_goal_changes(path: str) -> pd.DataFrame:
    def find_reason_for_activity_update(row):
        result = [
            row["goal_activity_id"], 
            row["subject_id"], # goal_id, 
            row["subject_user_id"], # user_id
            row["created_at"]
        ]
        if pd.isna(row["old_started_at"]) and not pd.isna(row["new_started_at"]):
            result.append("goal_started")
        elif pd.isna(row["old_completed_at"]) and not pd.isna(row["new_completed_at"]):
            result.append("goal_completed")
        elif pd.isna(row["old_abandoned_at"]) and not pd.isna(row["new_abandoned_at"]):
            result.append("goal_abandoned")
        elif row["old_due_on"] != row["new_due_on"]:
            result.append("due_date_changed")
        else:   
            print("Reason for goal change unknown.")
            result.append("reason_unknown")
        return result


    learning_goal_activity = pd.read_csv(path)
    result = learning_goal_activity.apply(find_reason_for_activity_update, axis=1).to_list()
    result = pd.DataFrame(result, columns=["goal_activity_id", "subject_id", "subject_user_id", "created_at", "update_reason"])
    return result



def camel_to_snake(column_name):
    """
    Convert a column name from camel case to snake case.
    """
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', column_name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def resolve_assessment(assessment: dict) -> pd.DataFrame:

    assessment_results = []
    revision_results = []

    for assessment_step in assessment:

        # resolve assessedSkills 
        assessed_skills = assessment_step["assessedSkills"]
        for s in assessed_skills:
            assessment_results.append({
                "skill_id": s["skillId"],
                "assessment_result": s["userAnswer"]
            })


        # resolve reviewedSkills
        reviewed_skills = assessment_step["reviewedSkills"]
        for s in reviewed_skills:
            revision_results.append({
                "skill_id": s["skillId"],
                "assessment_before_revision": s["assessedAs"],
                "assessment_after_revision": s["reviewedAs"],
                "correction_in_revision": (s["assessedAs"] != s["reviewedAs"])
            })


    assessment_results_df = pd.DataFrame(assessment_results)
    revision_results_df = pd.DataFrame(revision_results)

    final = revision_results_df.merge(
        assessment_results_df, 
        on="skill_id",
        how="outer"
    )

    return final



