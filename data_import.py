import logging

from dwh_importer.importer import SnowflakeConnector, DataImporter

def import_data():
    snowflake_connector = SnowflakeConnector()
    importer = DataImporter(snowflake_connector, "ANALYTICS", "ANALYTICS_CORE")

    query_dict = {
        # "role_skill": "select ROLE_ID, SKILL_ID, LEARN_ORDER from BRI_ROLE_SKILL;", 
        # "skill": "select SKILL_ID, TITLE_EN, TITLE_DE from DIM_SKILL;",
        # "role": "select ROLE_ID, TITLE_DE, TITLE_EN, OWNER_ORGANIZATION_ID from ANALYTICS.ANALYTICS_CORE.DIM_ROLE where OWNER_ORGANIZATION_ID <> '5561f987-7f3e-49bd-a99a-a1e7003fb37a';",
        # "skill_duration": "select s.SKILL_ID, l.language, sum(m.DURATION_MINUTES) as DURATION_MINUTES from DIM_MATERIAL m left join BRI_LESSON_MATERIAL lm on m.MATERIAL_ID = lm.MATERIAL_ID left join DIM_LESSON l on lm.LESSON_ID = l.LESSON_ID left join DIM_SKILL s on l.SKILL_ID = s.SKILL_ID where s.SKILL_ID IS NOT NULL AND s.IS_SKILL_ITEM = TRUE AND l.IS_DEFAULT = TRUE AND s.OWNER_ORGANIZATION_ID <> '5561f987-7f3e-49bd-a99a-a1e7003fb37a' group by s.SKILL_ID, l.LANGUAGE order by 1;",
        # "material": "select MATERIAL_ID, TITLE, PURPOSE, DURATION_MINUTES, EMPIRICAL_DURATION_MINUTES, LANGUAGE, OWNER_ORGANIZATION_ID from DIM_MATERIAL",
        "bri_lesson_material": "select LESSON_MATERIAL_ID, LESSON_ID, MATERIAL_ID, POSITION from BRI_LESSON_MATERIAL",
        # "lesson": "select LESSON_ID, PURPOSE, LANGUAGE, IS_DEFAULT, SKILL_ID from DIM_LESSON"
    }

    importer.import_to_csv(query_dict, path="data")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import_data()
