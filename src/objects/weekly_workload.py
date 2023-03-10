from typing import List

from .learning_path import Material


class WeeklyWorkload:
    def __init__(
            self, 
        start_date: str, 
        end_date: str, 
        theoretical_workload: float) -> None:
        
        # self.learning_relation_id: str
        self.start_date = start_date # usually a Monday, can only be different in the starting week
        self.end_date = end_date
        self.materials: List[Material] = [] # the list of Material that should theoretically be learned in this week
        self.theoretical_workload = theoretical_workload # the average duration that should theoretically be learned
        self.target_workload: int = None # this is the current target workload for this week
        self.additional_materials: List[Material] = [] # the list of Material that has been learned but was not planned for this week
        self.is_finished: bool = False # flag whether the week is finished (only relevant for prototype)
    
    @property
    def actual_workload(self) -> int:
        # this is the actual workload of the week, containing current materials to be done and already finished materials 
        # (including materials that were not due this week -> additional_materials)
        return sum([material.duration for material in self.materials] + [material.duration for material in self.additional_materials])

    @property
    def finished_workload(self) -> int:
        return sum([material.duration for material in self.materials if material.is_finished] + [material.duration for material in self.additional_materials if material.is_finished])

    @property
    def progress_in_percent(self) -> int:
        # counts progress made in week (also additional materials, that have not been originally part of this workload)
        if self.target_workload != 0:
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
    

    #### ONLY DISPLAYING OPTIONS FOR THE PROTOTYPE BELOW THIS LINE
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
