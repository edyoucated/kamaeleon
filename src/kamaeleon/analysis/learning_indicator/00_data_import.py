# CANNOT BE USED WITHOUT ACCESS TO THE DWH & DWH_IMPORTER: USE THE PROVIDED RESEARCH DATA INSTEAD

import logging

from dwh_importer.importer import (
    SnowflakeConnector, 
    DataImporter
)

from kamaeleon.analysis.analysis_helper import ORGANIZATION_IDS_LEARNING_INDICATOR as ORGANIZATION_IDS


ORGANIZATION_ID_FILTER = ', '.join(f"'{w}'" for w in ORGANIZATION_IDS)

def import_data(schema: str, query_dict: dict):
    snowflake_connector = SnowflakeConnector(warehouse="")
    importer = DataImporter(snowflake_connector, "ANALYTICS", schema)
    importer.import_to_csv(query_dict, path="data/learning_indicator")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    query_dict = {
        "dim_personalized_learning_path" : f"select * from DIM_PERSONALIZED_LEARNING_PATH where CONTEXT_ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",
        "fct_user_skill_history": f"select ush.* from FCT_USER_SKILL_HISTORY ush left join DIM_USER u on ush.USER_ID = u.USER_ID where ORGANIZATION_ID_FIRST_JOINED in ({ORGANIZATION_ID_FILTER});",        
        "dim_membership": f"select USER_ID, ORGANIZATION_ID, REFERENCE_DATA_ATTRIBUTE_1, ROLE from DIM_MEMBERSHIP where ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",
        
        "dim_learning_path": f"select LEARNING_PATH_ID, TITLE_DE, TITLE_EN, OWNER_ORGANIZATION_ID, CONTENT, CONTENT_INFORMATION from DIM_LEARNING_PATH where OWNER_ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",
        "bri_learning_path_skill": f"select LEARNING_PATH_ID, brs.SKILL_ID, POSITION from BRI_LEARNING_PATH_SKILL brs left join DIM_SKILL s on brs.SKILL_ID = s.SKILL_ID where s.OWNER_ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});", 
        "dim_skill": f"select SKILL_ID, TITLE_EN, TITLE_DE from DIM_SKILL where OWNER_ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",

        "fct_skill_duration": f"select s.SKILL_ID, l.language, sum(m.DURATION_MINUTES) as DURATION_MINUTES from DIM_MATERIAL m left join BRI_LESSON_MATERIAL lm on m.MATERIAL_ID = lm.MATERIAL_ID left join DIM_LESSON l on lm.LESSON_ID = l.LESSON_ID left join DIM_SKILL s on l.SKILL_ID = s.SKILL_ID where s.SKILL_ID IS NOT NULL AND l.IS_DEFAULT = TRUE AND s.OWNER_ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER}) group by s.SKILL_ID, l.LANGUAGE order by 1;",
        "dim_material": f"select MATERIAL_ID, TITLE, PURPOSE, DURATION_MINUTES, EMPIRICAL_DURATION_MINUTES, LANGUAGE from DIM_MATERIAL where OWNER_ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",
        "bri_lesson_material": f"select LESSON_MATERIAL_ID, LESSON_ID, blm.MATERIAL_ID, POSITION from BRI_LESSON_MATERIAL blm left join DIM_MATERIAL m on blm.MATERIAL_ID = m.MATERIAL_ID where m.OWNER_ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",
        "dim_lesson": f"select LESSON_ID, PURPOSE, LANGUAGE, IS_DEFAULT, l.SKILL_ID from DIM_LESSON l left join DIM_SKILL s on l.SKILL_ID = s.SKILL_ID where s.OWNER_ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",

        "bri_skill_question": "SELECT * FROM BRI_SKILL_QUESTION",
        "bri_material_question": "SELECT * FROM BRI_MATERIAL_QUESTION",
        "dim_question": "SELECT * FROM DIM_QUESTION",

        "dim_skill_skill_dependency" : "SELECT * FROM DIM_SKILL_SKILL_DEPENDENCY;",

        "fct_learning_content_progress": f"select * from FCT_LEARNING_CONTENT_PROGRESS where CONTEXT_ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",
        "fct_learning_content_activity": f"select * from FCT_LEARNING_CONTENT_ACTIVITY where CONTEXT_ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",

        "fct_goal": f"select * from FCT_GOAL where ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",
        "fct_goal_activity": f"select * from FCT_GOAL_ACTIVITY where NEW_ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",
        "fct_periodic_workload": f"select pw.* from FCT_PERIODIC_WORKLOAD pw left join FCT_GOAL g on pw.GOAL_ID = g.GOAL_ID where g.ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",
        "fct_periodic_workload_trigger": f"select pwt.* from FCT_PERIODIC_WORKLOAD_TRIGGER pwt left join FCT_GOAL g on pwt.GOAL_ID = g.GOAL_ID where g.ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",
        
        "fct_learning_path_exam": f"select * from FCT_LEARNING_PATH_EXAM where CONTEXT_ORGANIZATION_ID in ({ORGANIZATION_ID_FILTER});",

    }
    import_data(schema="ANALYTICS_CORE", query_dict=query_dict)


    query_dict = {
        "fct_event": "select * from FCT_CUSTOM_EVENT where EVENT_NAME = 'learningGoalWidget_see';"
    }
    import_data(schema="ANALYTICS_WEB", query_dict=query_dict)
