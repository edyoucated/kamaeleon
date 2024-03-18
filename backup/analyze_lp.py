#%%
import pandas as pd
import plotnine as p9

lp = pd.read_csv("data/dim_learning_path.csv")
bri_lp_skill = pd.read_csv("data/bri_learning_path_skill.csv")
dim_skill = pd.read_csv("data/dim_skill.csv")
skill_duration = pd.read_csv("data/skill_duration.csv")

dim_question = pd.read_csv("data/dim_question.csv")
bri_skill_question = pd.read_csv("data/bri_skill_question.csv")

dim_material = pd.read_csv("data/material.csv")
dim_lesson = pd.read_csv("data/lesson.csv")
bri_lesson_material = pd.read_csv("data/bri_lesson_material.csv")

user_skill_history = pd.read_csv("data/fct_user_skill_history.csv")
dependencies = pd.read_csv("data/dim_skill_skill_dependency.csv")

LEARNING_PATH_IDS = [
    "0442ab59-49d8-4445-87d7-3b726ff7c16a", # Excel
    # "771f05b7-dd3d-4100-b570-9fa4de2baf5c", # Effektives Lernen
    "618b8110-8e44-469f-9d18-cc45415f150c", # Führen virtueller Teams
    "6317e477-b69e-4ec6-80c5-bb43a0962717" # Stressmanagement
]

LANGUAGE = "de"
export_path = "export/lp_stats/"

#%% general stats 

# number of atoms 
# number of quizzes 
# number of users

lps = bri_lp_skill[bri_lp_skill["learning_path_id"].isin(LEARNING_PATH_IDS)]
lps = lps.merge(
    dim_skill,
    on="skill_id",
    how="left"
)

lps_atoms = lps.groupby("learning_path_id")["skill_id"].count().reset_index()
lps_atoms.columns = ["learning_path_id", "number_of_atoms"]

lps_skill_id_list = lps["skill_id"].unique()

# number of relations
lps_dependencies = dependencies[dependencies["prerequisite_skill_id"].isin(lps_skill_id_list)]

lps_dependencies = lps.merge(
    lps_dependencies, 
    left_on="skill_id", 
    right_on="prerequisite_skill_id",
    how="left"
)

lps_number_of_dependencies = lps_dependencies.groupby("learning_path_id")["prerequisite_skill_id"].count().reset_index()
lps_number_of_dependencies.columns = ["learning_path_id", "number_of_prerequisites"]

lps_number_of_dependencies

# put together 
df = pd.DataFrame(
    {
        "learning_path_title": [
            "Excel", 
            "Führen virtueller Teams", 
            "Stressmanagement"
        ], 
        "learning_path_id": [
            "0442ab59-49d8-4445-87d7-3b726ff7c16a",
            "618b8110-8e44-469f-9d18-cc45415f150c",
            "6317e477-b69e-4ec6-80c5-bb43a0962717"
        ]
    }
)

df = df.merge(
    lps_atoms, 
    on="learning_path_id", 
    how="left"
).merge(
    lps_number_of_dependencies,
    on="learning_path_id",
    how="left"
).to_csv(export_path + "general_stats.csv")

#%% single lp stats



for lp_id in LEARNING_PATH_IDS:

    single_lp = bri_lp_skill[bri_lp_skill["learning_path_id"] == lp_id]
    single_lp = single_lp.merge(
        dim_skill,
        on="skill_id",
        how="left"
    )

    LP_SKILL_LIST = single_lp.sort_values(by="position")["skill_id"].to_list()

    #%% get materials
    lp_materials = single_lp.merge(
        dim_lesson[(dim_lesson["language"] == LANGUAGE) & (dim_lesson["is_default"] == True)], 
        on="skill_id", 
        how="left"
    ).merge(
        bri_lesson_material, 
        on="lesson_id",
        how="left"
    ).merge(
        dim_material, 
        on="material_id", 
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
    )

    lp_materials = lp_materials[[
        "skill_position", 
        "skill_id", 
        "title_de", 
        "material_position",
        "material_title", 
        "purpose", 
        "duration_minutes"
    ]].sort_values(
        by=["skill_position", "material_position"]
    )

    lp_materials.to_csv(export_path + f"lp_materials_{lp_id}.csv", index=False)




    #%% check assessment 
    assessment = user_skill_history[(user_skill_history["skill_id"].isin(LP_SKILL_LIST)) & (user_skill_history["origin_validation"] == "SelfAssessment")]

    assessment["skill_id"] = pd.Categorical(assessment["skill_id"], categories=LP_SKILL_LIST, ordered=True)

    first_assessment = assessment.groupby(["user_id", "skill_id"]).first().dropna(subset="is_mastered").reset_index()

    plot_df = first_assessment.groupby("skill_id")["is_mastered"].mean().reset_index()

    # %%
    p: p9.ggplot = p9.ggplot(plot_df) + p9.geom_bar(p9.aes(x="skill_id", y="is_mastered"), stat="identity") + p9.ylim([0, 1]) + p9.theme(
        axis_title_y=p9.element_blank(),
        axis_text_y=p9.element_blank(),
        axis_ticks_major_y=p9.element_blank()
    ) + p9.coord_flip() 
    p.save(filename=export_path + f"lp_assessments_{lp_id}.pdf")

    #%% check dependencies 
    lp_dependencies = dependencies[dependencies["prerequisite_skill_id"].isin(LP_SKILL_LIST)]

    lp_dependencies.shape

    #%% 
    lp_dependencies_full = lp_dependencies.merge(
        dim_skill[["skill_id", "title_de"]],
        left_on="prerequisite_skill_id", 
        right_on="skill_id",
        how="left"
    ).rename(
        columns={
            "title_de": "prerequisite_title_de"
        }
    ).merge(
        dim_skill[["skill_id", "title_de"]],
        left_on="dependent_skill_id", 
        right_on="skill_id",
        how="left"
    ).rename(
        columns={
            "title_de": "dependency_title_de"
        }
    )

    lp_dependencies_full = lp_dependencies_full[[
        "prerequisite_skill_id", 
        "prerequisite_title_de",
        "dependency_title_de",
        "dependent_skill_id"
    ]]

    lp_dependencies_full.to_csv(export_path + f"lp_dependencies_{lp_id}.csv", index=False)
