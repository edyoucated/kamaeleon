# %% get questions (NEEDS TO BE DONE VIA MATERIALS :( )
question_tmp = bri_skill_question.merge(
    dim_question, 
    on="question_id", 
    how="left"
)
question_tmp = question_tmp[question_tmp["language"] == LANGUAGE][["skill_id", "skill_question_id", "title", "correct_answers", "incorrect_answers"]]

lp_questions = single_lp.merge(
    question_tmp,
    on="skill_id", 
    how="left"
)

lp_questions = lp_questions[[
    "position", 
    "skill_id", 
    "title_de", 
    "skill_question_id", 
    "title", 
    "correct_answers", 
    "incorrect_answers"
]]
