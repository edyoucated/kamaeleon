from .learning_plan import LearningPlan
from ..time_helper import get_day_delta


class LearningIndicator:
    def __init__(self, learning_plan: LearningPlan) -> None:
        self.learning_plan: LearningPlan = learning_plan
        self.total_buffer: float = 0.8 # "buffer" for the over all learning path progress
        self.weekly_buffer: float = 0.8 # "buffer" for last week's progress

    @property
    def average_learning_time_per_day(self) -> None:
        return self._average_learning_time_per_day()

    def _average_learning_time_per_day(self) -> float:
        # computes the average time that needs to be invested each day (from start date to end date) 
        # in order to finish the full learning path duration (sum of all material durations)
        lp_duration = self.learning_plan.learning_path.duration
        total_learning_days = get_day_delta(
            self.learning_plan.start_date, 
            self.learning_plan.end_date, 
            include_end_date=False
        )
        return lp_duration / total_learning_days

    def check_relative_learning_path_progress(self) -> bool:
        # checks whether the actual learning progress (learnt duration) until the current date is 
        # above the optimal progress until that date (weakened a little by a buffer)
        past_learning_days = get_day_delta(
            self.learning_plan.start_date, 
            self.learning_plan.current_date, 
            include_end_date=False
        )
        optimal_progress_until_current_date = self.average_learning_time_per_day * past_learning_days
        actual_progress_until_current_date = self.learning_plan.learning_path.finished_duration
        return actual_progress_until_current_date >= self.total_buffer * optimal_progress_until_current_date

    def check_last_weeks_progress(self) -> bool:
        # checks whether the last week's workload has been finished or not 
        # (multiplied by a little buffer, almost finished is fine, too :) )
        if self.learning_plan.past_week_workload is None:
            progress_indicator = None # if learning has not yet started, we need to display a different message
        else:
            progress_indicator = (self.learning_plan.past_week_workload.progress_in_percent >= self.weekly_buffer * 100) 
        return progress_indicator

    def get_message(self) -> None:
        # gets the motivational message depending on the relative learning path progress and last week's progress
        # real messages see specs 
        # There is one additional state (overdue) which is not treated here: The deadline was missed (see specs).
        rlpp = self.check_relative_learning_path_progress()
        lwp = self.check_last_weeks_progress()

        if lwp is None:
            msg = "Let's make progress on your learning goal!"
        else:
            if rlpp and lwp: 
                msg = "You're doing fantastic, keep up the great work!"
            elif rlpp and not lwp:
                msg = "Last week was not you're best, but you're on track. Be better than last week!"
            elif not rlpp and lwp:
                msg = "Last week you did great, but you're a little behind. Keep reaching your weekly goals."
            elif not rlpp and not lwp:
                msg = "If you continue like this, your learning goal is off track. You need to catch up!"
        return msg
    
    #### ONLY DISPLAYING OPTIONS FOR THE PROTOTYPE BELOW THIS LINE

    def display(self) -> str:
        msg = "\n==================================================\n"
        msg += "LEARNING INDICATOR\n"

        if self.learning_plan.out_of_date or self.learning_plan.is_done:
            # learning plan is over
            msg += self.summarize_msg()
        else:
            # show current learning plan
            if self.learning_plan.past_week_workload is not None:
                last_weeks_progress_in_percent = self.learning_plan.past_week_workload.progress_in_percent
            else: 
                last_weeks_progress_in_percent = "There is no last week."

            if self.learning_plan.next_week_workload is not None:
                # next_weeks_workload_in_minutes = self.learning_plan.next_week_workload.target_workload
                next_weeks_workload_in_minutes = self.learning_plan.next_week_workload.target_workload # this includes rounding
            else: 
                next_weeks_workload_in_minutes = "There is no next week."

            current_weeks_progress_in_minutes = self.learning_plan.current_week_workload.finished_workload
            # current_weeks_workload_in_minutes = self.learning_plan.current_week_workload.target_workload 
            current_weeks_workload_in_minutes = self.learning_plan.current_week_workload.target_workload # this includes rounding

            msg += f"Current week start: {self.learning_plan.current_week_start}\n"
            msg += f"Message: <{self.get_message()}>\n" 
            msg += f"\nPast week's progress: {last_weeks_progress_in_percent}%.\n"
            msg += f"Current week's progress: {current_weeks_progress_in_minutes}/{current_weeks_workload_in_minutes}min.\n"
            msg += f"Next week's workload: {next_weeks_workload_in_minutes}min.\n"

        msg += "\n==================================================\n"
        return msg
        
    def show(self) -> None:
        print(self.display())

    def summarize_msg(self) -> str:
        msg = ""
        for workload in self.learning_plan.past_weekly_workloads:
            msg += f"\nWeek {workload.start_date}: {workload.progress_in_percent}%"

        msg += "\n------------------------\n"
        if self.learning_plan.learning_path.progress_percent == 1:
            msg += "Learning goal reached!"
        elif self.learning_plan.current_date > self.learning_plan.end_date:
            msg += f"Learning goal missed: {self.learning_plan.learning_path.progress_percent}"
        
        return msg

    def summarize(self) -> None:
        print(self.summarize_msg())
