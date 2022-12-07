#%% IMPORTS
from src.objects.learning_path import LearningPath
from src.objects.learning_plan import LearningPlan, LearningIndicator

import warnings
warnings.filterwarnings('ignore')


#%% IMPORT LEARNING PATH
learning_path_id = "9ffc6b57-f46d-4ca2-95e2-e1e90313717e" # Data Reporting
language = "en"

learning_path = LearningPath()
learning_path.initialize_from_id(id=learning_path_id, language=language)

learning_path.print_full_path()

#%% CREATE LEARNING PLAN
start_date = "2022-12-02"
end_date = "2023-01-02"

learning_plan = LearningPlan(learning_path=learning_path)
learning_plan.initialize(start_date=start_date, end_date=end_date)
learning_plan.print_current_week()

#%% ADD LEARNING INDICATOR
learning_indicator = LearningIndicator(learning_plan=learning_plan)
learning_indicator.show()


#%% MAKE PROGRESS
learning_plan.make_progress(number_of_materials=6)
learning_plan.print_current_week()
learning_plan.print_next_week()
learning_indicator.show()


#%% SET NEW DATE AND RECALCULATE REMAINING PLAN
learning_plan.set_new_date("2022-12-05")
learning_plan.update()
learning_plan.print_surrounding_weeks()
learning_indicator.show()

#%% MAKE ASSESSMENT AND RECALCULATE REMAINING PLAN
learning_plan.print_summary()
skill_ids = [
    "d5bdc306-e5f0-4d4f-96cb-d4a21ca05744", # Contrast
    "e6228405-cbed-4a28-9225-ad1dae7aa797", # De-cluttering
    "ecff39d7-7c9a-4827-b7a2-83aadb6958e5", # Choosing the right chart type
]
learning_plan.assess_skills_by_id(skill_ids=skill_ids)
learning_plan.update()
learning_plan.print_summary()
learning_indicator.show()

#%% FINISH QUICK
# learning_plan.make_progress(number_of_materials=50)
# learning_plan.update()
# learning_indicator.show()

#%% OR RESET DEADLINE (fix indicator!)
learning_plan.reset_end_date("2023-02-21")
learning_plan.update()
learning_plan.print_summary()
learning_indicator.show()
