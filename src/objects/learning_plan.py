import random 

from typing import List
from collections import deque
from copy import deepcopy

from ..time_helper import get_day_delta, get_mondays_between, get_sundays_between, get_time_intervals, round_in_base
from .learning_path import Material, LearningPath


class WeeklyWorkload:
    def __init__(self, start_date: str, end_date: str, theoretical_workload: float) -> None:
        # self.learning_relation_id: str
        self.start_date = start_date
        self.end_date = end_date
        self.materials: List[Material] = []
        self.theoretical_workload = theoretical_workload # this is the pure distribution of material duration over the days of the week
        self.target_workload: int = None # this is the current target workload for this week
        self.additional_materials: List[Material] = []
        self.is_finished: bool = False

    def __repr__(self) -> str:
        msg = "\nWEEKLY WORKLOAD"
        msg += f"\nWorkload week: {self.start_date} -> {self.end_date}\nMaterials:\n"
        msg += "\n".join([f"{material.title}: {material.duration}min, Done: {material.is_finished}" for material in self.materials])
        msg +="\n-------------" 
        if self.additional_materials:
            msg += f"\nAdditional workload:\n"
            msg += "\n".join([f"{material.title}: {material.duration}min, Done: {material.is_finished}" for material in self.additional_materials])
        msg += f"\n\nTotal: {self.target_workload}min (actual: {self.actual_workload}, theoretical: {round(self.theoretical_workload)}), finished: {self.finished_workload}min."
        msg += f"\n\n-> Progress: {self.progress_in_percent}%" 

        return msg
    
    @property
    def actual_workload(self) -> int:
        # this is the actual workload of the week, containing current materials to be done and finished materials
        return sum([material.duration for material in self.materials] + [material.duration for material in self.additional_materials])

    @property
    def finished_workload(self) -> int:
        return sum([material.duration for material in self.materials if material.is_finished] + [material.duration for material in self.additional_materials if material.is_finished])

    @property
    def progress_in_percent(self) -> int:
        # counts progress made in week (also additional materials, that have not been originally part of this workload)
        if self.target_workload != 0:
            # progress = round((self.finished_workload / self.target_workload) * 100) 
            progress = round((self.finished_workload / self.target_workload) * 100)
        else:
            progress = 100
        return progress

    @property
    def number_of_materials(self) -> int:
        return len(self.materials)

    @property
    def material_ids(self) -> List[str]:
        return [material.id for material in self.materials]

    def add_material(self, material: Material) -> None: 
        self.materials.append(material)

    def add_additional_material(self, material: Material) -> None:
        self.additional_materials.append(material)

    def get_material_by_id(self, material_id: str) -> Material:
        return next((material for material in self.materials if material.id == material_id), None)

    # DEPRECATE!
    # def update_target_workload(self) -> None:
    #     if not self.is_finished and self.actual_workload != 0:
    #         self.target_workload = self.actual_workload
    #     else:
    #         pass

    # def check_is_finished(self) -> None:
    #     if self.target_workload is not None and self.finished_workload >= self.target_workload:
    #         self.is_finished = True

    # def update(self) -> None:
    #     # we use this to update the target workload ONLY if the workload has not yet been finished!!!
    #     self.check_is_finished()
    #     self.update_target_workload()
        



class LearningPlan:
    def __init__(self, learning_path: LearningPath) -> None:
        self.start_date = None
        self.end_date = None # due_on
        self.learning_path = learning_path

        self.current_week_start = None
        self.past_weekly_workloads: List[WeeklyWorkload] = []
        self.weekly_workloads: List[WeeklyWorkload] = []
        self.current_date: str = None

        self.out_of_date: bool = False
        self.is_done: bool = False

        self._round: bool = True
        self._round_base = 5
        self._round_mode = "floor"

    @property
    def round_mode(self) -> None:
        return self._round_mode

    @round_mode.setter
    def round_mode(self, value) -> None:
        if value not in ("best", "ceil", "floor", "none"):
            raise ValueError("Wrong mode.")
        self._round_mode = value

    @property
    def round_base(self) -> None:
        return self._round_base

    @round_base.setter
    def round_base(self, value) -> None:
        if not isinstance(value, int):
            raise ValueError("Base needs to be an integer.")
        self._round_base = value

    @property
    def current_week_workload(self) -> WeeklyWorkload:
        if len(self.weekly_workloads) > 0:
            return self.weekly_workloads[0]
        else:
            return None

    @property
    def next_week_workload(self) -> WeeklyWorkload:
        if len(self.weekly_workloads) > 1:
            return self.weekly_workloads[1]
        else:
            return None

    @property
    def past_week_workload(self) -> WeeklyWorkload:
        if len(self.past_weekly_workloads) > 0:
            return self.past_weekly_workloads[-1]
        else:
            return None
    
    def initialize(self, start_date: str, end_date: str,) -> None:
        # set up the entire plan
        self.start_date = start_date
        self.end_date = end_date
        self.current_week_start = self.start_date
        self.current_date = self.start_date
        self.weekly_workloads = self.calculate_weekly_workload(
            start_date=self.start_date,
            end_date=self.end_date,
            materials=self.learning_path.get_unfinished_and_unskipped_materials()
        )
        

    def _update_after_finished_material(self, material: Material) -> None:
        if material.id not in self.current_week_workload.material_ids:
            self.current_week_workload.add_additional_material(material)

            remaining_materials = self.learning_path.get_unfinished_and_unskipped_materials()
            current_week_workload = self._recalculate_current_week_workload(remaining_materials) 

            # filter materials added to current week
            remaining_materials = [material for material in remaining_materials if not material.id in self.current_week_workload.material_ids]

            # recalculate upcoming weeks
            upcoming_weekly_workloads = self.calculate_weekly_workload(
                start_date=self.next_week_workload.start_date, 
                end_date=self.weekly_workloads[-1].end_date,
                materials=remaining_materials
                )

            new_workloads = [current_week_workload]
            new_workloads.extend(upcoming_weekly_workloads)
            self.weekly_workloads = new_workloads
            
        # there is no else since we do not need to do anything else :)

    def _recalculate_current_week_workload(self, unfinished_materials: List[Material]) -> WeeklyWorkload:
        # keep finished materials and overwrite old workload
        workload = self.current_week_workload
        finished_materials: List[Material] = [material for material in workload.materials if material.is_finished]
        workload.materials = finished_materials 

        # add new materials to workload one by one if necessary (we count already finished materials here!)
        # here, TARGET workload needs to be exceeded as it is not overwritten again
        if len(unfinished_materials) > 0:
        
            unfinished_materials: deque = deque(unfinished_materials)
            while abs(workload.actual_workload + unfinished_materials[0].duration - workload.target_workload) <= abs(workload.actual_workload - workload.target_workload):
                current_material = unfinished_materials.popleft()
                workload.add_material(current_material)
                if len(unfinished_materials) == 0:
                    break

        return workload

    # def _recalculate_current_week_workload(self, unfinished_materials: List[Material]) -> WeeklyWorkload:
    #     # keep finished materials and overwrite old workload
    #     workload = self.current_week_workload
    #     finished_materials: List[Material] = [material for material in workload.materials if material.is_finished]
    #     workload.materials = finished_materials 

    #     # add new materials to workload one by one if necessary (we count already finished materials here!)
    #     if len(unfinished_materials) > 0:
        
    #         unfinished_materials: deque = deque(unfinished_materials)
    #         # while abs(workload.actual_workload + unfinished_materials[0].duration - workload.theoretical_workload) <= abs(workload.actual_workload - workload.theoretical_workload):
    #         while abs(round_in_base(workload.actual_workload + unfinished_materials[0].duration, base=self.round_base, mode=self.round_mode) - workload.theoretical_workload) <= abs(round_in_base(workload.actual_workload, base=self.round_base, mode=self.round_mode) - workload.theoretical_workload):
    #             current_material = unfinished_materials.popleft()
    #             workload.add_material(current_material)
    #             if len(unfinished_materials) == 0:
    #                 break
        
    #     workload.update()

    #     return workload

    def _update_after_assessment(self) -> None:
        # archive past weeks
        # move all additionally finished materials (from upcoming weeks) to the latest finished week (additional learning activities)
        # recalculate plan from start of the active week 
        pass
    
    # DEPRECATE
    # def update(self) -> None:
    #     if self.current_week_workload.end_date < self.current_date: # current week is over
    #         # ARCHIVE PAST LEARNING ACTIVITIES
    #         # move active workload (and more) to past if necessary 
    #         while self.weekly_workloads:
    #             # these are ordered
    #             if self.weekly_workloads[0].end_date < self.current_date:
    #                 workload = self.weekly_workloads.pop(0)
    #                 self.past_weekly_workloads.append(deepcopy(workload)) # deepcopy makes sure it is not touched anymore
    #             else: 
    #                 break
        
    #     if self.learning_path.progress_percent == 1:
    #         self.is_done = True # nothing to be done anymore
    #     elif self.current_date > self.end_date:
    #         self.out_of_date = True # nothing to be done anymore
    #     else: 
    #         # here, there must be workload left, so...
    #         # get current week start
    #         self.current_week_start = self.current_week_workload.start_date

    #         # recalculate the rest
    #         self.weekly_workloads = self.calculate_weekly_workload(
    #             start_date=self.current_week_start,
    #             end_date=self.end_date
    #         )

    def assess_skills_by_id(self, skill_ids: List[str]) -> None:
        for skill_id in skill_ids:
            self.learning_path.assess_skill_by_id(skill_id=skill_id)

    def assess_random_skills(self, n: int) -> None:
        skill_ids = random.choices(self.learning_path.skill_ids, k=n)
        for skill_id in skill_ids:
            self.learning_path.assess_skill_by_id(skill_id=skill_id)

    def make_progress(self, number_of_materials: int) -> None:
        # finishes one material after the other
        count = 0
        for material in self.learning_path.materials:
            if not material.is_finished:
                self.make_progress_by_material_id(material.id)
                count += 1
            
            if count == number_of_materials:
                break

    def make_progress_by_material_id(self, material_id: str) -> None:
        # this is only for the simulation: if a material is finished, we need to mark it as finished.
        # Additionally, if the material is not part of the current week's workload, we need to add it to additional materials.
        material = self.learning_path.get_material_by_id(material_id=material_id)
        if not (material.is_finished or material.is_skipped):
            material.finish()
            self._update_after_finished_material(material=material)
        else:
            print(f"Material {material.id}: {material.title} has already been finished/skipped.")

    def set_new_date(self, date: str) -> None:
        if date < self.current_date:
            raise ValueError(f"Date needs to be after {self.current_date}.")

        if self.current_week_workload.end_date < date: # current week is over
            # ARCHIVE PAST LEARNING ACTIVITIES
            # move active workload (and more) to past if necessary 
            while self.weekly_workloads:
                # these are ordered
                if self.weekly_workloads[0].end_date < date:
                    workload = self.weekly_workloads.pop(0)
                    self.past_weekly_workloads.append(deepcopy(workload)) # deepcopy makes sure it is not touched anymore
                else: 
                    break
        
        if self.learning_path.progress_percent == 1:
            self.is_done = True # nothing to be done anymore
        elif self.current_date > self.end_date:
            self.out_of_date = True # nothing to be done anymore
        else: 
            # here, there must be workload left, so...
            # get current week start
            self.current_week_start = self.current_week_workload.start_date

            # recalculate the rest
            self.weekly_workloads = self.calculate_weekly_workload(
                start_date=self.current_week_start,
                end_date=self.end_date,
                materials=self.learning_path.get_unfinished_and_unskipped_materials()
            )

        self.current_date = date

    def reset_end_date(self, date: str) -> None:
        if date < self.current_date:
            raise ValueError(f"Please set date later than {self.current_date}")
        self.end_date = date

    def calculate_weeks(self, start_date: str, end_date: str) -> dict:
        week_starts = get_mondays_between(start_date, end_date)
        week_ends = get_sundays_between(start_date, end_date)

        if start_date not in week_starts:
            week_starts.insert(0, start_date)

        if end_date not in week_ends: 
            week_ends.append(end_date)

        time_intervals = get_time_intervals(week_starts, week_ends)

        result = [
            {
                "week_start_date": week_start_date,
                "week_end_date": week_end_date,
                "number_of_days": days
            }
            for week_start_date, week_end_date, days in zip(week_starts, week_ends, time_intervals)
        ]

        return result

    # def calculate_theoretical_weekly_workload(self, start_date, end_date, total_workload_in_minutes: int) -> dict:
    #     weeks = self.calculate_weeks(start_date=start_date, end_date=end_date)
    #     total_weekdays = sum([w["number_of_days"] for w in weeks])
    #     daily_workload = total_workload_in_minutes / total_weekdays

    #     for w in weeks:
    #         w["workload"] = daily_workload * w["number_of_days"]

    #     return weeks

    def calculate_weekly_workload(self, start_date: str, end_date: str, materials: List[Material]) -> List[WeeklyWorkload]:

        weeks = self.calculate_weeks(start_date=start_date, end_date=end_date)
        unfinished_materials = deque([material for material in materials if not (material.is_finished or material.is_skipped)])
        actual_workloads: List[WeeklyWorkload] = []

        for week in weeks:

            # setup weekly workload
            material_duration = sum([material.duration for material in unfinished_materials])
            remaining_days = get_day_delta(week["week_start_date"], end_date, include_end_date=True)
            week_days = get_day_delta(week["week_start_date"], week["week_end_date"], include_end_date=True)
            theoretical_workload = (material_duration / remaining_days) * week_days

            weekly_workload = WeeklyWorkload(
                start_date=week["week_start_date"],
                end_date=week["week_end_date"],
                theoretical_workload=theoretical_workload
            )

            if len(unfinished_materials) == 0:
                print(f"WARNING: Week {weekly_workload.start_date} could not be filled with materials.")
            else:

                cond = True # always add one material
                while cond:
                    current_material = unfinished_materials.popleft()
                    weekly_workload.add_material(current_material)

                    if len(unfinished_materials) == 0: # break if no further materials
                        break

                    # recalculate condition (with the NEXT material)
                    duration_plus_next = weekly_workload.actual_workload + unfinished_materials[0].duration
                    err11 = abs(round_in_base(duration_plus_next, self.round_base, "floor") - weekly_workload.theoretical_workload)
                    # err12 = duration_plus_next - round_in_base(duration_plus_next, self.round_base, "floor")
                    
                    err21 = abs(round_in_base(weekly_workload.actual_workload, self.round_base, "floor") - weekly_workload.theoretical_workload)
                    # err22 = weekly_workload.actual_workload - round_in_base(weekly_workload.actual_workload, self.round_base, "floor")

                    cond = (err11 <= err21) # TODO: include other errors and weighting somehow

                # TODO: do a back-tracking to remove materials again if they were unnecessarily added
                if len(weekly_workload.materials) > 0:
                    while abs(round_in_base(weekly_workload.actual_workload - weekly_workload.materials[-1].duration, self.round_base, "floor")) ==  abs(round_in_base(weekly_workload.actual_workload, self.round_base, "floor")):
                        last_material = weekly_workload.materials.pop()
                        unfinished_materials.insert(0, last_material)

                        if len(weekly_workload.materials) == 0: 
                            break

            # set target workload once filled
            weekly_workload.target_workload = round_in_base(weekly_workload.actual_workload, self.round_base, "floor")
            actual_workloads.append(weekly_workload)  
        
        # add the last remainder
        if len(unfinished_materials) > 0:
            for remaining_material in unfinished_materials:
                actual_workloads[-1].add_material(remaining_material)

        return actual_workloads



    # def calculate_weekly_workload(self, start_date: str, end_date: str, materials: List[Material]) -> List[WeeklyWorkload]:
    #     unfinished_materials = deque([material for material in materials if not (material.is_finished or material.is_skipped)])
    #     total_workload_in_minutes = sum([material.duration for material in unfinished_materials])
    #     theoretical_workloads = self.calculate_theoretical_weekly_workload(
    #         start_date=start_date, 
    #         end_date=end_date,
    #         total_workload_in_minutes=total_workload_in_minutes
    #     )
    #     # unfinished_materials = deque(self.learning_path.get_unfinished_and_unskipped_materials()) # this includes assessments

    #     actual_workloads: List[WeeklyWorkload] = []
    #     for tw in theoretical_workloads:
    #         weekly_workload = WeeklyWorkload(
    #             start_date=tw["week_start_date"],
    #             end_date=tw["week_end_date"],
    #             theoretical_workload=tw["workload"]
    #         )

    #         if len(unfinished_materials) == 0:
    #             print(f"WARNING: Week {weekly_workload.start_date} could not be filled with materials.")
    #         else:
    #             # always add at least one material
    #             current_material = unfinished_materials.popleft()
    #             weekly_workload.add_material(current_material)
                
    #             # if there are more materials left, add materials one by one until workload is full
    #             if len(unfinished_materials) > 0:
                    
    #                 # while abs(weekly_workload.actual_workload + unfinished_materials[0].duration - weekly_workload.theoretical_workload) <= abs(weekly_workload.actual_workload - weekly_workload.theoretical_workload):
    #                 while abs(round_in_base(weekly_workload.actual_workload + unfinished_materials[0].duration, base=self.round_base, mode=self.round_mode) - weekly_workload.theoretical_workload) <= abs(round_in_base(weekly_workload.actual_workload, base=self.round_base, mode=self.round_mode) - weekly_workload.theoretical_workload):
    #                     current_material = unfinished_materials.popleft()
    #                     weekly_workload.add_material(current_material)

    #                     if len(unfinished_materials) == 0:
    #                         break
            
    #         actual_workloads.append(weekly_workload)
        
    #     # add the last remainder
    #     if len(unfinished_materials) > 0:
    #         for remaining_material in unfinished_materials:
    #             actual_workloads[-1].add_material(remaining_material)

    #     # set target workloads and add correct rounding mode
    #     for workload in actual_workloads:
    #         workload._round_base = self._round_base
    #         workload._round_mode = self._round_mode
    #         workload.update()

    #     return actual_workloads

    def print_all_weeks(self) -> None:
        print("\nPREVIOUS WEEK(S)")
        for workload in self.past_weekly_workloads:
            print(workload)

        print("\nCURRENT WEEK")
        print(self.current_week_workload)

        print("\nNEXT WEEK(S)")
        for workload in self.weekly_workloads:
            print(workload)

    def print_current_week(self) -> None:
        print("\nCURRENT WEEK")
        print(self.current_week_workload)

    def print_past_week(self) -> None:
        print("\nPAST WEEK")
        print(self.past_week_workload)

    def print_next_week(self) -> None:
        print("\nNEXT WEEK")
        print(self.next_week_workload)

    def print_surrounding_weeks(self) -> None:
        self.print_past_week()
        self.print_current_week()
        self.print_next_week()

    def summary_msg(self) -> str:
        msg = "\n"
        msg += f"Current date: {self.current_date}\n"

        for workload in self.past_weekly_workloads + self.weekly_workloads:
            msg += f"\nWeek {workload.start_date}: {workload.finished_workload} / {workload.target_workload} (a:{workload.actual_workload}, t:{round(workload.theoretical_workload)}) = {workload.progress_in_percent}%"
        
        return msg

    def print_summary(self) -> None: 
        print(self.summary_msg())


class LearningIndicator:
    def __init__(self, learning_plan: LearningPlan) -> None:
        self.learning_plan = learning_plan
        self.total_buffer: float = 0.8
        self.weekly_buffer: float = 0.8

    @property
    def average_learning_time_per_day(self) -> None:
        return self._average_learning_time_per_day()

    def _average_learning_time_per_day(self) -> float:
        lp_duration = self.learning_plan.learning_path.duration
        total_learning_days = get_day_delta(
            self.learning_plan.start_date, 
            self.learning_plan.end_date, 
            include_end_date=False
        )
        return lp_duration / total_learning_days

    def check_relative_learning_path_progress(self) -> bool:
        past_learning_days = get_day_delta(
            self.learning_plan.start_date, 
            self.learning_plan.current_date, 
            include_end_date=False
        )
        optimal_progress_until_current_date = self.average_learning_time_per_day * past_learning_days
        actual_progress_until_current_date = self.learning_plan.learning_path.finished_duration
        return actual_progress_until_current_date >= self.total_buffer * optimal_progress_until_current_date

    def check_last_weeks_progress(self) -> bool:
        if self.learning_plan.past_week_workload is None:
            progress_indicator = None # if learning has not yet started, we need to display a different message
        else:
            progress_indicator = (self.learning_plan.past_week_workload.progress_in_percent >= self.weekly_buffer * 100) 
        return progress_indicator

    def get_message(self) -> None:
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

