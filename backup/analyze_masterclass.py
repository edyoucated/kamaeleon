#%% 
import pandas as pd
import numpy as np


dim_skill = pd.read_csv("data/masterclass/dim_skill.csv")
dim_skill_skill = pd.read_csv("data/masterclass/dim_skill_skill.csv")

# %%
dim_skill["title"] = np.where(
    pd.isna(dim_skill["title_en"]), dim_skill["title_de"],
    dim_skill["title_en"]
)

#%%
taxonomy = dim_skill[dim_skill["taxonomy_level"] == "Skill"][[
    "owner_organization_id", "skill_id", "title"
]].rename(
    columns={
        "title": "skill_title"
    }
).merge(
    dim_skill_skill[["parent_skill_id", "child_skill_id"]].rename(
        columns={
            "parent_skill_id": "skill_id",
            "child_skill_id": "chapter_id"
        }
    ), 
    on="skill_id",
    how="left"
).merge(
    dim_skill[dim_skill["taxonomy_level"] == "Chapter"][[
        "skill_id", "title"
    ]].rename(columns={
        "skill_id": "chapter_id",
        "title": "chapter_title"
    }
    ),
    on="chapter_id",
    how="left"
).merge(
    dim_skill_skill[["parent_skill_id", "child_skill_id"]].rename(
        columns={
            "parent_skill_id": "chapter_id",
            "child_skill_id": "atom_id"
        }
    ), 
    on="chapter_id",
    how="left"
).merge(
    dim_skill[dim_skill["taxonomy_level"] == "Atom"][[
        "skill_id", "title"
    ]].rename(columns={
        "skill_id": "atom_id",
        "title": "atom_title"
    }
    ),
    on="atom_id",
    how="left"
)

#%% 
organization_ids = taxonomy["owner_organization_id"].unique()

with pd.ExcelWriter("export/masterclass/masterclass_taxonomies_no_ids.xlsx") as writer:

    for org_id in organization_ids:
        df: pd.DataFrame = taxonomy[taxonomy["owner_organization_id"] == org_id][["skill_title", "chapter_title", "atom_title"]]
        df.to_excel(writer, sheet_name=org_id, index=False)




