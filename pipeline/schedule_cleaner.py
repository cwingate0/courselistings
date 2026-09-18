import re
import pandas as pd
import sqlite3
import os

async def clean_for_schedule(raw_file: str):
    raw_path = f"../database/{raw_file}"
    raw_data = pd.read_json(raw_path)
    raw_data["clean_course"] = raw_data["course"].str.extract(r"([A-Z]{2,}[0-9]{4})")

    cleaned_df = pd.DataFrame({
        "catalog_course": raw_data["clean_course"],
        "section_number": raw_data["section_number"],
        "term": raw_data["term"],
        "instructor": raw_data["instructor"].apply(
            lambda x: re.sub(r"( -(e-mail)?(,)?(homepage)?)", "", x).strip()
            if isinstance(x, str) else None
        ),
        "instructor_culpa": None,
        "class_start_time": raw_data["start_time"],
        "class_end_time": raw_data["end_time"],
        "class_room": raw_data["class_room"],
        "vergil_link": raw_data["vergil_link"],
        "class_days": raw_data["class_days"],
    })

    destpath = "../backend/cleaned_sections.sqlite3"
    if os.path.exists(destpath):
        os.remove(destpath)

    with sqlite3.connect(destpath) as conn:
        cleaned_df.to_sql(
            "api_schedulecourse",
            conn,
            if_exists="replace",
            index=False,
        )

    print(f"✓ Transitional DB written: {destpath}")
    return destpath


if __name__ == "__main__":
    import asyncio
    asyncio.run(clean_for_schedule("raws/20261raw.json"))
