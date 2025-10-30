import os, sys
import pandas as pd
from typing import Dict
from config import DISTRICT_MAPPING_EXCEL_PATH



def convert_district_mappings_into_json(dataframe: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Converts all district mapping excel into json
    Args:
        dataframe
    Returns:
        dict containing districts & their coordinates
    """
    df["district"] = df["district"].str.strip().str.lower()

    df["alt_district_spelling"] = df["alt_district_spelling"].fillna("").str.lower()

    coord_map = {}
    for _, row in df.iterrows():
        names = [row["district"]]
        if row["alt_district_spelling"]:
            names += [n.strip() for n in row["alt_district_spelling"].split(",")]
        for name in names:
            coord_map[name.lower()] = {"latitude": row["y"], "longitude": row["x"]}

    return coord_map



df = pd.read_excel(DISTRICT_MAPPING_EXCEL_PATH)
coord_map = convert_district_mappings_into_json(df)

