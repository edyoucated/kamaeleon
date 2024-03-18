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

# LEARNING_PATH_IDS = [
#     "0442ab59-49d8-4445-87d7-3b726ff7c16a", # Excel
#     # "771f05b7-dd3d-4100-b570-9fa4de2baf5c", # Effektives Lernen
#     "618b8110-8e44-469f-9d18-cc45415f150c", # Führen virtueller Teams
#     "6317e477-b69e-4ec6-80c5-bb43a0962717" # Stressmanagement
# ]

LP_ID = "0442ab59-49d8-4445-87d7-3b726ff7c16a"
LANGUAGE = "de"

#%%
excel_short = pd.read_excel("data/additional/Excel_kurz.xlsx")
filter_skill_ids = excel_short["skill_id"].unique()

# %%
single_lp = bri_lp_skill[bri_lp_skill["learning_path_id"] == LP_ID]
single_lp = single_lp.merge(
    dim_skill,
    on="skill_id",
    how="left"
)

single_lp = single_lp[single_lp["skill_id"].isin(filter_skill_ids)]

LP_SKILL_LIST = single_lp.sort_values(by="position")["skill_id"].to_list()


#%% 
assessment = user_skill_history[(user_skill_history["skill_id"].isin(LP_SKILL_LIST)) & (user_skill_history["origin_validation"] == "SelfAssessment")]

assessment["skill_id"] = pd.Categorical(assessment["skill_id"], categories=LP_SKILL_LIST, ordered=True)

first_assessment = assessment.groupby(["user_id", "skill_id"]).first().dropna(subset="is_mastered").reset_index()

plot_df = first_assessment.groupby("skill_id")["is_mastered"].mean().reset_index()

p: p9.ggplot = p9.ggplot(plot_df) + p9.geom_bar(p9.aes(x="skill_id", y="is_mastered"), stat="identity") + p9.ylim([0, 1]) + p9.theme(
    axis_title_y=p9.element_blank(),
    axis_text_y=p9.element_blank(),
    axis_ticks_major_y=p9.element_blank()
) + p9.coord_flip() 
p.save(filename="export/lp_stats/" + f"lp_assessments_{LP_ID}_short.pdf")
