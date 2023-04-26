import logging

from dwh_importer.importer import SnowflakeConnector, DataImporter

ORGANIZATION_IDS = [
    "a1460275-3c3e-44ee-b522-9dfb59efffb7", # EIF 
    "0c30cde3-7b25-4765-9db8-60696a8fb5a0", # KAMAELEON-A
    "adad2008-bbf3-40f5-b292-7920fd9bc188", # KAMAELEON-B 
]

ORGANIZATION_FILTER = ', '.join(f"'{w}'" for w in ORGANIZATION_IDS)


def import_data(schema: str, query_dict: dict):
    snowflake_connector = SnowflakeConnector()
    importer = DataImporter(snowflake_connector, "ANALYTICS", schema)
    importer.import_to_csv(query_dict, path="data")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    query_dict = {
        "bri_role_skill": f"select ROLE_ID, brs.SKILL_ID, LEARN_ORDER from BRI_ROLE_SKILL brs left join DIM_SKILL s on brs.SKILL_ID = s.SKILL_ID where s.OWNER_ORGANIZATION_ID in ({ORGANIZATION_FILTER});", 
        "skill": f"select SKILL_ID, TITLE_EN, TITLE_DE from DIM_SKILL where OWNER_ORGANIZATION_ID in ({ORGANIZATION_FILTER});",
        "learning_path": f"select LEARNING_PATH_ID, TITLE_DE, TITLE_EN, OWNER_ORGANIZATION_ID from DIM_LEARNING_PATH where OWNER_ORGANIZATION_ID in ({ORGANIZATION_FILTER});",
        "skill_duration": f"select s.SKILL_ID, l.language, sum(m.DURATION_MINUTES) as DURATION_MINUTES from DIM_MATERIAL m left join BRI_LESSON_MATERIAL lm on m.MATERIAL_ID = lm.MATERIAL_ID left join DIM_LESSON l on lm.LESSON_ID = l.LESSON_ID left join DIM_SKILL s on l.SKILL_ID = s.SKILL_ID where s.SKILL_ID IS NOT NULL AND s.IS_SKILL_ITEM = TRUE AND l.IS_DEFAULT = TRUE AND s.OWNER_ORGANIZATION_ID in ({ORGANIZATION_FILTER}) group by s.SKILL_ID, l.LANGUAGE order by 1;",
        "material": f"select MATERIAL_ID, TITLE, PURPOSE, DURATION_MINUTES, EMPIRICAL_DURATION_MINUTES, LANGUAGE from DIM_MATERIAL where OWNER_ORGANIZATION_ID in ({ORGANIZATION_FILTER});",
        "bri_lesson_material": f"select LESSON_MATERIAL_ID, LESSON_ID, blm.MATERIAL_ID, POSITION from BRI_LESSON_MATERIAL blm left join DIM_MATERIAL m on blm.MATERIAL_ID = m.MATERIAL_ID where m.OWNER_ORGANIZATION_ID in ({ORGANIZATION_FILTER});",
        "lesson": f"select LESSON_ID, PURPOSE, LANGUAGE, IS_DEFAULT, l.SKILL_ID from DIM_LESSON l left join DIM_SKILL s on l.SKILL_ID = s.SKILL_ID where s.OWNER_ORGANIZATION_ID in ({ORGANIZATION_FILTER});",

        "goal": f"select * from FCT_GOAL where ORGANIZATION_ID in ({ORGANIZATION_FILTER});",
        "goal_activity": f"select * from FCT_GOAL_ACTIVITY where NEW_ORGANIZATION_ID in ({ORGANIZATION_FILTER});",
        "periodic_workload": f"select pw.* from FCT_PERIODIC_WORKLOAD pw left join FCT_GOAL g on pw.GOAL_ID = g.GOAL_ID where g.ORGANIZATION_ID in ({ORGANIZATION_FILTER});",
        "periodic_workload_trigger": f"select pwt.* from FCT_PERIODIC_WORKLOAD_TRIGGER pwt left join FCT_GOAL g on pwt.GOAL_ID = g.GOAL_ID where g.ORGANIZATION_ID in ({ORGANIZATION_FILTER});",
        
        "dim_skill_skill_dependency": f"select dss.* from DIM_SKILL_SKILL_DEPENDENCY dss left join DIM_SKILL ds on dss.PREREQUISITE_SKILL_ID = ds.SKILL_ID where OWNER_ORGANIZATION_ID in ({ORGANIZATION_FILTER});",
        "membership": f"select USER_ID, ORGANIZATION_ID, REFERENCE_DATA_ATTRIBUTE_1, ROLE from DIM_MEMBERSHIP where ORGANIZATION_ID in ({ORGANIZATION_FILTER});",
        "learning_path_exam": f"select * from FCT_LEARNING_PATH_EXAM where CONTEXT_ORGANIZATION_ID in ({ORGANIZATION_FILTER});",
        "user_skill_history": f"select ush.* from FCT_USER_SKILL_HISTORY ush left join DIM_USER u on ush.USER_ID = u.USER_ID where ORGANIZATION_ID_FIRST_JOINED in ({ORGANIZATION_FILTER});",
        "learning_content_progress": f"select * from FCT_LEARNING_CONTENT_PROGRESS where CONTEXT_ORGANIZATION_ID in ({ORGANIZATION_FILTER});"
    }
    import_data(schema="ANALYTICS_CORE", query_dict=query_dict)

    query_dict = {
        "event": "select * from FCT_CUSTOM_EVENT where EVENT_NAME = 'learningGoalWidget_see';"
    }
    import_data(schema="ANALYTICS_WEB", query_dict=query_dict)
