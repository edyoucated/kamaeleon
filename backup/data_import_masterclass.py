import logging

from dwh_importer.importer import SnowflakeConnector, DataImporter

ORGANIZATION_IDS = [
    "220247b7-e731-455b-8dfb-ababafe9d3b0",
    "ae812353-7238-4e54-9bcb-38a7e5642713",
    "a14cb623-a9b4-44c8-bf5f-267e275cc06f",
    "67669e3d-97fa-4049-8e30-cb84dd9491e0",
    "be998bcc-6006-4eec-89b8-29167601fdf7",
    "f1fd9ec6-befe-4768-9287-dac3544e25ee",
    "e8e40c59-ff46-4b82-a583-a2ea9d92570f"
]

ORGANIZATION_FILTER = ', '.join(f"'{w}'" for w in ORGANIZATION_IDS)


def import_data(schema: str, query_dict: dict):
    snowflake_connector = SnowflakeConnector(warehouse="")
    importer = DataImporter(snowflake_connector, "ANALYTICS", schema)
    importer.import_to_csv(query_dict, path="data")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    query_dict = {
        "dim_skill": f"select SKILL_ID, TITLE_EN, TITLE_DE, OWNER_ORGANIZATION_ID, TAXONOMY_LEVEL from DIM_SKILL where OWNER_ORGANIZATION_ID in ({ORGANIZATION_FILTER});",
        "dim_skill_skill": f"select SKILL_SKILL_ID, PARENT_SKILL_ID, CHILD_SKILL_ID, LEARN_ORDER from DIM_SKILL_SKILL;"
    }
    import_data(schema="ANALYTICS_CORE", query_dict=query_dict)
