import random 

from typing import List
from collections import deque
from copy import deepcopy

from ..time_helper import get_day_delta, get_mondays_between, get_sundays_between, get_time_intervals, round_in_base
from .learning_path import Material, LearningPath
from .weekly_workload import WeeklyWorkload


class LearningPlan:
    def __init__(self, learning_path: LearningPath) -> None:
        self.start_date = None # the date where the learning deadline was set 
        self.end_date = None # due_on / the learning deadline
        self.learning_path = learning_path # the learning path related to the learning goal and deadline

        self.current_week_start = None # the start date of the current week 
        self.past_weekly_workloads: List[WeeklyWorkload] = [] # past workloads, archived and never touched once here
        self.weekly_workloads: List[WeeklyWorkload] = [] # the rest of the weekly workloads (in order)
        self.current_date: str = None

        self.out_of_date: bool = False # helper for prototype
        self.is_done: bool = False # helper for prototype

        # rounding options for displaying the weekly duration
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
        # set up the entire plan and calculate weekly workloads
        self.start_date = start_date
        self.end_date = end_date
        self.current_week_start = self.start_date
        self.current_date = self.start_date
        self.weekly_workloads = self.calculate_weekly_workload(
            start_date=self.start_date,
            end_date=self.end_date,
            materials=self.learning_path.get_unfinished_and_unskipped_materials()
        )

    def calculate_weekly_workload(self, start_date: str, end_date: str, materials: List[Material]) -> List[WeeklyWorkload]:
        # this is where the heavy work is done :)
        weeks = self.calculate_weeks(start_date=start_date, end_date=end_date) 
        unfinished_materials = deque([material for material in materials if not (material.is_finished or material.is_skipped)]) # all unfinished learning path materials (materials attached to skills assessed as mastered are skipped!)
        actual_workloads: List[WeeklyWorkload] = [] 


        # calculate the weekly workloads one after another (as they depend on each other)
        for week in weeks:
            
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
                # it sometimes happens that weeks cannot be filled (but only towards the deadline, when no materials are left)
                # this is no problem but expected
                print(f"WARNING: Week {weekly_workload.start_date} could not be filled with materials.")
            else:

                cond = True # always add one material to the workload 
                while cond:
                    current_material = unfinished_materials.popleft()
                    weekly_workload.add_material(current_material)

                    if len(unfinished_materials) == 0: # break if no further materials
                        break

                    # recalculate condition (including the NEXT material in the learning path)
                    # for now: ignore err12 and err22 and the related to-dos
                    duration_plus_next = weekly_workload.actual_workload + unfinished_materials[0].duration
                    err11 = abs(round_in_base(duration_plus_next, self.round_base, "floor") - weekly_workload.theoretical_workload)
                    # err12 = duration_plus_next - round_in_base(duration_plus_next, self.round_base, "floor")
                    
                    err21 = abs(round_in_base(weekly_workload.actual_workload, self.round_base, "floor") - weekly_workload.theoretical_workload)
                    # err22 = weekly_workload.actual_workload - round_in_base(weekly_workload.actual_workload, self.round_base, "floor")

                    cond = (err11 <= err21) # TODO: include other errors and weighting somehow

                # do a back-tracking to remove materials again if they were unnecessarily added (this is necessary due to rounding)
                if len(weekly_workload.materials) > 0:
                    while abs(round_in_base(weekly_workload.actual_workload - weekly_workload.materials[-1].duration, self.round_base, "floor")) ==  abs(round_in_base(weekly_workload.actual_workload, self.round_base, "floor")):
                        last_material = weekly_workload.materials.pop()
                        unfinished_materials.insert(0, last_material)

                        if len(weekly_workload.materials) == 0: 
                            break

            # set target workload once filled
            weekly_workload.target_workload = round_in_base(weekly_workload.actual_workload, self.round_base, "floor")
            actual_workloads.append(weekly_workload)  
        
        # add the last remainder (this should never happen)
        if len(unfinished_materials) > 0:
            for remaining_material in unfinished_materials:
                actual_workloads[-1].add_material(remaining_material)

        return actual_workloads

    def calculate_weeks(self, start_date: str, end_date: str) -> List[dict]:
        # gives a list of week start dates, end dates and the number of days between start and end date
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
    

    #### ONLY DISPLAYING OPTIONS AND HELPERS FOR THE PROTOTYPE BELOW THIS LINE

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

    # TODO: DEPRECATE? 
    def _update_after_assessment(self) -> None:
        # archive past weeks
        # move all additionally finished materials (from upcoming weeks) to the latest finished week (additional learning activities)
        # recalculate plan from start of the active week 
        pass

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
