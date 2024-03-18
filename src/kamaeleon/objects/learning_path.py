from typing import Tuple, List
from enum import Enum
import pandas as pd


class PurposeOrder(Enum):
    Guidance = 1
    Educational = 2
    Inspirational = 3
    Tip = 4
    Example = 5
    Exercise = 6
    Reference = 7

    def __str__(self):
        return self.name


class Material: 
    def __init__(
        self, 
        id: str, 
        title: str, 
        duration: int, 
        empirical_duration: int, 
        language: str, 
        purpose: str, 
        use_empirical_duration: bool=False
    ) -> None:
        self.id = id
        self.title = title
        self._duration = duration
        self._empirical_duration = empirical_duration
        self.language = language
        self.purpose = purpose
        self._use_empirical_duration: bool = use_empirical_duration
        
        self._is_finished: bool = False
        self.is_skipped: bool = False

    def __repr__(self) -> str:
        return f"<Material: {self.title}>"

    def finish(self) -> None:
        self.is_finished = True

    def skip(self) -> None:
        self.is_skipped = True

    @property
    def duration(self) -> int:
        if self._use_empirical_duration:
            d = self._empirical_duration
        else: 
            d = self._duration
        return d

    @property
    def is_finished(self) -> bool:
        return self._is_finished

    @is_finished.setter
    def is_finished(self, value) -> None:
        if not isinstance(value, bool):
            raise ValueError("Needs to be boolean.")
        self._is_finished = value


class Skill: 
    def __init__(self, id: str, title: str) -> None:
        self.id = id
        self.title = title
        self.materials: Tuple[Material] = () # ordered 
        self.is_mastered: bool = False

    def __repr__(self) -> str:
        return f"<Skill: {self.title}>"

    def assess_as_mastered(self) -> None:
        self.is_mastered = True

        # for the prototype, attached materials are "skipped"
        for material in self.materials:
            material.skip()


class LearningPath:

    def __init__(self) -> None:
        self.id = None
        self.title = None
        self.skills: Tuple[Skill] = () # ordered
        self.language = None
        self._use_empirical_duration = False

    def __repr__(self) -> str:
        return f"<Learning path: {self.title}>"

    @property
    def materials(self) -> List[Material]:
        return [material for skill in self.skills for material in skill.materials]

    @property
    def skill_ids(self) -> List[str]:
        return [skill.id for skill in self.skills]

    @property
    def duration(self) -> int:
        duration = sum([material.duration for skill in self.skills for material in skill.materials])
        return duration

    @property
    def remaining_duration(self) -> int:
        rd = sum([material.duration for material in self.materials if not (material.is_finished or material.is_skipped)])
        return rd

    @property
    def finished_duration(self) -> int:
        fd = sum([material.duration for material in self.materials if material.is_finished])
        return fd

    @property
    def progress_percent(self) -> float:
        finished_duration = sum([material.duration for material in self.materials if material.is_finished or material.is_skipped])
        return round(finished_duration/self.duration, 2)

    def initialize_from_id(self, id: str, language: str) -> None:
        # load role
        self.id = id
        if language not in ("de", "en"):
            raise ValueError("Wrong language.")
        else:
            self.language = language

        self._load_meta_data()
        self._load_skills()
        self._load_materials()
    
    def print_full_path(self) -> None:
        for skill in self.skills:
            print("\n---------------------")
            print(f"\n{skill.title}: {skill.id}")
            for material in skill.materials:
                print(f"{material.title}: {material.id} | {material.duration} > {material.purpose}")


    def _load_skills(self) -> None:
        role_skill = pd.read_csv("data/role_skill.csv")
        skill = pd.read_csv("data/skill.csv")
        role_skill = role_skill[role_skill["role_id"] == self.id]
        role_skill.sort_values("learn_order", inplace=True)
        role_skill = pd.merge(role_skill, skill, on="skill_id", how="left")

        skills_list = []
        for _, skill_row in role_skill.iterrows(): # this is ordered
            skill_dict = skill_row.to_dict()
            if self.language == "en":
                skill_title = skill_dict["title_en"]
            elif self.language == "de":
                skill_title = skill_dict["title_de"]

            skills_list.append(
                Skill(
                    id=skill_dict["skill_id"],
                    title=skill_title
                )
            )

        self.skills = tuple(skills_list)

    def _load_materials(self) -> None:
        if len(self.skills) == 0: 
            raise ValueError("Need to load skills first.")

        material = pd.read_csv("data/material.csv")
        lesson = pd.read_csv("data/lesson.csv")
        bri_lesson_material = pd.read_csv("data/bri_lesson_material.csv")

        # filter and merge
        lesson = lesson[(lesson["skill_id"].isin(self.skill_ids)) & (lesson["language"] == self.language)]
        lesson.drop(columns=["language", "purpose"], inplace=True)
        lesson = pd.merge(lesson, bri_lesson_material, on="lesson_id", how="left")
        lesson = pd.merge(lesson, material, on="material_id", how="left")

        # assemble 
        for skill in self.skills:
            skill_lessons = lesson[lesson["skill_id"] == skill.id]

            # order lessons by purpose 
            skill_lessons['purpose'] = pd.Categorical(skill_lessons['purpose'], [str(i) for i in PurposeOrder], ordered=True)
            skill_lessons.sort_values(['purpose', "position"], inplace=True, ascending=True)

            materials = []
            for _, l in skill_lessons.iterrows():
                lesson_dict = l.to_dict()

                edm = lesson_dict["empirical_duration_minutes"]
                if isinstance(edm, float) and pd.notnull(edm):
                    empirical_duration = int(lesson_dict["empirical_duration_minutes"])
                else:
                    empirical_duration = int(lesson_dict["duration_minutes"])

                materials.append(
                    Material(
                        id=lesson_dict["material_id"],
                        title=lesson_dict["title"],
                        duration=int(lesson_dict["duration_minutes"]),
                        empirical_duration=empirical_duration,
                        language=lesson_dict["language"],
                        purpose=lesson_dict["purpose"],
                        use_empirical_duration=self._use_empirical_duration
                    )
                )

            skill.materials = tuple(materials)
                
    def _load_meta_data(self) -> None:
        role = pd.read_csv("data/role.csv")
        role = role[role["role_id"] == self.id].to_dict("records")[0]

        if self.language == "en":
            self.title = role["title_en"]
        elif self.language == "de":
            self.title = role["title_de"]

    def get_unfinished_materials(self) -> List[Material]:
        return [material for material in self.materials if not material.is_finished]

    def get_unfinished_and_unskipped_materials(self) -> List[Material]: # this is for assessments
        return [material for material in self.materials if not material.is_finished and not material.is_skipped]

    def get_skill_by_id(self, skill_id: str) -> Skill:
        return next((skill for skill in self.skills if skill.id == skill_id), None)
    
    def assess_skill_by_id(self, skill_id: str) -> None:
        skill = self.get_skill_by_id(skill_id)
        skill.assess_as_mastered()

    def get_material_by_id(self, material_id: str) -> Material:
        return next((material for material in self.materials if material.id == material_id), None)

    def get_material_position_in_path_by_id(self, material_id: str) -> int:
        # returns the position of a material in a learning path for sorting
        return next(i for i, material in enumerate(self.materials) if material.id == material_id)




        