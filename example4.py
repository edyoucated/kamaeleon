#%% IMPORTS
from src.objects.learning_path import LearningPath
from src.objects.learning_plan import LearningPlan, LearningIndicator

import warnings
warnings.filterwarnings('ignore')


#%% IMPORT LEARNING PATH
learning_path_id = "81c7c803-68cc-4b9a-9b74-a9cc8a22a9b5" # Power BI
language = "en"

learning_path = LearningPath()
learning_path.initialize_from_id(id=learning_path_id, language=language)

learning_path.print_full_path()

#%% CREATE LEARNING PLAN AND INDICATOR
start_date = "2022-12-02"
end_date = "2023-02-02"

learning_plan = LearningPlan(learning_path=learning_path)
learning_plan.initialize(start_date=start_date, end_date=end_date)
learning_plan.print_summary()

learning_indicator = LearningIndicator(learning_plan=learning_plan)
learning_indicator.show()

#%% MAKE PROGRESS
learning_plan.make_progress(number_of_materials=6)
learning_plan.set_new_date("2022-12-05")
learning_plan.update()
learning_indicator.show()

#%% MAKE RANDOM ASSESSMENT AND RECALCULATE REMAINING PLAN
learning_plan.print_summary()
learning_plan.assess_random_skills(n=10)
learning_plan.update()
learning_plan.print_summary()

#%%
learning_plan.make_progress(number_of_materials=12)
learning_plan.set_new_date("2022-12-12")
learning_indicator.show()

# %%
learning_plan.print_summary()
