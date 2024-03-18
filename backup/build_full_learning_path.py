#%%
import pandas as pd


lp = pd.read_csv("data/dim_learning_path.csv")
bri_lp_skill = pd.read_csv("data/bri_learning_path_skill.csv")
dim_skill = pd.read_csv("data/dim_skill.csv")
skill_duration = pd.read_csv("data/skill_duration.csv")

dim_question = pd.read_csv("data/dim_question.csv")
bri_skill_question = pd.read_csv("data/bri_skill_question.csv")
bri_material_question = pd.read_csv("data/bri_material_question.csv")

dim_material = pd.read_csv("data/material.csv")
dim_lesson = pd.read_csv("data/lesson.csv")
bri_lesson_material = pd.read_csv("data/bri_lesson_material.csv")

user_skill_history = pd.read_csv("data/fct_user_skill_history.csv")
dependencies = pd.read_csv("data/dim_skill_skill_dependency.csv")


def get_full_learning_path(learning_path_id: str) -> pd.DataFrame:

# LP_ID = "50bf8f86-68f1-4fc5-b83e-f7c5834e4f5d"

    full_lp = bri_lp_skill[bri_lp_skill["learning_path_id"] == learning_path_id]
    full_lp = full_lp.merge(
        dim_skill[["skill_id", "title_de"]].rename(columns={"title_de": "skill_title"}),
        on="skill_id", 
        how="left"
    )

    lp_skill_ids = full_lp["skill_id"].unique().tolist()

    # get all related materials
    lp_materials = full_lp.merge(
            dim_lesson[(dim_lesson["language"] == "de") & (dim_lesson["is_default"] == True)], 
            on="skill_id", 
            how="left"
        ).merge(
            bri_lesson_material, 
            on="lesson_id",
            how="left"
        ).dropna(
            subset=["lesson_id"]
        ).rename(
            columns={
                "position_x": "skill_position",
                "position_y": "material_position",
                "purpose_x": "purpose",
                "title": "material_title"
            }
        ).drop(columns=[
            "lesson_material_id",
            "lesson_id", 
            "purpose", 
            "language", 
            "is_default", 
            "material_position"
        ])

    lp_materials = lp_materials[[
        "skill_id",
        "material_id", 
    ]]
    lp_materials["object_type"] = "material"


#%% get questions attached to materials
    material_questions = lp_materials.merge(
            bri_material_question[["material_id", "question_id"]],
            on="material_id", 
            how="left"
        ).dropna()
    material_questions = material_questions[[
        "skill_id", 
        "question_id"
    ]]

    #%% get questions attached to skills 
    skill_questions = bri_skill_question[bri_skill_question["skill_id"].isin(lp_skill_ids)][["skill_id", "question_id"]]

    #%% combine 
    all_questions = pd.concat([skill_questions, material_questions])
    all_questions["object_type"] = "question"

    #%% assemble full LP 
    lp_content = pd.concat([
        all_questions.rename(columns={"question_id": "object_id"}), 
        lp_materials.rename(columns={"material_id": "object_id"})
    ])


    full_learning_path = full_lp.merge(
        lp_content,
        on="skill_id",
        how="left"
    ).sort_values(["position", "object_type", "object_id"])

    return full_learning_path
