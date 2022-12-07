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
# end_date = "2023-06-02"

learning_plan = LearningPlan(learning_path=learning_path)
learning_plan.initialize(start_date=start_date, end_date=end_date)
learning_plan.print_current_week()

#%% ADD LEARNING INDICATOR
learning_indicator = LearningIndicator(learning_plan=learning_plan)
learning_indicator.show()


#%% MAKE PROGRESS
learning_plan.make_progress(6)
learning_plan.print_current_week()
learning_indicator.show()


#%% SET NEW DATE AND RECALCULATE REMAINING PLAN
learning_plan.set_new_date("2022-12-05")
learning_plan.update()
learning_plan.print_surrounding_weeks()
learning_indicator.show()

#%% MAKE LITTLE PROGRESS
learning_plan.make_progress(1)
learning_plan.set_new_date("2022-12-12")
learning_plan.update()
learning_indicator.show()

# %% MAKE PROGRESS TO CATCH UP
learning_plan.current_week_workload.number_of_materials
learning_plan.make_progress(16)
learning_plan.set_new_date("2022-12-19")
learning_plan.update()
learning_indicator.show()

# %% MAKE PROGRESS
learning_plan.current_week_workload.number_of_materials
learning_plan.make_progress(13)
learning_plan.set_new_date("2022-12-26")
learning_plan.update()
learning_indicator.show()

#%% EARLY FINISH
learning_plan.make_progress(40)
learning_plan.set_new_date("2022-12-27")
learning_plan.update()
learning_indicator.show()


# %% MAKE PROGRESS
learning_plan.current_week_workload.number_of_materials
learning_plan.make_progress(11)
learning_plan.set_new_date("2023-01-02")
learning_plan.update()
learning_indicator.show()

#%% FINISH 1
learning_plan.set_new_date("2023-01-04")
learning_plan.update()
learning_indicator.show()

#%% FINISH 2
learning_plan.make_progress(5)
learning_plan.set_new_date("2023-01-04")
learning_plan.update()
learning_indicator.show()

